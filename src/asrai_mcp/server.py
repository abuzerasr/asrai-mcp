import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asrai_mcp.tools as tools

app = Server("asrai")

TOOLS = [
    Tool(
        name="market_overview",
        description=(
            "Get current crypto market pulse: trending coins, gainers/losers, RSI extremes, "
            "top/bottom signals. Use for general market questions like 'what's moving today' "
            "or 'give me a market brief'."
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="technical_analysis",
        description=(
            "Get full technical analysis for a specific coin: signal, ALSAT, SuperALSAT, "
            "PSAR, MACD-DEMA, AlphaTrend. Use when asked about TA, buy/sell signals, "
            "or indicators for a coin."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH, SOL"},
                "timeframe": {
                    "type": "string",
                    "enum": ["1D", "4H", "1W"],
                    "description": "Timeframe. Default: 1D",
                },
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="sentiment",
        description=(
            "Get market sentiment data: CBBI (crypto bull/bear index), CMC sentiment, "
            "CMC AI insights. Use for questions about market mood, fear/greed, or cycle position."
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="forecast",
        description=(
            "Get AI-powered 3-7 day price forecast for a specific coin including direction, "
            "confidence, and price targets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="screener",
        description=(
            "Run a market screener to find coins matching specific criteria. "
            "Types: ichimoku-trend, sar-coins, macd-coins, emacross, techrating, "
            "vwap, volume, highvolumelowcap, bounce-dip, galaxyscore, socialdominance, late-unlocked-coins."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "screener_type": {
                    "type": "string",
                    "enum": [
                        "ichimoku-trend", "sar-coins", "macd-coins", "emacross",
                        "techrating", "vwap", "volume", "highvolumelowcap",
                        "bounce-dip", "galaxyscore", "socialdominance", "late-unlocked-coins",
                        "ath", "rsi", "rsi-heatmap", "ao",
                    ],
                    "description": "Type of screener to run",
                },
            },
            "required": ["screener_type"],
        },
    ),
    Tool(
        name="smart_money",
        description=(
            "Get Smart Money Concepts (SMC) analysis: order blocks, fair value gaps (FVG), "
            "liquidity zones, BOS/CHoCH, plus support/resistance levels for a coin."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH"},
                "timeframe": {"type": "string", "enum": ["1D", "4H", "1W"], "description": "Default: 1D"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="elliott_wave",
        description=(
            "Get Elliott Wave analysis: current wave position, impulse/corrective structure, "
            "price targets for wave completion."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH"},
                "timeframe": {"type": "string", "enum": ["1D", "4H", "1W"], "description": "Default: 1D"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="ichimoku",
        description=(
            "Get Ichimoku cloud analysis: cloud position, Tenkan/Kijun cross, kumo twist, "
            "trend bias for a coin."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH"},
                "timeframe": {"type": "string", "enum": ["1D", "4H", "1W"], "description": "Default: 1D"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="cashflow",
        description=(
            "Get capital flow data showing where money is moving in the crypto market. "
            "Modes: 'market' (overall), 'coin' (single coin), 'group' (comma-separated coins)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["market", "coin", "group"],
                    "description": "Scope of cashflow data",
                },
                "symbol": {
                    "type": "string",
                    "description": "Coin symbol (required for mode=coin) or comma-separated symbols (for mode=group)",
                },
            },
            "required": ["mode"],
        },
    ),
    Tool(
        name="coin_info",
        description=(
            "Get detailed info and stats for a specific coin: market cap, volume, circulating supply, "
            "social stats, tokenomics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Coin symbol e.g. BTC, ETH, SOL"},
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="dexscreener",
        description=(
            "Get DEX trading data for a token: liquidity, volume, buys/sells, price change. "
            "Use contract_address alone for symbol search, or provide chain + contract_address for a specific token."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "contract_address": {"type": "string", "description": "Token contract address or symbol"},
                "chain": {"type": "string", "description": "Optional chain name e.g. ethereum, bsc, base, solana"},
            },
            "required": ["contract_address"],
        },
    ),
    Tool(
        name="chain_tokens",
        description=(
            "Get tokens on a specific blockchain filtered by max market cap. "
            "Use to find low-cap gems on a specific chain."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "chain": {"type": "string", "description": "Chain name e.g. ethereum, bsc, base, solana, avax"},
                "max_mcap": {"type": "string", "description": "Max market cap filter e.g. 10000000 (10M)"},
            },
            "required": ["chain", "max_mcap"],
        },
    ),
    Tool(
        name="portfolio",
        description=(
            "Get portfolio analysis. Optionally filter by a specific coin symbol."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Optional coin symbol to filter portfolio"},
            },
            "required": [],
        },
    ),
    Tool(
        name="channel_summary",
        description=(
            "Get a summary of latest crypto narratives, news and discussions from monitored channels."
        ),
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="ask_ai",
        description=(
            "Ask the Asrai AI analyst a freeform crypto question. Gets a full analytical response "
            "covering market context, signals, and actionable insights. Use for complex questions "
            "that require synthesis across multiple data points."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Your crypto market question"},
            },
            "required": ["question"],
        },
    ),
    Tool(
        name="indicator_guide",
        description=(
            "Reference guide for Asrai-specific indicators. FREE — no payment. "
            "WHEN TO CALL: only when you encounter an unfamiliar indicator name in tool output "
            "(e.g. ALSAT, SuperALSAT, AlphaTrend, PMax, MavilimW). "
            "DO NOT call automatically — only on demand. "
            "Standard indicators (RSI, MACD, Ichimoku, Elliott Wave, BB) are well-known, skip them. "
            "indicator='' or 'list' → compact 1-line summary of all indicators (~400 tokens). "
            "indicator='ALSAT' → full detail for that specific indicator (~500 tokens). "
            "indicator='all' → full guide for everything (~5800 tokens, avoid unless necessary)."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "description": (
                        "Indicator name to look up: 'ALSAT', 'SuperALSAT', 'AlphaTrend', 'PMax', 'PSAR', 'TD9', 'SMC', etc. "
                        "Empty or 'list' = compact summary of all. 'all' = full guide (expensive)."
                    ),
                },
            },
            "required": [],
        },
    ),
]


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    symbol = arguments.get("symbol", "")
    timeframe = arguments.get("timeframe", "1D")

    try:
        if name == "market_overview":
            result = await asyncio.wait_for(tools.market_overview(), timeout=55)
        elif name == "technical_analysis":
            result = await asyncio.wait_for(tools.technical_analysis(symbol, timeframe), timeout=55)
        elif name == "sentiment":
            result = await asyncio.wait_for(tools.sentiment(), timeout=55)
        elif name == "forecast":
            result = await asyncio.wait_for(tools.forecast(symbol), timeout=55)
        elif name == "screener":
            result = await asyncio.wait_for(tools.screener(arguments.get("screener_type", "")), timeout=55)
        elif name == "smart_money":
            result = await asyncio.wait_for(tools.smart_money(symbol, timeframe), timeout=55)
        elif name == "elliott_wave":
            result = await asyncio.wait_for(tools.elliott_wave(symbol, timeframe), timeout=55)
        elif name == "ichimoku":
            result = await asyncio.wait_for(tools.ichimoku(symbol, timeframe), timeout=55)
        elif name == "cashflow":
            result = await asyncio.wait_for(tools.cashflow(arguments.get("mode", "market"), symbol), timeout=55)
        elif name == "coin_info":
            result = await asyncio.wait_for(tools.coin_info(symbol), timeout=55)
        elif name == "dexscreener":
            result = await asyncio.wait_for(tools.dexscreener(arguments.get("contract_address", ""), arguments.get("chain", "")), timeout=55)
        elif name == "chain_tokens":
            result = await asyncio.wait_for(tools.chain_tokens(arguments.get("chain", ""), arguments.get("max_mcap", "")), timeout=55)
        elif name == "portfolio":
            result = await asyncio.wait_for(tools.portfolio(arguments.get("symbol", "")), timeout=55)
        elif name == "channel_summary":
            result = await asyncio.wait_for(tools.channel_summary(), timeout=55)
        elif name == "ask_ai":
            result = await asyncio.wait_for(tools.ask_ai(arguments.get("question", "")), timeout=55)
        elif name == "indicator_guide":
            result = await tools.indicator_guide(arguments.get("indicator", ""))
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})
    except asyncio.TimeoutError:
        result = json.dumps({"error": "Request timed out. The API is slow right now — try again in a moment."})

    return [TextContent(type="text", text=result)]


def main():
    from dotenv import load_dotenv
    import os
    # Try ~/.env first (home dir), then fall back to cwd
    load_dotenv(dotenv_path=os.path.expanduser("~/.env"))
    load_dotenv()  # also check cwd as fallback

    async def _run():
        async with stdio_server() as (r, w):
            await app.run(r, w, app.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
