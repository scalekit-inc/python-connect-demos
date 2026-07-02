"""
Salesforce file operations and SOQL queries using the Scalekit proxy.

This script demonstrates three operations against a connected Salesforce org:

1. Fetch Accounts — runs a SOQL SELECT via the /query endpoint, returning
   the top 10 accounts ordered by annual revenue.

2. Upload a file — POSTs a local PDF to the Salesforce Files library as a
   ContentVersion object. The file content is base64-encoded in the request
   body. A timestamp is appended to the filename to avoid collisions.

3. Download a file — fetches the raw binary from the ContentVersion/VersionData
   sub-resource using the ID returned by the upload, and saves it locally with
   a matching timestamp.

Scalekit injects the OAuth Authorization header and proxies all requests to
your connected Salesforce org — no manual token handling required.

Run:
    python salesforce_file_ops.py
"""

import base64
import os
from datetime import datetime

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALKIT_CLIENT_SECRET")

# Your Salesforce connection name from the Scalekit dashboard and your user ID
CONNECTION_NAME = "salesforce-ubB7gpKc"
IDENTIFIER = "avinash.kamath+1e1@scalekit.com"


def fetch_accounts(actions):
    # Fetch the top 10 Salesforce Accounts ordered by annual revenue.
    # Scalekit proxies the request and injects the OAuth token — no manual auth needed.
    print("Fetching top 10 Accounts...")

    result = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        method="GET",
        # Scalekit strips the /services/data/vXX.0 prefix, so just /query is used here
        path="/query",
        query_params={
            "q": "SELECT Id, Name, Industry, AnnualRevenue, BillingCity FROM Account ORDER BY AnnualRevenue DESC NULLS LAST LIMIT 10"
        },
    )

    accounts = result.json()
    for account in accounts.get("records", []):
        print(f"  {account['Name']} — {account.get('Industry', 'N/A')} — ${account.get('AnnualRevenue') or 0:,.0f}")



def upload_file(actions, file_path):
    # Salesforce Files API (ContentVersion) expects the file content as base64-encoded VersionData.
    # The uploaded file lands in the org's Files library and can be linked to any record later.
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(os.path.basename(file_path))
    file_name = f"{base}_{ts}{ext}"
    print(f"\nUploading {file_name}...")

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    result = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        method="POST",
        path="/sobjects/ContentVersion",
        body={
            "Title": file_name,
            # PathOnClient is required by Salesforce — it sets the file extension for type detection
            "PathOnClient": file_name,
            # VersionData must be base64 — Salesforce does not accept raw bytes here
            "VersionData": encoded,
        },
    )

    response = result.json()
    if result.status_code == 201:
        print(f"  Uploaded. ContentVersion ID: {response['id']}")
        return response["id"]
    else:
        print(f"  Upload failed ({result.status_code}): {response}")
        return None


def download_file(actions, content_version_id, output_path):
    # Download file content using the ContentVersion ID returned from upload.
    # Salesforce serves raw binary at the VersionData sub-resource.
    print(f"\nDownloading ContentVersion {content_version_id}...")

    result = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        method="GET",
        path=f"/sobjects/ContentVersion/{content_version_id}/VersionData",
    )

    if result.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(result.content)
        print(f"  Downloaded. Saved to: {output_path} ({len(result.content):,} bytes)")
    else:
        print(f"  Download failed ({result.status_code}): {result.text}")


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    #simple processing of the accounts fetched from salesforce
    fetch_accounts(actions)

    #uploading a file to salesforce
    content_version_id = upload_file(actions, "proxy/test_sdk_document.pdf")

    #downloading the file from salesforce using the content version id returned from upload
    if content_version_id:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        download_file(actions, content_version_id, f"proxy/test_sdk_document_downloaded_{ts}.pdf")


if __name__ == "__main__":
    main()
