# asrai-mcp

Crypto market analysis tools for AI agents, powered by the Asrai API.
Pay-per-use via [x402](https://x402.org) — no subscriptions, no API keys.
Each API endpoint costs **$0.001 USDC** on Base mainnet ($0.002 for `ask_ai`).

## Install

```bash
pip install asrai-mcp
```

## Setup

**Step 1 — Create a `.env` file** with your wallet private key:

| OS | File location |
|---|---|
| macOS / Linux | `~/.env` (i.e. `/Users/yourname/.env`) |
| Windows | `C:\Users\yourname\.env` |

File contents:
```
PRIVATE_KEY=0x<your_private_key>
```

> You need an Ethereum wallet funded with USDC on Base mainnet.

---

**Step 2 — Add to your AI client config:**

### Claude Desktop

Config file location:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Add this:
```json
{
  "mcpServers": {
    "asrai": {
      "command": "asrai-mcp"
    }
  }
}
```

### Cursor / Windsurf / any MCP client

Same config block above, add it to the MCP settings of your client.

---

**Step 3 — Restart your AI client** and ask:

> "What's the market sentiment right now?"

The agent picks the right tools automatically and pays via x402.

---

## Available Tools

| Tool | Endpoints called |
|---|---|
| `market_overview` | `/trending`, `/gainers-losers`, `/rsi`, `/top-bottom` |
| `technical_analysis` | `/signal`, `/alsat`, `/superalsat`, `/psar`, `/macd-dema`, `/alphatrend`, `/td` |
| `sentiment` | `/cbbi`, `/cmc-sentiment`, `/cmcai` |
| `forecast` | `/forecasting/{symbol}` |
| `screener` | `/ichimoku-trend`, `/sar-coins`, `/macd-coins`, `/emacross`, `/techrating`, `/vwap`, `/volume`, `/highvolumelowcap`, `/bounce-dip`, `/galaxyscore`, `/socialdominance`, `/late-unlocked-coins`, `/ath`, `/rsi`, `/rsi-heatmap`, `/ao` |
| `smart_money` | `/smartmoney`, `/support-resistance` |
| `elliott_wave` | `/ew/{symbol}` |
| `ichimoku` | `/ichimoku/{symbol}` |
| `cashflow` | `/cashflow/market`, `/cashflow/coin`, `/cashflow/group` |
| `coin_info` | `/coinstats`, `/info`, `/price`, `/tags` |
| `dexscreener` | `/dexscreener/{address}` |
| `chain_tokens` | `/chain/{chain}/{max_mcap}` |
| `portfolio` | `/portfolio` |
| `channel_summary` | `/channel-summary` |
| `ask_ai` | `/ai` ($0.0020) |

## Example Prompts

- "What's moving in crypto today?"
- "Give me full TA on ETH daily"
- "What's the Elliott Wave count for BTC?"
- "Show me smart money levels on SOL 4H"
- "Run the volume screener"
- "What's the market sentiment right now?"
- "Forecast BTC for the next week"

## Network

- Chain: **Base mainnet**
- Token: **USDC**
- Facilitator: `https://facilitator.payai.network`
