import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET")
)
connect = scalekit.connect


link_response = connect.get_authorization_link(
    connection_name="SLACK",
    identifier="default",
)

print("click on the link to authorize slack", link_response.link)
input("Press Enter after authorizing Slack...")

response = scalekit.connect.execute_tool(
    tool_name="slack_send_message",
    identifier="default",
    tool_input={
        "channel": "#connect",
        "text": "Hello from demo!",
    },
)

print(response)



