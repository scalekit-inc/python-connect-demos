import mimetypes
import os

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv()



ENV_URL = os.getenv("ENV_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

CONNECTION_NAME = "googledrive-ci3BvjJC"
IDENTIFIER = "claude"


def main():
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)

    # ── Upload ────────────────────────────────────────────────────────────────

    file_path = "test_sdk_document.pdf"
    file_name = "demo_upload.pdf"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    print(f"Uploading {file_name} ({len(file_bytes):,} bytes)...")

    upload_response = client.actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path="/upload/drive/v3/files",
        method="POST",
        query_params={"uploadType": "media", "name": file_name},
        form_data=file_bytes,
        headers={"Content-Type": mime_type},
    )

    if upload_response.status_code != 200:
        print(f"Upload failed with status code {upload_response.status_code}: {upload_response.text}")
        return

    file_metadata = upload_response.json()
    file_id = file_metadata["id"]
    print(f"Uploaded. File ID: {file_id}")

    # ── Download ──────────────────────────────────────────────────────────────


    # file will be downloaded to this file
    output_path = "test_sdk_document_downloaded.pdf"

    print(f"Downloading file {file_id}...")

    download_response = client.actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/drive/v3/files/{file_id}",
        method="GET",
        query_params={"alt": "media"},
    )

    with open(output_path, "wb") as f:
        f.write(download_response.content)

    print(f"Downloaded. Saved to: {output_path} ({len(download_response.content):,} bytes)")

    # ── Export ────────────────────────────────────────────────────────────────

    # Export a Google Doc (Workspace file) as PDF — SDK TEST document
    # create a  doc  in your workspace and copy your file ID here, It can be found from the URL when you open the document in browser, it will be something like https://docs.google.com/document/d/FILE_ID/edit
    doc_id = "<YOUR_GOOGLE_DOC_FILE_ID>"
    export_path = "exported.pdf"

    print(f"Exporting Google Doc {doc_id} as PDF...")

    export_response = client.actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/drive/v3/files/{doc_id}/export",
        method="GET",
        query_params={"mimeType": "application/pdf"},
    )

    with open(export_path, "wb") as f:
        f.write(export_response.content)

    print(f"Exported. Saved to: {export_path} ({len(export_response.content):,} bytes)")


if __name__ == "__main__":
    main()