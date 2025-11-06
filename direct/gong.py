import json

import scalekit.client
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
connection_name = "gong" # Get this from your scalekit dashboard
identifier = "yourGongUser"


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
            "domain": "youraccount.gong.com",
            "username": "Gong API Key",  # Your Gong API  Key username
            "password": "Gong API Key Secret" # Your Gong API Key  Secret as password
        }
    }
)



auth_details = response.connected_account.authorization_details
print(auth_details['static_auth']['username'])
print(auth_details['static_auth']['domain'])

#uncomment to see password
#print(auth_details['static_auth']['password'])


update_response = scalekit.actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details= {
        "static_auth": {
            "domain": "youraccount.gong.com",
            "username": "Updated Gong API Key",  # Your Gong API  Key username
            "password": "Updated Gong API Key Secret" # Your Gong API Key  Secret as password
        }
    }
)

auth_details = update_response.connected_account.authorization_details

print("Updated Auth Details:")
print(auth_details['static_auth']['username'])
#uncomment to see password
#print(auth_details['static_auth']['password'])
print(auth_details['static_auth']['domain'])
