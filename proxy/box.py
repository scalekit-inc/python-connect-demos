"""
Box file upload and download examples using the Scalekit proxy.

Box file uploads go to upload.box.com (not api.box.com) and require
multipart form data — use actions.request() for both upload and download.

Run:
    python box.py
"""

import json
import mimetypes
import os

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("ENV_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Your Box connection name from the Scalekit dashboard and your user ID
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER_IDENTIFIER>"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    # ── Upload a file ─────────────────────────────────────────────────────────
    # Box uploads go to upload.box.com, not api.box.com.
    # Scalekit injects the Authorization: Bearer token automatically.

    file_path = "test_file.txt"
    file_name = "demo_upload.txt"

    # Create a test file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("Hello from Scalekit Box proxy example!")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    print(f"Uploading {file_name} ({len(file_bytes):,} bytes)...")

    # Box requires a JSON attributes part and a file part in multipart.
    # Parent folder ID "0" is the root folder.
    attributes = json.dumps({"name": file_name, "parent": {"id": "0"}})

    upload_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path="/api/2.0/files/content",
        method="POST",
        form_data={
            "attributes": (None, attributes, "application/json"),
            "file": (file_name, file_bytes, mime_type),
        },
        base_url_override="https://upload.box.com",
    )

    if upload_response.status_code not in (200, 201):
        print(f"Upload failed: {upload_response.status_code} {upload_response.text}")
        return

    file_metadata = upload_response.json()
    file_id = file_metadata["entries"][0]["id"]
    print(f"Uploaded. File ID: {file_id}")

    # ── Download a file ───────────────────────────────────────────────────────

    output_path = "downloaded_file.txt"
    print(f"\nDownloading file {file_id}...")

    download_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/2.0/files/{file_id}/content",
        method="GET",
    )

    with open(output_path, "wb") as f:
        f.write(download_response.content)
    print(f"Downloaded. Saved to: {output_path} ({len(download_response.content):,} bytes)")

    # ── Get file metadata ─────────────────────────────────────────────────────

    print(f"\nFetching metadata for file {file_id}...")
    meta_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/2.0/files/{file_id}",
        method="GET",
    )
    meta = meta_response.json()
    print(f"Name: {meta['name']}, Size: {meta['size']} bytes, Modified: {meta['modified_at']}")

    # ── List root folder contents ─────────────────────────────────────────────

    print("\nListing root folder contents...")
    folder_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path="/api/2.0/folders/0/items",
        method="GET",
        params={"limit": 10},
    )
    items = folder_response.json()
    for entry in items.get("entries", []):
        print(f"  [{entry['type']}] {entry['name']} (ID: {entry['id']})")

    # ── Delete the uploaded file ──────────────────────────────────────────────

    print(f"\nDeleting file {file_id}...")
    delete_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/api/2.0/files/{file_id}",
        method="DELETE",
    )
    if delete_response.status_code == 204:
        print("Deleted successfully.")
    else:
        print(f"Delete returned: {delete_response.status_code}")


if __name__ == "__main__":
    main()
