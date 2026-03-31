import os

from dotenv import load_dotenv
import scalekit.client as scalekit_sdk

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

ENV_URL = os.getenv("SCALEKIT_ENV_URL")
CLIENT_ID = os.getenv("SCALEKIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCALEKIT_CLIENT_SECRET")

# your google drive connection name from scalekit and your user identifier
CONNECTION_NAME = "<YOUR_CONNECTION_NAME>"
IDENTIFIER = "<YOUR_USER_IDENTIFIER>"


def export_via_custom_domain(client):
    file_id = "<YOUR_FILE_ID>"
    export_path = "exported.pdf"
    print(f"\nExporting presentation {file_id} as PDF via custom domain...")

    export_response = client.actions.request(
        connection_name=CONNECTION_NAME,
        identifier=IDENTIFIER,
        path=f"/presentation/d/{file_id}/export/pdf",
        method="GET",
        headers={"x-proxy-domain": "docs.google.com"},
    )

    print(f"Status: {export_response.status_code}")
    print(f"Headers: {dict(export_response.headers)}")
    if export_response.status_code != 200:
        print(f"Body: {export_response.text}")
        return

    with open(export_path, "wb") as f:
        f.write(export_response.content)

    size_mb = len(export_response.content) / (1024 * 1024)
    print(f"Exported. Saved to: {export_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    client = scalekit_sdk.ScalekitClient(ENV_URL, CLIENT_ID, CLIENT_SECRET)
    export_via_custom_domain(client)
