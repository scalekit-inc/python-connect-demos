"""
Scalekit Agent Auth Quickstart — with embedded user-verify server
https://docs.scalekit.com/agent-auth/quickstart/

Usage:
  pip install scalekit-sdk-python python-dotenv
  python user_verification.py <connection_name> [--user_verify_mode b2b|b2c]
"""

import argparse
import os
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server, WSGIRequestHandler

import scalekit.client
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Config — reads from .env
# ---------------------------------------------------------------------------
CLIENT_ID     = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")
ENV_URL       = os.getenv("SCALEKIT_ENV_URL")

missing = [k for k, v in {
    "SCALEKIT_CLIENT_ID": CLIENT_ID,
    "SCALEKIT_CLIENT_SECRET": CLIENT_SECRET,
    "SCALEKIT_ENV_URL": ENV_URL,
}.items() if not v]
if missing:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

parser = argparse.ArgumentParser(description="Scalekit Agent Auth Quickstart")
parser.add_argument("identifier", help="User identifier (e.g. user@example.com)")
parser.add_argument("connection_name", help="Connection name (e.g. gmail)")
parser.add_argument("--user_verify_mode", choices=["b2b", "b2c"], default="b2c", help="User verification mode (default: b2c)")
args = parser.parse_args()

USER_IDENTIFIER = args.identifier
CONNECTION_NAME = args.connection_name
MODE = args.user_verify_mode
STATE = "abc"

VERIFY_PORT = 9000
VERIFY_URL  = f"http://localhost:{VERIFY_PORT}/verify"

# ---------------------------------------------------------------------------
# 1. Scalekit client
# ---------------------------------------------------------------------------
scalekit_client = scalekit.client.ScalekitClient(
    env_url=ENV_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)

# ---------------------------------------------------------------------------
# 2. Get or create connected account
# ---------------------------------------------------------------------------
response = scalekit_client.actions.get_or_create_connected_account(
    connection_name=CONNECTION_NAME, identifier=USER_IDENTIFIER,
)
connected_account = response.connected_account
print(f"Connected account: {connected_account.id}  status={connected_account.status}")


# ---------------------------------------------------------------------------
# Verify callback server (used in b2b mode)
# ---------------------------------------------------------------------------
class _SilentHandler(WSGIRequestHandler):
    def log_message(self, *args): pass


def wait_for_verify_callback():
    """Handle exactly one /verify request, call the verify API via SDK, redirect."""
    def wsgi_app(environ, start_response):
        params = parse_qs(environ.get("QUERY_STRING", ""))
        auth_request_id = params.get("auth_request_id", [""])[0]
        print(f"\n[verify] auth_request_id={auth_request_id}")

        response = scalekit_client.actions.verify_connected_account_user(
            auth_request_id=auth_request_id,
            identifier=USER_IDENTIFIER,
        )
        redirect_url = response.post_user_verify_redirect_url or ENV_URL
        print(f"Redirect user to: {response.post_user_verify_redirect_url}")

        start_response("302 Found", [("Location", redirect_url), ("Content-Length", "0")])
        return [b""]

    with make_server("localhost", VERIFY_PORT, wsgi_app, handler_class=_SilentHandler) as httpd:
        httpd.handle_request()


# ---------------------------------------------------------------------------
# 3. Authorize if not ACTIVE
# ---------------------------------------------------------------------------
if connected_account.status != "ACTIVE":
    print(f"{CONNECTION_NAME} is not connected: {connected_account.status}")

    if MODE == "b2b":
        # B2B: get magic link with user_verify_url and state, then start local verify server
        link_response = scalekit_client.actions.get_authorization_link(
            connection_name=CONNECTION_NAME,
            identifier=USER_IDENTIFIER,
            user_verify_url=VERIFY_URL,
            state=STATE,
        )

        print(f"🔗 Click the link to authorize {CONNECTION_NAME}: {link_response.link}")
        print("⏳ Waiting for you to complete authorization...")

        wait_for_verify_callback()
        print("✅ Verified!")
    else:
        # B2C: no user verification step — just get the auth link and wait for manual confirmation
        link_response = scalekit_client.actions.get_authorization_link(
            connection_name=CONNECTION_NAME,
            identifier=USER_IDENTIFIER,
        )

        print(f"🔗 Click the link to authorize {CONNECTION_NAME}: {link_response.link}")
        input("⎆ Press Enter after completing authorization...")

print(f"✅ {CONNECTION_NAME} is ACTIVE")

# ---------------------------------------------------------------------------
# 4. Execute tool
# ---------------------------------------------------------------------------
print("\n--- Fetching last 5 read emails ---")
tool_response = scalekit_client.actions.execute_tool(
    tool_name="gmail_fetch_mails",
    identifier=USER_IDENTIFIER,
    tool_input={"query": "is:read", "max_results": 5},
)
print(tool_response)
