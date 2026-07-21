#!/usr/bin/env python3
"""Force-refresh tools for a given Scalekit connected account (ca_xxx).

Uses scalekit-sdk-python. The SDK authenticates with your client credentials
internally, so there is no separate access-token step.
"""

import os
import sys

from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.v1.connected_accounts.connected_accounts_pb2 import UpdateConnectedAccount

load_dotenv()

# ── Configuration (from .env — see .env.example) ─────────────
ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")
CA_ID = os.getenv("CONNECTED_ACCOUNT_ID")


def main() -> None:
    missing = [
        name
        for name, value in {
            "SCALEKIT_ENV_URL": ENV_URL,
            "SCALEKIT_CLIENT_ID": CLIENT_ID,
            "SCALEKIT_CLIENT_SECRET": CLIENT_SECRET,
            "CONNECTED_ACCOUNT_ID": CA_ID,
        }.items()
        if not value
    ]
    if missing:
        sys.exit(
            f"Missing required env var(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )

    client = ScalekitClient(
        env_url=ENV_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    # Step 1: fetch the connected account's current state
    print(f">> [1] Fetching connected account auth for {CA_ID} ...")
    fetch_response = client.actions.get_connected_account(connected_account_id=CA_ID)
    print(fetch_response)

    # Step 2: Force refreshing tools
    print(f">> [2] Force refreshing tools {CA_ID} ...")
    update_response = client.connected_accounts.update_connected_account(
        connector="",
        identifier="",
        connected_account=UpdateConnectedAccount(),
        connected_account_id=CA_ID,
    )
    status = update_response[1].code().name
    print(f">> Update status: {status}")
    print(update_response[0].connected_account)

    print(">> Tools refresh done.")


if __name__ == "__main__":
    main()
