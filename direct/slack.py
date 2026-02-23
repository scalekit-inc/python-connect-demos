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
actions = scalekit.actions


link_response = actions.get_authorization_link(
    connection_name="SLACK",
    identifier="user_123234234", #vons user ID
)


print("click on the link to authorize slack", link_response.link)
input("Press Enter after authorizing Slack...")

response = actions.execute_tool(
    tool_name="slack_send_message",
    identifier="idento", #vons user ID
    tool_input={
        "channel": "#connect",
        "text": "Hello from Avinash via ScaleKit Connect!",
    },
)

print(response)
