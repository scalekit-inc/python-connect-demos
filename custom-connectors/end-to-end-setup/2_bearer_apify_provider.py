import os
import sys
import uuid

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.types import AuthField, AuthPattern, CreateCustomProviderRequest
from scalekit.v1.connections.connections_pb2 import ConnectionType, CreateConnection, Flags
from scalekit.v1.tools.tools_pb2 import ScopedToolFilter

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
USER_IDENTIFIER = os.getenv("USER_IDENTIFIER")


def main():
    if not APIFY_API_TOKEN:
        print("Missing environment variable: APIFY_API_TOKEN. Check your .env file.")
        sys.exit(1)

    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create provider ───────────────────────────────────────────────────────

    print("Creating custom BEARER provider for Apify MCP...")
    try:
        provider_response = sc.actions.providers.create_custom_provider(
            CreateCustomProviderRequest(
                display_name="Apify MCP",
                description="Apify integration via MCP",
                proxy_url="https://mcp.apify.com",
                proxy_enabled=True,
                auth_patterns=[
                    AuthPattern(
                        type="BEARER",
                        display_name="Bearer Token",
                        description="Authenticate with an Apify API token.",
                        is_mcp=True,
                        fields=[
                            AuthField(
                                field_name="token",
                                label="API Token",
                                input_type="password",
                            )
                        ],
                    )
                ],
                metadata={"tenant_id": str(uuid.uuid4())},
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
                type=ConnectionType.BEARER,
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
    # BEARER auth does not use an authorization URL — credentials are supplied
    # directly here via static_auth. The field name must match the field_name
    # defined on the AuthField above ("token").

    print("\nCreating connected account with bearer token...")
    try:
        ca_response = sc.actions.create_connected_account(
            connection_name=connection_name,
            identifier=USER_IDENTIFIER,
            authorization_details={
                "static_auth": {
                    "token": APIFY_API_TOKEN,
                }
            },
        )
    except Exception as e:
        print(f"Failed to create connected account: {e}")
        sys.exit(1)

    connected_account = ca_response.connected_account
    print(f"Connected account created: id={connected_account.id}, status={connected_account.status}")

    # ── List scoped tools ─────────────────────────────────────────────────────
    # Unlike OAuth, BEARER credentials are available immediately after account
    # creation — no browser flow needed, so tools are ready to query right away.

    print("\nListing scoped tools for Apify MCP...")
    try:
        scoped_response, _ = sc.tools.list_scoped_tools(
            identifier=USER_IDENTIFIER,
            filter=ScopedToolFilter(connection_names=[connection_name]),
            page_size=100,
        )
    except Exception as e:
        print(f"Failed to list scoped tools: {e}")
        sys.exit(1)

    if scoped_response and scoped_response.tools:
        tool_names = [t.tool.definition["name"] for t in scoped_response.tools]
        print(f"Tools ({len(tool_names)}):")
        for name in tool_names:
            print(f"  - {name}")
    else:
        print("No tools returned.")


if __name__ == "__main__":
    main()
