# asrai-mcp

Crypto market analysis MCP server for Claude Desktop — pay-per-use via x402 on Base mainnet.

**Zero install.** Just Node.js (already on your machine via npx).

## Quick start

**Step 1** — Add to your Claude Desktop config:

| OS | Config path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "asrai": {
      "command": "npx",
      "args": ["-y", "asrai-mcp"],
      "env": {
        "PRIVATE_KEY": "0x<your_base_wallet_private_key>"
      }
    }
  }
}
```

**Or** store your key in `~/.env` (loaded automatically — no `env` block needed in config):

```
PRIVATE_KEY=0x<your_base_wallet_private_key>
```

```json
{
  "mcpServers": {
    "asrai": {
      "command": "npx",
      "args": ["-y", "asrai-mcp"]
    }
  }
}
```

**Step 2** — Restart Claude Desktop. Done.

Each API call costs **$0.001 USDC** from your wallet on Base mainnet. Make sure your wallet has a small USDC balance (~$1–2 to start).

## What you get

15+ crypto analysis tools available directly in Claude:

| Tool | What it does | Cost |
|---|---|---|
| `market_overview` | Trending, gainers/losers, RSI extremes | $0.004 |
| `technical_analysis` | ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend | $0.007 |
| `sentiment` | CBBI, CMC sentiment, AI insights | $0.003 |
| `forecast` | AI 3-7 day price prediction | $0.001 |
| `screener` | Find coins by criteria | $0.001 |
| `smart_money` | Order blocks, FVGs, support/resistance | $0.002 |
| `elliott_wave` | Elliott Wave analysis | $0.001 |
| `ichimoku` | Ichimoku cloud | $0.001 |
| `cashflow` | Capital flow data | $0.001 |
| `coin_info` | Stats, info, price, tags | $0.004 |
| `dexscreener` | DEX trading data | $0.001 |
| `chain_tokens` | Low-cap tokens on chain | $0.001 |
| `portfolio` | Portfolio analysis | $0.001 |
| `channel_summary` | Latest crypto narratives | $0.001 |
| `ask_ai` | AI analyst freeform answer | $0.002 |
| `indicator_guide` | Asrai indicator reference | FREE |

## Spend limit

Default session cap: **$2.00 USDC**. To change:

```json
"env": {
  "PRIVATE_KEY": "0x...",
  "ASRAI_MAX_SPEND": "5.0"
}
```

## Links

- Homepage: https://asrai.me/agents
- GitHub: https://github.com/abuzerasr/asrai-mcp
