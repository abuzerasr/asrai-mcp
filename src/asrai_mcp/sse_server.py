"""
Asrai MCP Server — multi-user mode for n8n / server deployments.

Supports two MCP transports:
  - SSE (legacy):           /sse?key=0x<private_key>
  - HTTP Streamable (new):  /mcp?key=0x<private_key>

Each user connects with their own wallet private key in the URL.
The server passes the key to x402 payments per-connection, so every user
pays from their own wallet automatically. No subscriptions needed.

Stdio mode (Claude Desktop / openclaw) is completely unaffected — it uses
the separate `asrai-mcp` command with PRIVATE_KEY env var as before.

Environment variables:
    ASRAI_HOST        Bind host (default: 0.0.0.0)
    ASRAI_PORT        Bind port (default: 8402)
    ASRAI_MAX_SPEND   Max USDC spend per session (default: 2.0)
"""

import contextlib
import os
import secrets
from eth_account import Account
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

from asrai_mcp.server import app as mcp_app
from asrai_mcp.tools import _current_account, _connection_spend

# --- SSE (legacy) transport ---
sse_transport = SseServerTransport("/messages/")

# --- Streamable HTTP (new) transport ---
_streamable_manager = StreamableHTTPSessionManager(
    app=mcp_app,
    stateless=False,
    json_response=False,
)


async def handle_sse(request: Request):
    """Legacy SSE transport — kept for backward compatibility."""
    key = request.query_params.get("key", "").strip()

    if not key:
        key = os.environ.get("PRIVATE_KEY", "").strip()

    if not key:
        return Response(
            "Missing wallet key. Connect with: /sse?key=0x<private_key>",
            status_code=401,
        )

    try:
        account = Account.from_key(key)
    except Exception:
        return Response("Invalid private key format.", status_code=400)

    _current_account.set(account)
    _connection_spend.set(0.0)

    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_app.run(
            streams[0], streams[1], mcp_app.create_initialization_options()
        )


async def handle_streamable(request: Request):
    """HTTP Streamable transport — current MCP standard (recommended)."""
    # Only set account for new sessions (no session ID header yet)
    session_id = request.headers.get("mcp-session-id")

    if not session_id:
        key = request.query_params.get("key", "").strip()

        if not key:
            key = os.environ.get("PRIVATE_KEY", "").strip()

        if not key:
            return Response(
                "Missing wallet key. Connect with: /mcp?key=0x<private_key>",
                status_code=401,
            )

        try:
            account = Account.from_key(key)
        except Exception:
            return Response("Invalid private key format.", status_code=400)

        # Set context — inherited by the new session task
        _current_account.set(account)
        _connection_spend.set(0.0)

    await _streamable_manager.handle_request(
        request.scope, request.receive, request._send
    )


async def generate_wallet(request: Request):
    """Generate a new EVM wallet for a Telegram bot user.
    Called by n8n when a new user starts the bot.
    Returns: { address, private_key }
    """
    private_key = "0x" + secrets.token_hex(32)
    account = Account.from_key(private_key)
    return JSONResponse({
        "address": account.address,
        "private_key": private_key,
    })


async def health(request: Request):
    return JSONResponse({"status": "ok", "server": "asrai-mcp-sse", "version": "0.4.4"})


@contextlib.asynccontextmanager
async def lifespan(app):
    async with _streamable_manager.run():
        yield


starlette_app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/mcp", endpoint=handle_streamable, methods=["GET", "POST", "DELETE"]),
        Route("/generate-wallet", endpoint=generate_wallet, methods=["POST"]),
        Route("/health", endpoint=health),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
)


def main():
    import uvicorn
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=os.path.expanduser("~/.env"))
    load_dotenv()

    host = os.environ.get("ASRAI_HOST", "0.0.0.0")
    port = int(os.environ.get("ASRAI_PORT", "8402"))

    print(f"Asrai MCP SSE Server — http://{host}:{port}")
    print(f"SSE (legacy):          /sse?key=0x<private_key>")
    print(f"HTTP Streamable (new): /mcp?key=0x<private_key>")
    print(f"Health check:          http://{host}:{port}/health")

    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == "__main__":
    main()
