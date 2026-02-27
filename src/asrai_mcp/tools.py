import asyncio
import contextvars
import json
import os
from eth_account import Account
from x402.clients.httpx import x402HttpxClient

BASE_URL = "https://x402.asrai.me"
X402_HEADERS = {"x-coinbase-402": "true", "x-payment-token": "usdc"}

# Per-connection state via ContextVar — works for both stdio (single-user)
# and SSE (multi-user) modes without any code changes to tools.
_current_account: contextvars.ContextVar = contextvars.ContextVar("current_account", default=None)
_connection_spend: contextvars.ContextVar = contextvars.ContextVar("connection_spend", default=0.0)


def _check_spend(amount: float):
    max_s = float(os.environ.get("ASRAI_MAX_SPEND", "2.0"))
    current = _connection_spend.get(0.0)
    new_total = current + amount
    _connection_spend.set(new_total)
    if new_total > max_s:
        raise ValueError(
            f"Session spend limit of ${max_s} USDC reached. "
            f"Set ASRAI_MAX_SPEND env var to increase."
        )


def _get_account():
    # SSE multi-user mode: account set per-connection by sse_server.py
    ctx_account = _current_account.get(None)
    if ctx_account:
        return ctx_account
    # Stdio mode (Claude Desktop / openclaw): read from env as before
    key = os.environ.get("PRIVATE_KEY")
    if not key:
        raise ValueError("PRIVATE_KEY environment variable is required")
    return Account.from_key(key)


async def _get(path: str) -> dict | list | str:
    _check_spend(0.001)
    async with x402HttpxClient(account=_get_account(), base_url=BASE_URL, timeout=30.0) as client:
        r = await client.get(path, headers=X402_HEADERS)
        raw = (await r.aread()).decode()
        try:
            return json.loads(raw)
        except Exception:
            return raw


async def _post(path: str, body: dict) -> dict | list | str:
    _check_spend(0.001)
    async with x402HttpxClient(account=_get_account(), base_url=BASE_URL, timeout=30.0) as client:
        r = await client.post(path, json=body, headers=X402_HEADERS)
        raw = (await r.aread()).decode()
        try:
            return json.loads(raw)
        except Exception:
            return raw


async def _gather(*paths: str) -> dict:
    # Sequential to avoid x402 parallel payment conflicts from same wallet
    results = {}
    for path in paths:
        try:
            results[path] = await _get(path)
        except Exception as e:
            results[path] = str(e)
    return results


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

async def market_overview() -> str:
    data = await _gather(
        "/api/trending/",
        "/api/gainers-losers/",
        "/api/rsi/",
        "/api/top-bottom/",
    )
    return json.dumps(data, indent=2)


async def technical_analysis(symbol: str, timeframe: str = "1D") -> str:
    s = symbol.lower().rstrip("usdt")
    data = await _gather(
        f"/api/signal/{s}usdt/{timeframe}",
        f"/api/alsat/{s}usdt/{timeframe}",
        f"/api/superalsat/{s}usdt",
        f"/api/psar/{s}usdt/{timeframe}",
        f"/api/macd-dema/{s}usdt/{timeframe}",
        f"/api/alphatrend/{s}usdt/{timeframe}",
        f"/api/td/{s}usdt/{timeframe}",
    )
    return json.dumps(data, indent=2)


async def sentiment() -> str:
    data = await _gather(
        "/api/cbbi/",
        "/api/cmc-sentiment/",
        "/api/cmcai/",
    )
    return json.dumps(data, indent=2)


async def forecast(symbol: str) -> str:
    s = symbol.lower().rstrip("usdt")
    data = await _get(f"/api/forecasting/{s}usdt")
    return json.dumps(data, indent=2)


async def screener(screener_type: str) -> str:
    valid = [
        "ichimoku-trend", "sar-coins", "macd-coins", "emacross",
        "techrating", "vwap", "volume", "highvolumelowcap",
        "bounce-dip", "galaxyscore", "socialdominance", "late-unlocked-coins",
        "ath", "rsi", "rsi-heatmap", "ao",
    ]
    if screener_type not in valid:
        return json.dumps({"error": f"Invalid screener. Choose from: {valid}"})
    data = await _get(f"/api/{screener_type}/")
    return json.dumps(data, indent=2)


async def smart_money(symbol: str, timeframe: str = "1D") -> str:
    s = symbol.lower().rstrip("usdt")
    data = await _gather(
        f"/api/smartmoney/{s}usdt/{timeframe}",
        f"/api/support-resistance/{s}usdt/{timeframe}",
    )
    return json.dumps(data, indent=2)


async def elliott_wave(symbol: str, timeframe: str = "1D") -> str:
    s = symbol.lower().rstrip("usdt")
    data = await _get(f"/api/ew/{s}usdt/{timeframe}")
    return json.dumps(data, indent=2)


async def ichimoku(symbol: str, timeframe: str = "1D") -> str:
    s = symbol.lower().rstrip("usdt")
    data = await _get(f"/api/ichimoku/{s}usdt/{timeframe}")
    return json.dumps(data, indent=2)


async def cashflow(mode: str, symbol: str = "") -> str:
    if mode == "market":
        data = await _get("/api/cashflow/market")
    elif mode == "coin" and symbol:
        data = await _get(f"/api/cashflow/coin/{symbol.lower()}")
    elif mode == "group" and symbol:
        data = await _get(f"/api/cashflow/group/{symbol.lower()}")
    else:
        return json.dumps({"error": "mode must be 'market', 'coin', or 'group'. coin/group require symbol."})
    return json.dumps(data, indent=2)


async def coin_info(symbol: str) -> str:
    s = symbol.lower()
    data = await _gather(f"/api/coinstats/{s}", f"/api/info/{s}", f"/api/price/{s}", f"/api/tags/{s}")
    return json.dumps(data, indent=2)


async def dexscreener(contract_address: str, chain: str = "") -> str:
    if chain:
        data = await _get(f"/api/dexscreener/{chain}/{contract_address}")
    else:
        data = await _get(f"/api/dexscreener/{contract_address}")
    return json.dumps(data, indent=2)


async def chain_tokens(chain: str, max_mcap: str) -> str:
    data = await _get(f"/api/chain/{chain}/{max_mcap}")
    return json.dumps(data, indent=2)


async def portfolio(symbol: str = "") -> str:
    path = f"/api/portfolio/{symbol.lower()}" if symbol else "/api/portfolio/"
    data = await _get(path)
    return json.dumps(data, indent=2)


async def channel_summary() -> str:
    data = await _get("/api/channel-summary/")
    return json.dumps(data, indent=2)


async def ask_ai(question: str) -> str:
    data = await _post("/ai", {"message": question})
    return json.dumps(data, indent=2)


from asrai_mcp.indicators_guide import indicator_guide  # noqa: F401
