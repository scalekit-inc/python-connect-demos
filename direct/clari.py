import json

import scalekit.client
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
connection_name = "clari_copilot" # Get this from your scalekit dashboard
identifier = "clari_user"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit.actions


response = actions.get_or_create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details= {
        "static_auth": {
            "username": "Clari API Key",
            "password": "Clari API Password"
        }
    }
)



auth_details = response.connected_account.authorization_details
print(auth_details['static_auth']['username'])
print(auth_details['static_auth']['password'])



update_response = scalekit.actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details= {
        "static_auth": {
            "username": "New API Key",
            "password" :"New Password"
        }
    }
)

auth_details = update_response.connected_account.authorization_details

print("Updated Auth Details:")
print(auth_details['static_auth']['username'])
print(auth_details['static_auth']['password'])