import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALKIT_CLIENT_SECRET"),
    env_url="https://kindle-dev.scalekit.cloud",
)




connect = scalekit.connect


link_response = connect.get_authorization_link(
    connection_name="SLACK",
    identifier="avinash.kamath@scalekit.com",
)

print("click on the link to authorize slack", link_response.link)
input("Press Enter after authorizing Slack...")

response = scalekit.connect.execute_tool(
    tool_name="SLACK.SEND_MESSAGE",
    identifier="avinash.kamath@scalekit.com",
    tool_input={
        "channel": "#connect",
        "text": "Hello from Show and tell !",
    },
)

print(response)



