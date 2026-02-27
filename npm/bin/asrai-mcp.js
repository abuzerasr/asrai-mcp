#!/usr/bin/env node
/**
 * asrai-mcp npm wrapper
 * Spawns the Python asrai-mcp package via uvx (preferred) or pip-installed command.
 *
 * Usage via npx:
 *   npx asrai-mcp          (uses PRIVATE_KEY env var)
 *
 * Usage in Claude Desktop config:
 *   { "command": "npx", "args": ["-y", "asrai-mcp"] }
 */

const { spawnSync } = require('child_process');

const args = process.argv.slice(2);

// Try uvx first — no pre-install needed, works if uv is installed
const uvx = spawnSync('uvx', ['asrai-mcp', ...args], {
  stdio: 'inherit',
  env: process.env,
});

if (uvx.status === 0) {
  process.exit(0);
}

// Fall back to pip-installed asrai-mcp command
const pip = spawnSync('asrai-mcp', args, {
  stdio: 'inherit',
  env: process.env,
});

if (pip.status !== null) {
  process.exit(pip.status);
}

// Neither worked — print helpful error
console.error(
  '\nError: asrai-mcp requires either:\n' +
  '  - uv installed: https://docs.astral.sh/uv/ (then it runs automatically)\n' +
  '  - OR: pip install asrai-mcp\n'
);
process.exit(1);
