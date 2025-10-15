import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
identifier="user-1234"

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit.actions
link_response = actions.get_authorization_link(
    connection_name="linear-2",
    identifier=identifier
)
print("click on the link to authorize linear", link_response.link)
input("Press Enter after authorizing linear...")

response = scalekit.connect.execute_tool(
    tool_name="linear_issues_list",
    identifier=identifier,
    tool_input={
        "assignee" : "avinash.kamath@scalekit.com",
    },
)

print(response)