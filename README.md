# asrai-mcp

Crypto market analysis tools for AI agents, powered by the Asrai API.
Pay-per-use via [x402](https://x402.org) — no subscriptions, no API keys.
Each request costs **$0.001 USDC** on Base mainnet ($0.002 for `ask_ai`).

## Install

**Option 1 — uvx (recommended, no permanent install):**
```bash
# Install uv once (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run — downloads and starts automatically
uvx asrai-mcp
```

**Option 2 — pip:**
```bash
pip install asrai-mcp
asrai-mcp
```

**Option 3 — npx (launcher for uvx, requires both Node.js and uv):**
```bash
npx -y asrai-mcp
```

---

## Setup

**Step 1 — Get a wallet with USDC on Base mainnet**

You need an Ethereum wallet funded with USDC on Base mainnet.
Export your private key (starts with `0x`).

**Step 2 — Set your private key**

Either via `.env` file:

| OS | File location |
|---|---|
| macOS / Linux | `~/.env` or `.env` in project directory |
| Windows | `C:\Users\yourname\.env` |

```
PRIVATE_KEY=0x<your_private_key>
```

Or pass it directly in the Claude Desktop config (see below).

---

## Claude Desktop Config

Config file location:

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**Option A — uvx with key inline (recommended):**
```json
{
  "mcpServers": {
    "asrai": {
      "command": "uvx",
      "args": ["asrai-mcp"],
      "env": { "PRIVATE_KEY": "0x<YOUR_PRIVATE_KEY>" }
    }
  }
}
```

**Option B — uvx with .env file (key stored separately):**
```json
{
  "mcpServers": {
    "asrai": {
      "command": "uvx",
      "args": ["asrai-mcp"]
    }
  }
}
```

**Option C — Remote (no local install at all):**
```json
{
  "mcpServers": {
    "asrai": {
      "url": "https://mcp.asrai.me/mcp?key=0x<YOUR_PRIVATE_KEY>",
      "transport": "streamable-http"
    }
  }
}
```

**Option D — pip install:**
```json
{
  "mcpServers": {
    "asrai": {
      "command": "asrai-mcp",
      "env": { "PRIVATE_KEY": "0x<YOUR_PRIVATE_KEY>" }
    }
  }
}
```

### Cursor / Windsurf / any MCP client

Same config blocks above — paste into your MCP settings.

**Step 3 — Restart your AI client** and ask:

> "What's the market sentiment right now?"

The agent picks the right tools automatically and pays via x402.

---

## Available Tools

| Tool | What it does |
|---|---|
| `market_overview` | Trending coins, top gainers/losers, RSI extremes |
| `technical_analysis` | Full TA: ALSAT, SuperALSAT, PSAR, MACD-DEMA, AlphaTrend, TD |
| `sentiment` | CBBI, CMC sentiment, CMC AI insights |
| `forecast` | 3–7 day price forecast with confidence |
| `screener` | Find coins by 13+ criteria (Ichimoku, SAR, MACD, RSI, volume...) |
| `smart_money` | Order blocks, FVG, liquidity zones, support/resistance |
| `elliott_wave` | Elliott Wave count and targets |
| `ichimoku` | Ichimoku cloud analysis |
| `cashflow` | Capital flow by market / coin / group |
| `coin_info` | Market cap, volume, supply, social stats |
| `dexscreener` | DEX liquidity, volume, buys/sells |
| `chain_tokens` | Tokens on a chain filtered by market cap |
| `portfolio` | Portfolio analysis |
| `channel_summary` | Latest crypto news and narratives |
| `ask_ai` | Freeform question to Asrai AI analyst ($0.002) |
| `indicator_guide` | FREE — reference guide for Asrai indicators |

## Example Prompts

- "What's moving in crypto today?"
- "Give me full TA on ETH daily"
- "What's the Elliott Wave count for BTC?"
- "Show me smart money levels on SOL 4H"
- "Run the volume screener"
- "What's the market sentiment right now?"
- "Forecast BTC for the next week"

---

## Docker (Server Mode)

For server deployments — n8n, OpenWebUI, multi-user setups. Exposes HTTP instead of stdio.

### Quick start

```bash
docker run -d \
  -p 8402:8402 \
  --name asrai-mcp \
  asrai-mcp-server
```

### docker-compose

```yaml
services:
  asrai-mcp-server:
    build: .
    image: asrai-mcp-server
    container_name: asrai_mcp_server
    environment:
      - ASRAI_HOST=0.0.0.0
      - ASRAI_PORT=8402
      - ASRAI_MAX_SPEND=5.0   # max USDC per session
    ports:
      - "127.0.0.1:8402:8402"
    restart: unless-stopped
    networks:
      - nginx_network

networks:
  nginx_network:
    external: true
```

```bash
docker compose up -d
```

### Endpoints

| Endpoint | Transport | Auth |
|---|---|---|
| `/mcp?key=0x<key>` | HTTP Streamable (recommended) | key in URL |
| `/sse?key=0x<key>` | SSE (legacy) | key in URL |
| `/generate-wallet` | POST | none — generates a new wallet |
| `/health` | GET | none |

Each user connects with their **own** private key — payments come from their own wallet automatically.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `ASRAI_HOST` | `0.0.0.0` | Bind host |
| `ASRAI_PORT` | `8402` | Bind port |
| `ASRAI_MAX_SPEND` | `2.0` | Max USDC spend per session |

---

## Network

- Chain: **Base mainnet**
- Token: **USDC**
- Facilitator: `https://facilitator.payai.network`

## Links

- Website: [asrai.me](https://asrai.me)
- Agents page: [asrai.me/agents](https://asrai.me/agents)
- x402 protocol: [x402.org](https://x402.org)
