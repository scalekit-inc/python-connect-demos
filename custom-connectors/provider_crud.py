import os
import sys

from dotenv import load_dotenv
from google.protobuf.json_format import MessageToDict, MessageToJson
from scalekit import ScalekitClient
from scalekit.actions.types import AuthPattern, OAuthConfig

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")


def main():
    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create ────────────────────────────────────────────────────────────────
    # The low-level _providers_client is used here because metadata is only
    # supported at that layer (not available via the high-level providers API).
    print("Creating custom OAuth provider...")
    try:
        create_result = sc.actions._providers_client.create_custom_provider(
            display_name="Example MCP",
            description="Example integration via MCP",
            proxy_url="https://mcp.example.com/mcp",
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
            metadata={"env": "dev", "team": "platform"},
        )
    except Exception as e:
        print(f"Failed to create provider: {e}")
        sys.exit(1)

    provider_proto = create_result[0].provider
    print(f"Provider created: identifier={provider_proto.identifier}, name={provider_proto.display_name}")
    print(f"Provider (after create):\n{MessageToJson(provider_proto)}")

    # ── Read ──────────────────────────────────────────────────────────────────
    # Always GET before UPDATE to read current state, including metadata.
    print("\nFetching provider before update...")
    try:
        list_result = sc.actions._providers_client.list_providers(
            identifier=provider_proto.identifier,
        )
    except Exception as e:
        print(f"Failed to fetch provider: {e}")
        sys.exit(1)

    providers = list_result[0].providers
    fetched_proto = providers[0] if providers else provider_proto
    print(f"Provider (after GET):\n{MessageToJson(fetched_proto)}")

    # ── Update ────────────────────────────────────────────────────────────────
    # update_custom_provider is PUT-style, not PATCH — the server replaces the
    # entire provider with what you send. Always GET first, then echo back every
    # field you want to keep (display_name, proxy_url, auth_patterns, metadata,
    # etc.) alongside the fields you actually want to change. Omitting any field
    # silently wipes its value on the server.
    print("\nUpdating provider...")
    existing_metadata = dict(fetched_proto.metadata)
    updated_metadata = {**existing_metadata, "updated_by": "sample-script"}
    try:
        update_result = sc.actions._providers_client.update_custom_provider(
            identifier=fetched_proto.identifier,
            display_name=fetched_proto.display_name,
            proxy_url=fetched_proto.proxy_url,
            description="Updated description via MCP",
            auth_patterns=[AuthPattern.from_dict(p) for p in MessageToDict(fetched_proto.auth_patterns)],
            metadata=updated_metadata,
        )
    except Exception as e:
        print(f"Failed to update provider: {e}")
        sys.exit(1)

    updated_proto = update_result[0].provider
    print(f"Provider (after update):\n{MessageToJson(updated_proto)}")

    # ── Delete ────────────────────────────────────────────────────────────────
    print("\nDeleting provider...")
    try:
        sc.actions._providers_client.delete_custom_provider(
            identifier=updated_proto.identifier,
        )
    except Exception as e:
        print(f"Failed to delete provider: {e}")
        sys.exit(1)

    print(f"Provider '{updated_proto.identifier}' deleted successfully.")


if __name__ == "__main__":
    main()
