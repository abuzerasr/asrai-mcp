/**
 * Asrai MCP SSE Server — multi-user mode for Docker / n8n deployments.
 *
 * Supports two MCP transports:
 *   SSE (legacy):           GET  /sse?key=0x<private_key>
 *   HTTP Streamable (new):  POST /mcp?key=0x<private_key>  (recommended)
 *
 * Each user connects with their own wallet private key in the URL.
 * Payments are signed per-connection from that wallet — no shared keys.
 *
 * Also exposes:
 *   POST /generate-wallet   → create a new EVM wallet (for Telegram bot / n8n)
 *   GET  /health            → health check for Docker
 *
 * Environment variables:
 *   ASRAI_HOST        Bind host (default: 0.0.0.0)
 *   ASRAI_PORT        Bind port (default: 8402)
 *   ASRAI_MAX_SPEND   Max USDC spend per session (default: 2.0)
 */

import express from "express";
import { randomBytes, randomUUID } from "node:crypto";
import { createRequire } from "node:module";
import { privateKeyToAccount } from "viem/accounts";

const { version } = createRequire(import.meta.url)("../package.json");
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { createServer } from "./server.js";
import { connectionStorage } from "./tools.js";

const app = express();
app.use(express.json());

// Track active SSE transports by session ID (for POST /messages routing)
// Stores { transport, key } so the key is available when POST /messages arrives
const sseTransports = {};

// Track active streamable HTTP transports by session ID
const streamableTransports = {};

// ── Key extraction helper ─────────────────────────────────────────────────────

function extractKey(req, res, endpoint) {
  const key = (req.query.key ?? process.env.PRIVATE_KEY ?? "").trim();
  if (!key) {
    res.status(401).send(`Missing wallet key. Connect with: ${endpoint}?key=0x<private_key>`);
    return null;
  }
  try {
    privateKeyToAccount(key); // validate format
    return key;
  } catch {
    res.status(400).send("Invalid private key format.");
    return null;
  }
}

// ── SSE (legacy) transport ────────────────────────────────────────────────────

app.get("/sse", async (req, res) => {
  const key = extractKey(req, res, "/sse");
  if (!key) return;

  const transport = new SSEServerTransport("/messages", res);
  sseTransports[transport.sessionId] = { transport, key };

  res.on("close", () => {
    delete sseTransports[transport.sessionId];
  });

  await connectionStorage.run({ key, spend: 0 }, async () => {
    const server = createServer();
    await server.connect(transport);
  });
});

app.post("/messages", async (req, res) => {
  const sessionId = req.query.sessionId;
  const session = sseTransports[sessionId];
  if (session) {
    await connectionStorage.run({ key: session.key, spend: 0 }, async () => {
      await session.transport.handlePostMessage(req, res);
    });
  } else {
    res.status(400).send("No active session found.");
  }
});

// ── HTTP Streamable transport (recommended) ───────────────────────────────────

// POST /mcp — initialize new session or handle existing session message
app.post("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"];

  if (sessionId) {
    // Existing session — route to stored transport
    const session = streamableTransports[sessionId];
    if (!session) return res.status(404).json({ jsonrpc: "2.0", error: { code: -32000, message: "Session not found" }, id: null });

    await connectionStorage.run({ key: session.key, spend: 0 }, async () => {
      await session.transport.handleRequest(req, res, req.body);
    });
  } else if (isInitializeRequest(req.body)) {
    // New session — extract and validate key
    const key = extractKey(req, res, "/mcp");
    if (!key) return;

    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (id) => {
        streamableTransports[id] = { transport, key };
      },
    });

    transport.onclose = () => {
      if (transport.sessionId) delete streamableTransports[transport.sessionId];
    };

    await connectionStorage.run({ key, spend: 0 }, async () => {
      const server = createServer();
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    });
  } else {
    res.status(400).json({ jsonrpc: "2.0", error: { code: -32000, message: "No valid session ID" }, id: null });
  }
});

// GET /mcp — SSE stream for server-initiated messages (existing sessions only)
app.get("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"];
  const session = streamableTransports[sessionId];
  if (!session) return res.status(400).send("Invalid or missing session ID");

  await connectionStorage.run({ key: session.key, spend: 0 }, async () => {
    await session.transport.handleRequest(req, res);
  });
});

// DELETE /mcp — session termination
app.delete("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"];
  const session = streamableTransports[sessionId];
  if (!session) return res.status(400).send("Invalid or missing session ID");

  await connectionStorage.run({ key: session.key, spend: 0 }, async () => {
    await session.transport.handleRequest(req, res, req.body);
  });
});

// ── Utility routes ────────────────────────────────────────────────────────────

app.post("/generate-wallet", (_req, res) => {
  const privateKey = "0x" + randomBytes(32).toString("hex");
  const account = privateKeyToAccount(privateKey);
  res.json({ address: account.address, private_key: privateKey });
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", server: "asrai-mcp", version });
});

// ── Start ─────────────────────────────────────────────────────────────────────

export function startSseServer() {
  const host = process.env.ASRAI_HOST ?? "0.0.0.0";
  const port = parseInt(process.env.ASRAI_PORT ?? "8402", 10);

  app.listen(port, host, () => {
    console.log(`Asrai MCP Server — http://${host}:${port}`);
    console.log(`  SSE (legacy):    /sse?key=0x<private_key>`);
    console.log(`  HTTP Streamable: /mcp?key=0x<private_key>  ← recommended`);
    console.log(`  Generate wallet: POST /generate-wallet`);
    console.log(`  Health:          /health`);
  });
}
