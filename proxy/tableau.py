"""
Tableau binary export examples using the Scalekit proxy.

Binary responses (PNG images, PDF files, Excel files, .twbx workbooks, .tdsx
data sources) must be downloaded through actions.request() — the SDK's
execute_tool() only handles JSON responses.

Run:
    python tableau.py
"""

import os
import time

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("ENV_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Your Tableau connection name from the Scalekit dashboard and your user ID
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER_IDENTIFIER>"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    # ── Step 1: Get connected account ────────────────────────────────────────

    connected_account = actions.get_connected_account(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
    ).connected_account

    # ── Step 2: Get site ID ───────────────────────────────────────────────────
    # The site_id (LUID) is required for every Tableau REST API call.
    # Call tableau_session_get once and cache it for the session.

    session = actions.execute_tool(
        tool_name="tableau_session_get",
        connected_account_id=connected_account.id,
        tool_input={},
    )
    site_id = session["session"]["site"]["id"]
    print(f"Site ID: {site_id}")

    # ── Step 3: Discover workbooks and views ──────────────────────────────────

    workbooks = actions.execute_tool(
        tool_name="tableau_workbooks_list",
        connected_account_id=connected_account.id,
        tool_input={"site_id": site_id},
    )
    workbook = workbooks["workbooks"]["workbook"][0]
    workbook_id = workbook["id"]
    print(f"Workbook: {workbook['name']} (ID: {workbook_id})")

    views = actions.execute_tool(
        tool_name="tableau_list_views",
        connected_account_id=connected_account.id,
        tool_input={"site_id": site_id, "workbook_id": workbook_id},
    )
    view = views["views"]["view"][0]
    view_id = view["id"]
    print(f"View: {view['name']} (ID: {view_id})")

    # ── Export: PNG image ─────────────────────────────────────────────────────
    # Scalekit automatically injects the X-Tableau-Auth session token header.

    print("\nDownloading view as PNG...")
    response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/views/{view_id}/image",
        method="GET",
        params={"resolution": "high"},  # optional: 'high' or 'standard'
    )
    with open("dashboard.png", "wb") as f:
        f.write(response.content)
    print(f"Saved dashboard.png ({len(response.content):,} bytes)")

    # ── Export: PDF ───────────────────────────────────────────────────────────

    print("\nDownloading view as PDF...")
    response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/views/{view_id}/pdf",
        method="GET",
        params={"type": "a4", "orientation": "landscape"},
    )
    with open("dashboard.pdf", "wb") as f:
        f.write(response.content)
    print(f"Saved dashboard.pdf ({len(response.content):,} bytes)")

    # ── Export: Excel (crosstab) ──────────────────────────────────────────────

    print("\nDownloading view as Excel...")
    response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/views/{view_id}/crosstab/excel",
        method="GET",
    )
    with open("dashboard.xlsx", "wb") as f:
        f.write(response.content)
    print(f"Saved dashboard.xlsx ({len(response.content):,} bytes)")

    # ── Download: Full workbook (.twbx) ───────────────────────────────────────

    print("\nDownloading full workbook (.twbx)...")
    response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/workbooks/{workbook_id}/content",
        method="GET",
    )
    with open("workbook.twbx", "wb") as f:
        f.write(response.content)
    print(f"Saved workbook.twbx ({len(response.content):,} bytes)")

    # ── Trigger a data source refresh and poll the job ────────────────────────
    # Refresh triggering and job polling use execute_tool (JSON responses).

    datasources = actions.execute_tool(
        tool_name="tableau_datasources_list",
        connected_account_id=connected_account.id,
        tool_input={"site_id": site_id},
    )
    datasource = datasources["datasources"]["datasource"][0]
    datasource_id = datasource["id"]
    print(f"\nDatasource: {datasource['name']} (ID: {datasource_id})")

    print("Triggering extract refresh...")
    refresh = actions.execute_tool(
        tool_name="tableau_datasource_refresh",
        connected_account_id=connected_account.id,
        tool_input={"site_id": site_id, "datasource_id": datasource_id},
    )
    job_id = refresh["job"]["id"]
    print(f"Job ID: {job_id}")

    while True:
        time.sleep(10)
        job = actions.execute_tool(
            tool_name="tableau_job_get",
            connected_account_id=connected_account.id,
            tool_input={"site_id": site_id, "job_id": job_id},
        )
        status = job["job"]["status"]
        print(f"  Status: {status}")
        if status != "InProgress":
            break
    print(f"Refresh completed: {status}")

    # ── Download: Data source package (.tdsx) ─────────────────────────────────

    print("\nDownloading data source (.tdsx)...")
    response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{site_id}/datasources/{datasource_id}/content",
        method="GET",
    )
    with open("datasource.tdsx", "wb") as f:
        f.write(response.content)
    print(f"Saved datasource.tdsx ({len(response.content):,} bytes)")

    # ── Sign out ──────────────────────────────────────────────────────────────
    # Invalidate the session token when the agent session ends.

    actions.execute_tool(
        tool_name="tableau_auth_signout",
        connected_account_id=connected_account.id,
        tool_input={},
    )
    print("\nSigned out. Session token invalidated.")


if __name__ == "__main__":
    main()
