# asrai-mcp

Crypto market analysis tools for AI agents, powered by the Asrai API.
Pay-per-use via [x402](https://x402.org) — no subscriptions, no API keys.
Each tool call costs $0.05 USDC (or $0.10 for `ask_ai`) on Base mainnet.

## Install

```bash
pip install asrai-mcp
# or with uvx (no install needed):
uvx asrai-mcp
```

## Setup

You need an Ethereum wallet funded with USDC on Base mainnet.

### Claude Desktop

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "asrai": {
      "command": "uvx",
      "args": ["asrai-mcp"],
      "env": {
        "PRIVATE_KEY": "0x<your_private_key>"
      }
    }
  }
}
```

### Any other MCP client

```bash
PRIVATE_KEY=0x<your_key> asrai-mcp
```

## Available Tools

| Tool | Description | Cost |
|---|---|---|
| `market_overview` | Trending, gainers/losers, RSI, top/bottom signals | $0.20 |
| `technical_analysis` | ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend for a coin | $0.30 |
| `sentiment` | CBBI, CMC sentiment, CMC AI insights | $0.15 |
| `forecast` | 3-7 day AI price forecast for a coin | $0.05 |
| `screener` | Run screeners: ichimoku-trend, sar-coins, macd-coins, volume, etc. | $0.05 |
| `smart_money` | SMC analysis: order blocks, FVGs, liquidity zones | $0.10 |
| `elliott_wave` | Elliott Wave analysis and targets | $0.05 |
| `ichimoku` | Ichimoku cloud analysis | $0.05 |
| `cashflow` | Capital flow: market-wide, per coin, or group | $0.05 |
| `coin_info` | Market cap, supply, social stats for a coin | $0.10 |
| `dexscreener` | DEX data by contract address | $0.05 |
| `channel_summary` | Latest crypto narratives from monitored channels | $0.05 |
| `ask_ai` | Freeform question to the Asrai AI analyst | $0.10 |

## Usage Examples

Once installed, just ask your AI agent naturally:

- "What's moving in crypto today?"
- "Give me full TA on ETH daily"
- "What's the Elliott Wave count for BTC?"
- "Show me smart money levels on SOL 4H"
- "Run the volume screener"
- "What's the market sentiment right now?"
- "Forecast BTC for the next week"

The agent picks the right tools automatically and pays via x402.

## Network

- Chain: **Base mainnet**
- Token: **USDC**
- Facilitator: `https://facilitator.payai.network`
