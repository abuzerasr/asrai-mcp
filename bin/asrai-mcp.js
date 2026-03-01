#!/usr/bin/env node
/**
 * Asrai MCP server — pure Node.js, zero install required.
 * Usage: npx -y asrai-mcp
 */

import { config } from "dotenv";
import { homedir } from "os";
import { join } from "path";
import { startStdio } from "../src/server.js";

// Load ~/.env first, then cwd .env as fallback
config({ path: join(homedir(), ".env") });
config();

// Warn if no key set — one message, once
if (!process.env.PRIVATE_KEY) {
  process.stderr.write("[asrai-mcp] Warning: PRIVATE_KEY not set — x402 payments will fail.\n");
  process.stderr.write("[asrai-mcp] Set it in your Claude Desktop config or ~/.env file.\n");
  process.stderr.write("[asrai-mcp] See: https://github.com/abuzerasr/asrai-mcp\n");
}

startStdio().catch((err) => {
  process.stderr.write(`[asrai-mcp] Fatal: ${err.message}\n`);
  process.exit(1);
});
