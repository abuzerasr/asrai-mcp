/**
 * Asrai API calls via x402 payment protocol.
 * Each call costs $0.001 USDC from the user's wallet on Base mainnet.
 *
 * Supports two modes:
 *  - stdio (Claude Desktop): reads PRIVATE_KEY from env
 *  - SSE (Docker/n8n): key injected per-connection via AsyncLocalStorage
 */

import { AsyncLocalStorage } from "node:async_hooks";
import { wrapFetchWithPayment, x402Client } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const BASE_URL = "https://x402.asrai.me";
const X402_HEADERS = { "x-coinbase-402": "true", "x-payment-token": "usdc" };

// Per-connection state — works for both stdio and multi-user SSE
// In stdio mode: nothing set here, falls back to PRIVATE_KEY env var
// In SSE mode: each connection runs inside connectionStorage.run({ key, spend: 0 }, ...)
export const connectionStorage = new AsyncLocalStorage();

function getMaxSpend() {
  return parseFloat(process.env.ASRAI_MAX_SPEND ?? "2.0");
}

function checkSpend(amount) {
  const store = connectionStorage.getStore();
  if (store) {
    store.spend = (store.spend ?? 0) + amount;
    if (store.spend > getMaxSpend()) {
      throw new Error(
        `Session spend limit of $${getMaxSpend()} USDC reached. ` +
        `Set ASRAI_MAX_SPEND env var to increase.`
      );
    }
  }
}

function buildFetch() {
  // SSE mode: key from per-connection storage
  // stdio mode: key from env var
  const store = connectionStorage.getStore();
  const key = store?.key ?? process.env.PRIVATE_KEY;
  if (!key) throw new Error("PRIVATE_KEY environment variable is required");

  const signer = privateKeyToAccount(key);
  const client = new x402Client();
  registerExactEvmScheme(client, { signer });
  return wrapFetchWithPayment(fetch, client);
}

async function _get(path) {
  checkSpend(0.001);
  const fetchWithPayment = buildFetch();
  const res = await fetchWithPayment(`${BASE_URL}${path}`, {
    headers: X402_HEADERS,
    signal: AbortSignal.timeout(90_000),
  });
  const text = await res.text();
  try { return JSON.parse(text); } catch { return text; }
}

async function _post(path, body) {
  checkSpend(0.001);
  const fetchWithPayment = buildFetch();
  const res = await fetchWithPayment(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { ...X402_HEADERS, "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(90_000),
  });
  const text = await res.text();
  try { return JSON.parse(text); } catch { return text; }
}

async function _gather(...paths) {
  // Sequential — parallel x402 payments from same wallet can conflict
  const results = {};
  for (const path of paths) {
    try { results[path] = await _get(path); }
    catch (e) { results[path] = String(e); }
  }
  return results;
}

// ── Symbol normalisation ────────────────────────────────────────────────────

function sym(symbol) {
  return symbol.toLowerCase().replace(/usdt$/, "");
}

// ── Tool handlers ───────────────────────────────────────────────────────────

export async function market_overview() {
  return JSON.stringify(await _gather(
    "/api/trending/",
    "/api/gainers-losers/",
    "/api/rsi/",
    "/api/top-bottom/",
  ), null, 2);
}

export async function technical_analysis(symbol, timeframe = "1D") {
  const s = sym(symbol);
  return JSON.stringify(await _gather(
    `/api/signal/${s}usdt/${timeframe}`,
    `/api/alsat/${s}usdt/${timeframe}`,
    `/api/superalsat/${s}usdt`,
    `/api/psar/${s}usdt/${timeframe}`,
    `/api/macd-dema/${s}usdt/${timeframe}`,
    `/api/alphatrend/${s}usdt/${timeframe}`,
    `/api/td/${s}usdt/${timeframe}`,
  ), null, 2);
}

export async function sentiment() {
  return JSON.stringify(await _gather(
    "/api/cbbi/",
    "/api/cmc-sentiment/",
    "/api/cmcai/",
  ), null, 2);
}

export async function forecast(symbol) {
  return JSON.stringify(await _get(`/api/forecasting/${sym(symbol)}usdt`), null, 2);
}

export async function screener(screener_type) {
  const valid = [
    "ichimoku-trend", "sar-coins", "macd-coins", "emacross",
    "techrating", "vwap", "volume", "highvolumelowcap",
    "bounce-dip", "galaxyscore", "socialdominance", "late-unlocked-coins",
    "ath", "rsi", "rsi-heatmap", "ao",
  ];
  if (!valid.includes(screener_type)) {
    return JSON.stringify({ error: `Invalid screener. Choose from: ${valid.join(", ")}` });
  }
  return JSON.stringify(await _get(`/api/${screener_type}/`), null, 2);
}

export async function smart_money(symbol, timeframe = "1D") {
  const s = sym(symbol);
  return JSON.stringify(await _gather(
    `/api/smartmoney/${s}usdt/${timeframe}`,
    `/api/support-resistance/${s}usdt/${timeframe}`,
  ), null, 2);
}

export async function elliott_wave(symbol, timeframe = "1D") {
  return JSON.stringify(await _get(`/api/ew/${sym(symbol)}usdt/${timeframe}`), null, 2);
}

export async function ichimoku(symbol, timeframe = "1D") {
  return JSON.stringify(await _get(`/api/ichimoku/${sym(symbol)}usdt/${timeframe}`), null, 2);
}

export async function cashflow(mode, symbol = "") {
  if (mode === "market") {
    return JSON.stringify(await _get("/api/cashflow/market"), null, 2);
  }
  if ((mode === "coin" || mode === "group") && symbol) {
    return JSON.stringify(await _get(`/api/cashflow/${mode}/${symbol.toLowerCase()}`), null, 2);
  }
  return JSON.stringify({ error: "mode must be 'market', 'coin', or 'group'. coin/group require symbol." });
}

export async function coin_info(symbol) {
  const s = symbol.toLowerCase();
  return JSON.stringify(await _gather(
    `/api/coinstats/${s}`,
    `/api/info/${s}`,
    `/api/price/${s}`,
    `/api/tags/${s}`,
  ), null, 2);
}

export async function dexscreener(contract_address, chain = "") {
  const path = chain
    ? `/api/dexscreener/${chain}/${contract_address}`
    : `/api/dexscreener/${contract_address}`;
  return JSON.stringify(await _get(path), null, 2);
}

export async function chain_tokens(chain, max_mcap) {
  return JSON.stringify(await _get(`/api/chain/${chain}/${max_mcap}`), null, 2);
}

export async function portfolio(symbol = "") {
  const path = symbol ? `/api/portfolio/${symbol.toLowerCase()}` : "/api/portfolio/";
  return JSON.stringify(await _get(path), null, 2);
}

export async function channel_summary() {
  return JSON.stringify(await _get("/api/channel-summary/"), null, 2);
}

export async function ask_ai(question) {
  return JSON.stringify(await _post("/ai", { message: question }), null, 2);
}
