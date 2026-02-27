# asrai-mcp

Crypto market analysis tools for AI agents, powered by the Asrai API.
Pay-per-use via [x402](https://x402.org) — no subscriptions, no API keys.
Each API endpoint costs **$0.001 USDC** on Base mainnet ($0.002 for `ask_ai`).

## Install

Three options — pick one:

```bash
# Option 1 — npx (recommended, no install needed — requires Node.js)
npx -y asrai-mcp

# Option 2 — uvx (no install needed — requires uv)
uvx asrai-mcp

# Option 3 — pip (traditional)
pip install asrai-mcp
```

## Setup

**Step 1 — Set your wallet private key**

Either create a `.env` file:

| OS | File location |
|---|---|
| macOS / Linux | `~/.env` or `.env` in your project |
| Windows | `C:\Users\yourname\.env` |

```
PRIVATE_KEY=0x<your_private_key>
```

Or pass it inline in the config (see below).

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

**Option A — npx with key inline (recommended, no Python needed):**
```json
{
  "mcpServers": {
    "asrai": {
      "command": "npx",
      "args": ["-y", "asrai-mcp"],
      "env": { "PRIVATE_KEY": "0x<YOUR_PRIVATE_KEY>" }
    }
  }
}
```

**Option A2 — npx with .env file (key stored separately):**
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

**Option B — Remote HTTP Streamable (no local install at all):**
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

**Option C — pip install (classic):**
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

Same config blocks above — add to the MCP settings of your client.

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

## Docker (SSE / HTTP Streamable Server)

For server deployments — n8n, OpenWebUI, multi-user setups. Exposes an HTTP server instead of stdio.

### Quick start

```bash
docker run -d \
  -p 8402:8402 \
  --name asrai-mcp \
  asrai-mcp-server
```

### docker-compose (recommended for production)

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

Each user connects with their **own** private key in the URL — payments come from their own wallet automatically.

### Connect Claude Desktop to the server

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

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `PRIVATE_KEY` | — | Fallback key if none in URL |
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
- x402 info: [x402.org](https://x402.org)
