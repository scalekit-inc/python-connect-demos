"""
Tableau proxy examples using the Scalekit proxy.

Tableau binary downloads (PNG, PDF, Excel, .twbx, .tdsx) must go through
the Scalekit proxy — the session token (X-Tableau-Auth) is injected
automatically. The site ID is resolved from the connected account after
sign-in; call tableau_session_get once to retrieve it for URL construction.

Run:
    python tableau.py
"""

import os

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")

# Your Tableau connection name from the Scalekit dashboard and your user ID
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER_IDENTIFIER>"

# IDs to fill in before running — fetch these via tableau_workbooks_list
# and tableau_views_list first (see comments below).
VIEW_ID = "<YOUR_VIEW_ID>"
WORKBOOK_ID = "<YOUR_WORKBOOK_ID>"
DATASOURCE_ID = "<YOUR_DATASOURCE_ID>"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    connected_account = actions.get_connected_account(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
    ).connected_account

    # ── Get site ID ───────────────────────────────────────────────────────────
    # The site ID (LUID) is needed to build proxy URL paths.
    # Call tableau_session_get once and reuse the value for all requests.

    session = actions.execute_tool(
        tool_name="tableau_session_get",
        connected_account_id=connected_account.id,
        tool_input={},
    )
    site_id = session["session"]["site"]["id"]
    print(f"Site ID: {site_id}")

    # ── Discover IDs (optional — uncomment to find VIEW_ID / WORKBOOK_ID) ────
    #
    # workbooks = actions.execute_tool(
    #     tool_name="tableau_workbooks_list",
    #     connected_account_id=connected_account.id,
    #     tool_input={},
    # )
    # for wb in workbooks["workbooks"]["workbook"]:
    #     print(f"Workbook: {wb['id']}  {wb['name']}")
    #
    # views = actions.execute_tool(
    #     tool_name="tableau_views_list",
    #     connected_account_id=connected_account.id,
    #     tool_input={},
    # )
    # for v in views["views"]["view"]:
    #     print(f"View: {v['id']}  {v['name']}")

    # ── Export a view as PNG ──────────────────────────────────────────────────

    print(f"\nExporting view {VIEW_ID} as PNG...")

    image_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/views/{VIEW_ID}/image",
        method="GET",
        query_params={"resolution": "high"},
    )

    if image_response.status_code != 200:
        print(f"PNG export failed: {image_response.status_code} {image_response.text}")
        return

    with open("dashboard.png", "wb") as f:
        f.write(image_response.content)
    print(f"Saved dashboard.png ({len(image_response.content):,} bytes)")

    # ── Export a view as PDF ──────────────────────────────────────────────────

    print(f"\nExporting view {VIEW_ID} as PDF...")

    pdf_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/views/{VIEW_ID}/pdf",
        method="GET",
        query_params={"type": "a4", "orientation": "landscape"},
    )

    if pdf_response.status_code != 200:
        print(f"PDF export failed: {pdf_response.status_code} {pdf_response.text}")
        return

    with open("dashboard.pdf", "wb") as f:
        f.write(pdf_response.content)
    print(f"Saved dashboard.pdf ({len(pdf_response.content):,} bytes)")

    # ── Download a workbook (.twbx) ───────────────────────────────────────────

    print(f"\nDownloading workbook {WORKBOOK_ID}...")

    workbook_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/workbooks/{WORKBOOK_ID}/content",
        method="GET",
    )

    if workbook_response.status_code != 200:
        print(f"Workbook download failed: {workbook_response.status_code} {workbook_response.text}")
        return

    with open("workbook.twbx", "wb") as f:
        f.write(workbook_response.content)
    print(f"Saved workbook.twbx ({len(workbook_response.content):,} bytes)")

    # ── Download a data source (.tdsx) ────────────────────────────────────────

    print(f"\nDownloading data source {DATASOURCE_ID}...")

    datasource_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/datasources/{DATASOURCE_ID}/content",
        method="GET",
    )

    if datasource_response.status_code != 200:
        print(f"Data source download failed: {datasource_response.status_code} {datasource_response.text}")
        return

    with open("datasource.tdsx", "wb") as f:
        f.write(datasource_response.content)
    print(f"Saved datasource.tdsx ({len(datasource_response.content):,} bytes)")


if __name__ == "__main__":
    main()
