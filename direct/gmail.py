import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect
link_response = connect.get_authorization_link(
    connection_name="GMAIL",
    identifier="avinash.kamath@scalekit.com",
)

print("click on the link to authorize gmail", link_response.link)
input("Press Enter after authorizing gmail...")

response = scalekit.connect.execute_tool(
    tool_name="GMAIL_FETCH_MAILS",
    identifier="avinash.kamath@scalekit.com",
    tool_input={
        "max_results" : 1
    },
)

print(response)