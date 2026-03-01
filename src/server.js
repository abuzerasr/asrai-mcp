/**
 * Asrai MCP server — tool definitions and request handlers.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import * as tools from "./tools.js";
import { indicator_guide } from "./indicator_guide.js";

// ── Tool definitions ────────────────────────────────────────────────────────

const TOOLS = [
  {
    name: "market_overview",
    description:
      "Get current crypto market pulse: trending coins, gainers/losers, RSI extremes, top/bottom signals. " +
      "Use for general market questions like 'what's moving today' or 'give me a market brief'.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "technical_analysis",
    description:
      "Get full technical analysis for a specific coin: signal, ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend. " +
      "Use when asked about TA, buy/sell signals, or indicators for a coin.",
    inputSchema: {
      type: "object",
      properties: {
        symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH, SOL" },
        timeframe: { type: "string", enum: ["1D", "4H", "1W"], description: "Timeframe. Default: 1D" },
      },
      required: ["symbol"],
    },
  },
  {
    name: "sentiment",
    description:
      "Get market sentiment: CBBI (crypto bull/bear index), CMC sentiment, CMC AI insights. " +
      "Use for questions about market mood, fear/greed, or cycle position.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "forecast",
    description: "Get AI-powered 3-7 day price forecast for a coin: direction, confidence, price targets.",
    inputSchema: {
      type: "object",
      properties: { symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH" } },
      required: ["symbol"],
    },
  },
  {
    name: "screener",
    description:
      "Run a market screener to find coins matching specific criteria. " +
      "Types: ichimoku-trend, sar-coins, macd-coins, emacross, techrating, vwap, volume, " +
      "highvolumelowcap, bounce-dip, galaxyscore, socialdominance, late-unlocked-coins, ath, rsi, rsi-heatmap, ao.",
    inputSchema: {
      type: "object",
      properties: {
        screener_type: {
          type: "string",
          enum: [
            "ichimoku-trend", "sar-coins", "macd-coins", "emacross",
            "techrating", "vwap", "volume", "highvolumelowcap",
            "bounce-dip", "galaxyscore", "socialdominance", "late-unlocked-coins",
            "ath", "rsi", "rsi-heatmap", "ao",
          ],
          description: "Type of screener to run",
        },
      },
      required: ["screener_type"],
    },
  },
  {
    name: "smart_money",
    description:
      "Get Smart Money Concepts (SMC): order blocks, fair value gaps, liquidity zones, BOS/CHoCH, " +
      "plus support/resistance levels.",
    inputSchema: {
      type: "object",
      properties: {
        symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH" },
        timeframe: { type: "string", enum: ["1D", "4H", "1W"], description: "Default: 1D" },
      },
      required: ["symbol"],
    },
  },
  {
    name: "elliott_wave",
    description: "Get Elliott Wave analysis: current wave position, impulse/corrective structure, price targets.",
    inputSchema: {
      type: "object",
      properties: {
        symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH" },
        timeframe: { type: "string", enum: ["1D", "4H", "1W"], description: "Default: 1D" },
      },
      required: ["symbol"],
    },
  },
  {
    name: "ichimoku",
    description: "Get Ichimoku cloud analysis: cloud position, Tenkan/Kijun cross, kumo twist, trend bias for a coin.",
    inputSchema: {
      type: "object",
      properties: {
        symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH" },
        timeframe: { type: "string", enum: ["1D", "4H", "1W"], description: "Default: 1D" },
      },
      required: ["symbol"],
    },
  },
  {
    name: "cashflow",
    description:
      "Get capital flow data showing where money is moving. " +
      "Modes: 'market' (overall), 'coin' (single coin), 'group' (comma-separated coins).",
    inputSchema: {
      type: "object",
      properties: {
        mode: {
          type: "string",
          enum: ["market", "coin", "group"],
          description: "Scope of cashflow data",
        },
        symbol: {
          type: "string",
          description: "Coin symbol (required for coin/group modes)",
        },
      },
      required: ["mode"],
    },
  },
  {
    name: "coin_info",
    description: "Get detailed info for a coin: market cap, volume, supply, social stats, tokenomics.",
    inputSchema: {
      type: "object",
      properties: { symbol: { type: "string", description: "Coin symbol e.g. BTC, ETH, SOL" } },
      required: ["symbol"],
    },
  },
  {
    name: "dexscreener",
    description: "Get DEX trading data for a token: liquidity, volume, buys/sells, price change. Use contract_address alone for symbol search, or provide chain + contract_address for a specific token.",
    inputSchema: {
      type: "object",
      properties: {
        contract_address: { type: "string", description: "Token contract address or symbol" },
        chain: { type: "string", description: "Optional chain e.g. ethereum, bsc, base, solana" },
      },
      required: ["contract_address"],
    },
  },
  {
    name: "chain_tokens",
    description: "Get low-cap tokens on a specific blockchain filtered by max market cap.",
    inputSchema: {
      type: "object",
      properties: {
        chain: { type: "string", description: "Chain e.g. ethereum, bsc, base, solana, avax" },
        max_mcap: { type: "string", description: "Max market cap e.g. 10000000 (10M)" },
      },
      required: ["chain", "max_mcap"],
    },
  },
  {
    name: "portfolio",
    description: "Get portfolio analysis. Optionally filter by a specific coin.",
    inputSchema: {
      type: "object",
      properties: { symbol: { type: "string", description: "Optional coin symbol to filter" } },
      required: [],
    },
  },
  {
    name: "channel_summary",
    description: "Get a summary of latest crypto narratives and discussions from monitored channels.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "ask_ai",
    description:
      "Ask the Asrai AI analyst a freeform crypto question. Gets a full analytical response " +
      "covering market context, signals, and actionable insights.",
    inputSchema: {
      type: "object",
      properties: { question: { type: "string", description: "Your crypto market question" } },
      required: ["question"],
    },
  },
  {
    name: "indicator_guide",
    description:
      "Reference guide for Asrai-specific indicators. FREE — no payment. " +
      "WHEN TO CALL: only when you encounter an unfamiliar indicator name in tool output " +
      "(e.g. ALSAT, SuperALSAT, AlphaTrend, PMax, MavilimW). " +
      "Standard indicators (RSI, MACD, Ichimoku, Elliott Wave, BB) are well-known — skip them. " +
      "indicator='' or 'list' → compact 1-line summary of all. " +
      "indicator='ALSAT' → full detail. indicator='all' → everything (avoid unless needed).",
    inputSchema: {
      type: "object",
      properties: {
        indicator: {
          type: "string",
          description: "Indicator name e.g. 'ALSAT', 'SuperALSAT', 'PMax'. Empty = compact list.",
        },
      },
      required: [],
    },
  },
];

// ── Request handlers ─────────────────────────────────────────────────────────

async function handleTool(name, args) {
  const sym = args?.symbol ?? "";
  const tf  = args?.timeframe ?? "1D";

  try {
    switch (name) {
      case "market_overview":    return await tools.market_overview();
      case "technical_analysis": return await tools.technical_analysis(sym, tf);
      case "sentiment":          return await tools.sentiment();
      case "forecast":           return await tools.forecast(sym);
      case "screener":           return await tools.screener(args?.screener_type ?? "");
      case "smart_money":        return await tools.smart_money(sym, tf);
      case "elliott_wave":       return await tools.elliott_wave(sym, tf);
      case "ichimoku":           return await tools.ichimoku(sym, tf);
      case "cashflow":           return await tools.cashflow(args?.mode ?? "market", sym);
      case "coin_info":          return await tools.coin_info(sym);
      case "dexscreener":        return await tools.dexscreener(args?.contract_address ?? "", args?.chain ?? "");
      case "chain_tokens":       return await tools.chain_tokens(args?.chain ?? "", args?.max_mcap ?? "");
      case "portfolio":          return await tools.portfolio(sym);
      case "channel_summary":    return await tools.channel_summary();
      case "ask_ai":             return await tools.ask_ai(args?.question ?? "");
      case "indicator_guide":    return indicator_guide(args?.indicator ?? "");
      default:                   return JSON.stringify({ error: `Unknown tool: ${name}` });
    }
  } catch (err) {
    if (err.name === "TimeoutError" || err.message?.includes("timed out")) {
      return JSON.stringify({ error: "Request timed out. The API is slow right now — try again in a moment." });
    }
    return JSON.stringify({ error: String(err.message ?? err) });
  }
}

// ── Server factory — reused by both stdio and SSE modes ───────────────────────

export function createServer() {
  const server = new Server(
    { name: "asrai", version: "0.5.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const result = await handleTool(request.params.name, request.params.arguments ?? {});
    return { content: [{ type: "text", text: result }] };
  });

  return server;
}

// ── Stdio startup (Claude Desktop / npx) ─────────────────────────────────────

export async function startStdio() {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
