import json
import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

connection_name = "clari" # Get this from your scalekit dashboard
identifier = "your_clari_user"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)

actions = scalekit.actions

# Create or get connected account using static auth
response = actions.get_or_create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details={
        "static_auth": {
            "username": "CLARI_API_KEY",        # Clari Copilot API Key
            "password": "CLARI_API_PASSWORD"    # Clari Copilot API Password
        }
    }
)

auth_details = response.connected_account.authorization_details

print(auth_details["static_auth"]["username"])
# uncomment if you want to see the secret
# print(auth_details["static_auth"]["password"])

# Update credentials later if needed
update_response = actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details={
        "static_auth": {
            "username": "UPDATED_CLARI_API_KEY",
            "password": "UPDATED_CLARI_API_PASSWORD"
        }
    }
)

auth_details = update_response.connected_account.authorization_details

print("Updated Auth Details:")
print(auth_details["static_auth"]["username"])
# uncomment to see password
# print(auth_details["static_auth"]["password"])
