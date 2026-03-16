import json

import scalekit.client
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
connection_name = "your_zendesk_token" # Get this from your scalekit dashboard
identifier = "your_zendesk"


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
            "domain": "scalekithelp.zendesk.com",
            "username": "avinash.kamath@scalekit.com",  # Zendesk email/username
            "password": "Zendesk Password"  # Zendesk  API token
        }
    }
)


# list of tickets for the authenticate user
response = scalekit.actions.execute_tool(
    tool_name="zendesk_tickets_list",
    identifier=identifier,
    tool_input={
        "page": "1"
    }
)

print(response)

