import scalekit.client
import os
from dotenv import load_dotenv



# Load environment variables
load_dotenv()
connection_name = "salesforce-connected" # Get this from your scalekit dashboard
identifier = "sandbox-user-1"  # A unique identifier for the connected account


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit.actions

response = actions.get_or_create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    api_config={
        "environment_type" : "SANDBOX",
    }
)

link = actions.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)

print("click on the link to authorize Salseforce", link.link)
input("Press Enter after authorizing salesforce...")


tool_response = scalekit.connect.execute_tool(
    tool_name="salesforce_soql_execute",
    identifier=identifier,
    tool_input={
        "soql_query": "SELECT Id, Name FROM Account"
    }
)

print(tool_response)

# change the environment type to PRODUCTION after testing
response = actions.update_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    api_config={
        "environment_type" : "PRODUCTION",
    }
)
print("Updated connected account to PRODUCTION")