import scalekit.client
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
connection_name = "salesforce-external"
identifier = "user-test-123"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit.actions


link = actions.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)

print("click on the link to authorize Salseforce", link.link)
input("Press Enter after authorizing salesforce...")

response = actions.get_connected_account(
    connection_name=connection_name,
    identifier=identifier,
)

connected_account = response.connected_account

tokens = connected_account.authorization_details["oauth_token"]
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

print("access token:",access_token)
print("refresh token:",refresh_token)



#For salesforce update your domain and API version of your customer instance
updated_api_config = {
    "version": "API VERSION",
    "domain": "orgfarm-69f4803bbd-dev-ed.develop.my.salesforce.com",
}

actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    api_config=updated_api_config,
)

response = scalekit.connect.execute_tool(
    tool_name="salesforce_soql_execute",
    identifier=identifier,
    tool_input={
        "soql_query": "SELECT Id, Name FROM Account"
    }
)
