import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET")
)
actions = scalekit.actions

CONNECTOR  = "bigqueryserviceaccount"
IDENTIFIER = "bigquery-demo-user"

# Service account JSON (replace with a real one)
SERVICE_ACCOUNT_JSON = """{
  "type": "service_account",
  "project_id": "my-gcp-project",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nREPLACE_WITH_REAL_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
  "client_email": "my-sa@my-gcp-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-sa%40my-gcp-project.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}"""

# Step 1: Get or create connected account with service account credentials
response = actions.get_or_create_connected_account(
    connection_name=CONNECTOR,
    identifier=IDENTIFIER,
    authorization_details={
        "static_auth": {
            "service_account_json": SERVICE_ACCOUNT_JSON
        }
    }
)

account = response.connected_account
print(f"Connected account: {account.id} | Status: {account.status}")

# Step 2: Execute a BigQuery tool
result = actions.execute_tool(
    tool_name="bigqueryserviceaccount_run_query",
    connection_name=CONNECTOR,
    identifier=IDENTIFIER,
    tool_input={
        "query": "SELECT 1 AS test"
    }
)

print("Query result:", result.data)
