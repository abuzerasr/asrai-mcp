#!/usr/bin/env node
/**
 * asrai-mcp npm wrapper
 * Launches the Python asrai-mcp package via uvx (preferred) or pip-installed command.
 *
 * Usage via npx:
 *   npx -y asrai-mcp
 *
 * Usage in Claude Desktop config:
 *   { "command": "npx", "args": ["-y", "asrai-mcp"] }
 */

const { spawnSync } = require('child_process');
const os = require('os');

const args = process.argv.slice(2);
const isWindows = os.platform() === 'win32';

// All messages go to stderr — stdout must stay clean for MCP JSON-RPC protocol
function log(msg) {
  process.stderr.write(msg + '\n');
}

function checkCommand(cmd) {
  const check = spawnSync(
    isWindows ? 'where' : 'which',
    [cmd],
    { stdio: 'ignore' }
  );
  return check.status === 0;
}

// ─── Check what's available ───────────────────────────────────────────────────

const hasUvx = checkCommand('uvx');
const hasUv  = checkCommand('uv');
const hasPip = checkCommand('asrai-mcp');

// ─── Nothing available ────────────────────────────────────────────────────────

if (!hasUvx && !hasUv && !hasPip) {
  log('');
  log('asrai-mcp: Python is required but not found.');
  log('');
  log('Quick fix — install uv (Python package manager):');
  if (isWindows) {
    log('  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"');
  } else {
    log('  curl -LsSf https://astral.sh/uv/install.sh | sh');
  }
  log('  Then re-run: npx -y asrai-mcp');
  log('');
  log('Alternative — install via pip:');
  log('  pip install asrai-mcp');
  log('');
  process.exit(1);
}

// ─── Warn if no PRIVATE_KEY set (stdio mode only) ─────────────────────────────

if (!process.env.PRIVATE_KEY && args.length === 0) {
  log('[asrai-mcp] Warning: PRIVATE_KEY env var not set — x402 payments will fail.');
  log('[asrai-mcp] Set it in your Claude Desktop config or .env file.');
  log('[asrai-mcp] See: https://github.com/asrai-ai/asrai-mcp');
  log('');
}

// ─── Try uvx ──────────────────────────────────────────────────────────────────

if (hasUvx || hasUv) {
  log('[asrai-mcp] Starting via uvx (downloads latest version if needed)...');

  const result = spawnSync('uvx', ['asrai-mcp', ...args], {
    stdio: ['inherit', 'inherit', 'inherit'],
    env: process.env,
  });

  if (result.error) {
    log('[asrai-mcp] uvx failed: ' + result.error.message);
  } else if (result.status === 0) {
    process.exit(0);
  } else {
    log('[asrai-mcp] uvx exited with code ' + result.status);
  }

  // If uvx failed but pip-installed version exists, fall through
  if (!hasPip) {
    log('');
    log('[asrai-mcp] Failed to start. Try:');
    log('  pip install asrai-mcp   # install manually');
    log('  PRIVATE_KEY=0x...       # set your wallet key');
    log('');
    process.exit(result.status ?? 1);
  }
}

// ─── Fall back to pip-installed asrai-mcp ────────────────────────────────────

if (hasPip) {
  log('[asrai-mcp] Starting (pip-installed)...');

  const result = spawnSync('asrai-mcp', args, {
    stdio: ['inherit', 'inherit', 'inherit'],
    env: process.env,
  });

  if (result.error) {
    log('[asrai-mcp] Error: ' + result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

process.exit(1);
