"""
Tableau export and download examples using the Scalekit proxy.

Tableau's export endpoints (PDF, image, crosstab, CSV data) and download
endpoints (workbook .twbx, datasource .tdsx) return binary file content.
Use actions.request() to retrieve the bytes and save them locally.

Run:
    python tableau.py
"""

import os

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("ENV_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Your Tableau connection name from the Scalekit dashboard and your user identifier
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER_IDENTIFIER>"

# IDs — get these from the list/get tools (e.g. tableau_workbooks_list, tableau_views_list)
SITE_ID = "<YOUR_SITE_ID>"
WORKBOOK_ID = "<YOUR_WORKBOOK_ID>"
VIEW_ID = "<YOUR_VIEW_ID>"
DATASOURCE_ID = "<YOUR_DATASOURCE_ID>"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    # ── Export view as PDF ────────────────────────────────────────────────────

    print("Exporting view as PDF...")
    pdf_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/views/{VIEW_ID}/pdf",
        method="GET",
        query_params={
            "type": "A4",          # page size: Letter, Legal, A4, A5, B5
            "orientation": "Landscape",  # Portrait or Landscape
        },
    )
    with open("view_export.pdf", "wb") as f:
        f.write(pdf_response.content)
    print(f"PDF saved to: view_export.pdf ({len(pdf_response.content):,} bytes)")

    # ── Export view as PNG image ──────────────────────────────────────────────

    print("\nExporting view as image...")
    image_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/views/{VIEW_ID}/image",
        method="GET",
        query_params={
            "resolution": "high",  # high or standard
        },
    )
    with open("view_export.png", "wb") as f:
        f.write(image_response.content)
    print(f"Image saved to: view_export.png ({len(image_response.content):,} bytes)")

    # ── Export view crosstab as Excel ─────────────────────────────────────────

    print("\nExporting view crosstab as Excel...")
    crosstab_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/views/{VIEW_ID}/crosstab/excel",
        method="GET",
    )
    with open("view_crosstab.xlsx", "wb") as f:
        f.write(crosstab_response.content)
    print(f"Crosstab saved to: view_crosstab.xlsx ({len(crosstab_response.content):,} bytes)")

    # ── Export view data as CSV ───────────────────────────────────────────────

    print("\nExporting view data as CSV...")
    data_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/views/{VIEW_ID}/data",
        method="GET",
        query_params={
            "pageSize": 200,
            "pageNumber": 1,
        },
    )
    with open("view_data.csv", "wb") as f:
        f.write(data_response.content)
    print(f"CSV saved to: view_data.csv ({len(data_response.content):,} bytes)")

    # ── Download workbook (.twbx) ─────────────────────────────────────────────

    print(f"\nDownloading workbook {WORKBOOK_ID}...")
    workbook_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/workbooks/{WORKBOOK_ID}/content",
        method="GET",
    )
    with open("workbook.twbx", "wb") as f:
        f.write(workbook_response.content)
    print(f"Workbook saved to: workbook.twbx ({len(workbook_response.content):,} bytes)")

    # ── Download data source (.tdsx) ──────────────────────────────────────────

    print(f"\nDownloading data source {DATASOURCE_ID}...")
    datasource_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/3.28/sites/{SITE_ID}/datasources/{DATASOURCE_ID}/content",
        method="GET",
    )
    with open("datasource.tdsx", "wb") as f:
        f.write(datasource_response.content)
    print(f"Data source saved to: datasource.tdsx ({len(datasource_response.content):,} bytes)")


if __name__ == "__main__":
    main()
