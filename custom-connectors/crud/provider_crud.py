import os
import sys

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.types import (
    AuthPattern,
    CreateCustomProviderRequest,
    DeleteCustomProviderRequest,
    ListProvidersRequest,
    OAuthConfig,
    UpdateCustomProviderRequest,
)

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")


def main():
    sc = ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Create ────────────────────────────────────────────────────────────────
    # metadata (and icon_src) are supported directly on the high-level
    # providers facade since SDK 2.15.0 — no need for the low-level client.
    print("Creating custom OAuth provider...")
    try:
        create_response = sc.actions.providers.create_custom_provider(
            CreateCustomProviderRequest(
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
        )
    except Exception as e:
        print(f"Failed to create provider: {e}")
        sys.exit(1)

    provider = create_response.provider
    print(f"Provider created: identifier={provider.identifier}, name={provider.display_name}")
    print(f"Provider (after create):\n{provider.model_dump_json(indent=2)}")

    # ── Read ──────────────────────────────────────────────────────────────────
    # Always GET before UPDATE to read current state, including metadata.
    print("\nFetching provider before update...")
    try:
        list_response = sc.actions.providers.list_providers(
            ListProvidersRequest(identifier=provider.identifier)
        )
    except Exception as e:
        print(f"Failed to fetch provider: {e}")
        sys.exit(1)

    providers = list_response.providers
    fetched = providers[0] if providers else provider
    print(f"Provider (after GET):\n{fetched.model_dump_json(indent=2)}")

    # ── Update ────────────────────────────────────────────────────────────────
    # update_custom_provider is PUT-style, not PATCH — the server replaces the
    # entire provider with what you send. Always GET first, then echo back every
    # field you want to keep (display_name, proxy_url, auth_patterns, metadata,
    # etc.) alongside the fields you actually want to change. Omitting any field
    # silently wipes its value on the server.
    print("\nUpdating provider...")
    existing_metadata = dict(fetched.metadata)
    updated_metadata = {**existing_metadata, "updated_by": "sample-script"}
    try:
        update_response = sc.actions.providers.update_custom_provider(
            UpdateCustomProviderRequest(
                identifier=fetched.identifier,
                display_name=fetched.display_name,
                proxy_url=fetched.proxy_url,
                description="Updated description via MCP",
                auth_patterns=fetched.auth_patterns,
                metadata=updated_metadata,
            )
        )
    except Exception as e:
        print(f"Failed to update provider: {e}")
        sys.exit(1)

    updated = update_response.provider
    print(f"Provider (after update):\n{updated.model_dump_json(indent=2)}")

    # ── Delete ────────────────────────────────────────────────────────────────
    print("\nDeleting provider...")
    try:
        sc.actions.providers.delete_custom_provider(
            DeleteCustomProviderRequest(identifier=updated.identifier)
        )
    except Exception as e:
        print(f"Failed to delete provider: {e}")
        sys.exit(1)

    print(f"Provider '{updated.identifier}' deleted successfully.")


if __name__ == "__main__":
    main()
