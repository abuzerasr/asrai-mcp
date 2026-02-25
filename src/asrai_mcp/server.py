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
]


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    symbol = arguments.get("symbol", "")
    timeframe = arguments.get("timeframe", "1D")

    if name == "market_overview":
        result = await tools.market_overview()
    elif name == "technical_analysis":
        result = await tools.technical_analysis(symbol, timeframe)
    elif name == "sentiment":
        result = await tools.sentiment()
    elif name == "forecast":
        result = await tools.forecast(symbol)
    elif name == "screener":
        result = await tools.screener(arguments.get("screener_type", ""))
    elif name == "smart_money":
        result = await tools.smart_money(symbol, timeframe)
    elif name == "elliott_wave":
        result = await tools.elliott_wave(symbol, timeframe)
    elif name == "ichimoku":
        result = await tools.ichimoku(symbol, timeframe)
    elif name == "cashflow":
        result = await tools.cashflow(arguments.get("mode", "market"), symbol)
    elif name == "coin_info":
        result = await tools.coin_info(symbol)
    elif name == "dexscreener":
        result = await tools.dexscreener(arguments.get("contract_address", ""), arguments.get("chain", ""))
    elif name == "chain_tokens":
        result = await tools.chain_tokens(arguments.get("chain", ""), arguments.get("max_mcap", ""))
    elif name == "portfolio":
        result = await tools.portfolio(arguments.get("symbol", ""))
    elif name == "channel_summary":
        result = await tools.channel_summary()
    elif name == "ask_ai":
        result = await tools.ask_ai(arguments.get("question", ""))
    else:
        result = json.dumps({"error": f"Unknown tool: {name}"})

    return [TextContent(type="text", text=result)]


def main():
    async def _run():
        async with stdio_server() as (r, w):
            await app.run(r, w, app.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
