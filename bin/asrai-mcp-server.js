#!/usr/bin/env node
/**
 * Asrai MCP SSE Server — Docker / n8n mode.
 * Usage: npx asrai-mcp-server
 *        or via Docker (see docker-compose.yml)
 */

import { config } from "dotenv";
import { homedir } from "os";
import { join } from "path";
import { startSseServer } from "../src/sse-server.js";

config({ path: join(homedir(), ".env") });
config();

startSseServer();
