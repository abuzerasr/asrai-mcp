# asrai-mcp

Crypto market analysis tools for AI agents, powered by the Asrai API.
Pay-per-use via [x402](https://x402.org) — no subscriptions, no API keys.

> **Note:** This is the npx launcher for the [asrai-mcp Python package](https://pypi.org/project/asrai-mcp/).
> It requires [uv](https://docs.astral.sh/uv/) to be installed on your system.

## Quick Start

```bash
# Install uv (one time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run via npx
npx -y asrai-mcp
```

## Claude Desktop Config

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

You need an Ethereum wallet funded with USDC on Base mainnet.
Each request costs **$0.001 USDC**.

## Full Documentation

See the main package: [github.com/abuzerasr/asrai-mcp](https://github.com/abuzerasr/asrai-mcp)

## Links

- Website: [asrai.me](https://asrai.me)
- Agents page: [asrai.me/agents](https://asrai.me/agents)
- PyPI: [pypi.org/project/asrai-mcp](https://pypi.org/project/asrai-mcp/)
