import os
import sys
import uuid

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.types import AuthPattern, OAuthConfig
from scalekit.v1.connections.connections_pb2 import ConnectionType, CreateConnection, DeleteEnvironmentConnectionRequest, Flags
from scalekit.v1.tools.tools_pb2 import ScopedToolFilter

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")
USER_IDENTIFIER = os.getenv("USER_IDENTIFIER")


def main():
    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create provider ───────────────────────────────────────────────────────

    print("Creating custom OAuth provider for Custom Pylon MCP...")
    try:
        create_result = sc.actions._providers_client.create_custom_provider(
            display_name="Custom Pylon MCP",
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
            metadata={"tenant_id": str(uuid.uuid4())},
        )
    except Exception as e:
        print(f"Failed to create provider: {e}")
        sys.exit(1)

    provider = create_result[0].provider
    print(f"Provider created: identifier={provider.identifier}, name={provider.display_name}")

    # ── Create connection ─────────────────────────────────────────────────────

    print("\nCreating app connection for the provider...")
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

    print(f"\nAuthorization URL: {auth_response.link}")

    answer = input("\nOpen the URL in your browser and complete the OAuth flow. Done? (y): ").strip().lower()
    if answer != "y":
        print("Exiting — re-run once authorization is complete.")
        sys.exit(0)

    # ── List scoped tools ─────────────────────────────────────────────────────

    print("\nListing scoped tools for Pylon MCP...")
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

    print("\nExecuting tool: c-custompylonmcp_get_me...")
    try:
        response = sc.actions.execute_tool(
            tool_name="c-custompylonmcp_get_me",
            identifier=USER_IDENTIFIER,
            connection_name=connection_name,
            tool_input={},
        )
    except Exception as e:
        print(f"Failed to execute tool: {e}")
        sys.exit(1)

    print(f"Response: {response.data}")

    # ── Cleanup ───────────────────────────────────────────────────────────────

    answer = input("\nCleanup test provider and keep your environment clean? (y/n): ").strip().lower()
    if answer == "y":
        cleanup(sc, connected_account.id, connection.id, connection_name, provider.identifier)


def cleanup(sc, connected_account_id, connection_id, connection_name, provider_identifier):
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
        sc.actions._providers_client.delete_custom_provider(
            identifier=provider_identifier,
        )
        print("  Provider deleted.")
    except Exception as e:
        print(f"  Failed to delete provider: {e}")

    print("Cleanup complete.")


if __name__ == "__main__":
    main()
