import os
import sys
import uuid

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.types import AuthField, AuthPattern, CreateCustomProviderRequest, DeleteCustomProviderRequest
from scalekit.v1.connections.connections_pb2 import ConnectionType, CreateConnection, DeleteEnvironmentConnectionRequest, Flags
from scalekit.v1.tools.tools_pb2 import ScopedToolFilter

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")
USER_IDENTIFIER = os.getenv("USER_IDENTIFIER")


def main():
    if not CONTEXT7_API_KEY:
        print("Missing environment variable: CONTEXT7_API_KEY. Check your .env file.")
        sys.exit(1)

    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create provider ───────────────────────────────────────────────────────

    print("Creating custom API_KEY provider for Custom Context7 MCP...")
    try:
        create_response = sc.actions.providers.create_custom_provider(
            CreateCustomProviderRequest(
                display_name="Custom Context7 MCP",
                description="Context7 integration via MCP",
                proxy_url="https://mcp.context7.com/mcp",
                proxy_enabled=True,
                auth_patterns=[
                    AuthPattern(
                        type="API_KEY",
                        display_name="API Key",
                        description="Authenticate with a Context7 API key.",
                        is_mcp=True,
                        fields=[
                            AuthField(
                                field_name="api_key",
                                label="API Key",
                                input_type="password",
                            )
                        ],
                        auth_header_key_override="CONTEXT7_API_KEY",
                    )
                ],
                metadata={"tenant_id": str(uuid.uuid4())},
            )
        )
    except Exception as e:
        print(f"Failed to create provider: {e}")
        sys.exit(1)

    provider = create_response.provider
    print(f"Provider created: identifier={provider.identifier}, name={provider.display_name}")

    # ── Create connection ─────────────────────────────────────────────────────

    print("\nCreating app connection for the provider...")
    try:
        conn_response = sc.connection.create_environment_connection(
            connection=CreateConnection(
                provider_key=provider.identifier,
                type=ConnectionType.API_KEY,
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
    # API_KEY auth does not use an authorization URL — credentials are supplied
    # directly here via static_auth. The field name must match the field_name
    # defined on the AuthField above ("api_key").

    print("\nCreating connected account with API key...")
    try:
        ca_response = sc.actions.create_connected_account(
            connection_name=connection_name,
            identifier=USER_IDENTIFIER,
            authorization_details={
                "static_auth": {
                    "api_key": CONTEXT7_API_KEY,
                }
            },
        )
    except Exception as e:
        print(f"Failed to create connected account: {e}")
        sys.exit(1)

    connected_account = ca_response.connected_account
    print(f"Connected account created: id={connected_account.id}, status={connected_account.status}")

    # ── List scoped tools ─────────────────────────────────────────────────────

    print("\nListing scoped tools for Custom Context7 MCP...")
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

    # ── Execute tool ──────────────────────────────────────────────────────────

    print("\nExecuting tool: c-customcontext7mcp_query-docs...")
    try:
        response = sc.actions.execute_tool(
            tool_name="c-customcontext7mcp_query-docs",
            identifier=USER_IDENTIFIER,
            connection_name=connection_name,
            tool_input={
                "libraryId": "/vercel/next.js",
                "query": "How do i setup server-side rendering?",
            },
        )
    except Exception as e:
        print(f"Failed to execute tool: {e}")
        sys.exit(1)

    print(f"Response: {response.data}")

    # ── Cleanup ───────────────────────────────────────────────────────────────

    answer = input("\nCleanup test provider and keep your environment clean? (y/n): ").strip().lower()
    if answer == "y":
        cleanup(sc, connection.id, connection_name, provider.identifier)


def cleanup(sc, connection_id, connection_name, provider_identifier):
    print("\nCleaning up...")

    print("  Deleting connected account...")
    try:
        sc.actions.delete_connected_account(
            connection_name=connection_name,
            identifier=USER_IDENTIFIER,
        )
        print("  Connected account deleted.")
    except Exception as e:
        print(f"  Failed to delete connected account: {e}")

    # For connection update/delete refer to: https://docs.scalekit.com/sdks/python/reference
    print("  Deleting app connection...")
    try:
        sc.connection.core_client.grpc_exec(
            sc.connection.connection_service.DeleteEnvironmentConnection.with_call,
            DeleteEnvironmentConnectionRequest(connection_id=connection_id),
        )
        print("  Connection deleted.")
    except Exception as e:
        print(f"  Failed to delete connection: {e}")

    print("  Deleting custom provider...")
    try:
        sc.actions.providers.delete_custom_provider(
            DeleteCustomProviderRequest(identifier=provider_identifier)
        )
        print("  Provider deleted.")
    except Exception as e:
        print(f"  Failed to delete provider: {e}")

    print("Cleanup complete.")


if __name__ == "__main__":
    main()
