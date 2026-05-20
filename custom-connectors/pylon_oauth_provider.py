import os
import sys

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.types import AuthPattern, CreateCustomProviderRequest, OAuthConfig
from scalekit.v1.connections.connections_pb2 import ConnectionType, CreateConnection, Flags

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")

USER_IDENTIFIER = "<YOUR_USER_IDENTIFIER>"


def main():
    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create provider ───────────────────────────────────────────────────────

    print("Creating custom OAuth provider for Pylon MCP...")
    try:
        provider_response = sc.actions.providers.create_custom_provider(
            CreateCustomProviderRequest(
                display_name="Pylon MCP",
                description="Pylon integration via MCP",
                proxy_url="https://mcp.usepylon.com",
                proxy_enabled=True,
                auth_patterns=[
                    AuthPattern(
                        type="OAUTH",
                        display_name="OAuth 2.1",
                        description="Authenticate via browser OAuth.",
                        is_mcp=True,
                        oauth_config=OAuthConfig(),
                    )
                ],
            )
        )
    except Exception as e:
        print(f"Failed to create provider: {e}")
        sys.exit(1)

    provider = provider_response.provider
    print(f"Provider created: identifier={provider.identifier}, name={provider.display_name}")

    # ── Create connection ─────────────────────────────────────────────────────

    print("\nCreating environment connection for the provider...")
    try:
        conn_response = sc.connection.create_environment_connection(
            connection=CreateConnection(
                provider_key=provider.identifier,
                type=ConnectionType.OAUTH,
            ),
            flags=Flags(is_app=True),
        )
    except Exception as e:
        print(f"Failed to create connection: {e}")
        sys.exit(1)

    connection = conn_response[0].connection
    connection_name = connection.key_id
    print(f"Connection created: id={connection.id}, key={connection_name}")

    # ── Create connected account ──────────────────────────────────────────────

    print("\nCreating connected account for user...")
    try:
        ca_response = sc.actions.create_connected_account(
            connection_name=connection_name,
            identifier=USER_IDENTIFIER,
        )
    except Exception as e:
        print(f"Failed to create connected account: {e}")
        sys.exit(1)

    connected_account = ca_response.connected_account
    print(f"Connected account created: id={connected_account.id}, status={connected_account.status}")

    # ── Get authorization URL ─────────────────────────────────────────────────
    # Send this URL to the user. They must open it in a browser and complete the
    # OAuth flow before the connected account becomes active and tools are available.

    print("\nFetching authorization URL...")
    try:
        auth_response = sc.actions.get_authorization_link(
            connection_name=connection_name,
            identifier=USER_IDENTIFIER,
        )
    except Exception as e:
        print(f"Failed to fetch authorization URL: {e}")
        sys.exit(1)

    print(f"Authorization URL: {auth_response.link}")
    print("\nShare this URL with the user. Once they complete the OAuth flow, the connected")
    print("account status will change to ACTIVE and tools will become available.")

    # ── List scoped tools (after OAuth is complete) ───────────────────────────
    # Once the user has completed the OAuth flow, call list_scoped_tools to see
    # the tools available for this connection and user:
    #
    #   from scalekit.v1.tools.tools_pb2 import ScopedToolFilter
    #
    #   scoped_response, _ = sc.tools.list_scoped_tools(
    #       identifier=USER_IDENTIFIER,
    #       filter=ScopedToolFilter(connection_names=[connection_name]),
    #       page_size=100,
    #   )
    #   tool_names = [t.tool.definition["name"] for t in scoped_response.tools]
    #   print(f"Available tools: {tool_names}")


if __name__ == "__main__":
    main()
