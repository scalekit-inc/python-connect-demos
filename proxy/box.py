"""
Box file upload and download examples using the Scalekit proxy.

Box file uploads go to upload.box.com (not api.box.com) and require
multipart form data — pass files= as a kwarg so requests sets the
correct Content-Type boundary automatically.

Run:
    python box.py
"""

import json
import mimetypes
import os
import time

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")

# Your Box connection name from the Scalekit dashboard and your user ID
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    actions = client.actions

    # ── Upload a file ─────────────────────────────────────────────────────────
    # Box uploads go to upload.box.com, not api.box.com.
    # Scalekit injects the Authorization: Bearer token automatically.

    file_path = "test_file.txt"
    file_name = f"demo_upload_test{int(time.time())}.txt"

    with open(file_path, "w") as f:
        f.write("Hello from Scalekit SDK demo!")

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
        headers={"x-proxy-domain": "upload.box.com"},
        files={
            "attributes": (None, attributes, "application/json"),
            "file": (file_name, file_bytes, mime_type),
        },
    )

    if upload_response.status_code not in (200, 201):
        print(f"Upload failed: {upload_response.status_code} {upload_response.text}")
        return

    file_id = upload_response.json()["entries"][0]["id"]
    print(f"Uploaded. File ID: {file_id}")

    # ── Download a file ───────────────────────────────────────────────────────
    # Box returns a 302 redirect to a pre-signed CDN URL — requests follows it automatically.

    output_path = "downloaded_file.txt"
    print(f"\nDownloading file {file_id}...")

    download_response = actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/2.0/files/{file_id}/content",
        method="GET"
    )

    with open(output_path, "wb") as f:
        f.write(download_response.content)
    print(f"Downloaded to: {output_path} ({len(download_response.content):,} bytes)")



if __name__ == "__main__":
    main()
