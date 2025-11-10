import json

import scalekit.client
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth




# Load environment variables
load_dotenv()
connection_name = "gong-uceg5u9E" # Get this from your scalekit dashboard
identifier = "yourGongUserASdasdasd"


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
            "domain": "us-30899.api.gong.io",
            "username": "C524S6V36EE4ID4K4IBJW2WFGGZLP5OM",  # Your Gong API  Key username
            "password": "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjIwNzc3OTE1NDcsImFjY2Vzc0tleSI6IkM1MjRTNlYzNkVFNElENEs0SUJKVzJXRkdHWkxQNU9NIn0.52BD5YN8LEppIO2_0B83INQq_XwF9-ayMI5_xD2AD8s" # Your Gong API Key  Secret as password
        }
    }
)

auth_details = update_response.connected_account.authorization_details

print("Updated Auth Details:")
print(auth_details['static_auth']['username'])
#uncomment to see password
#print(auth_details['static_auth']['password'])
print(auth_details['static_auth']['domain'])


#make an api call using a tool
# Use requests to call the Gong API: GET https://{domain}/v2/users with Basic Auth
domain = auth_details['static_auth'].get('domain')
username = auth_details['static_auth'].get('username')
password = auth_details['static_auth'].get('password')

if not domain or not username or not password:
    print("Missing domain/username/password in connected account authorization_details; skipping API call.")
else:
    url = f"https://{domain}/v2/users"
    print(f"Making GET request to: {url}")
    resp = None
    try:
        # Send Accept: application/json header so the API returns JSON when available
        headers = {"Accept": "application/json"}
        # Use explicit HTTPBasicAuth for Basic Authentication
        resp = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, timeout=10)
        resp.raise_for_status()
        # Try to parse JSON, else print text
        try:
            data = resp.json()
            print("GET /v2/users response JSON:")
            print(json.dumps(data, indent=2))
        except ValueError:
            print("GET /v2/users response text:")
            print(resp.text)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        if resp is not None:
            print(f"Status code: {getattr(resp, 'status_code', 'N/A')}")
            print(f"Response body: {getattr(resp, 'text', '')}")
