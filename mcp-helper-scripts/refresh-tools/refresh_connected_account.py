#!/usr/bin/env python3
"""Force-refresh tools for a given Scalekit connected account (ca_xxx).

Uses scalekit-sdk-python. The SDK authenticates with your client credentials
internally, so there is no separate access-token step.
"""

from scalekit import ScalekitClient
from scalekit.v1.connected_accounts.connected_accounts_pb2 import UpdateConnectedAccount

# ─────────────────────────────────────────────────────────────
# YOUR INPUTS HERE
# ─────────────────────────────────────────────────────────────
ENV_URL = "https://your-auth-domain"   # your environment URL
CLIENT_ID = "skc_xxxxxx"               # SCALEKIT_CLIENT_ID
CLIENT_SECRET = "xxxxxxxx"             # SCALEKIT_CLIENT_SECRET
CA_ID = "ca_xxxxxx"                     # connected account id
# ─────────────────────────────────────────────────────────────


def main() -> None:
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
