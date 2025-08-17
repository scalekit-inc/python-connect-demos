import scalekit.client
import os
from dotenv import load_dotenv
from scalekit.connect.types import ToolInput, ToolOutput


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
    identifier="default",
)

print("click on the link to authorize gmail", link_response.link)
input("Press Enter after authorizing gmail...")

@connect.post_modifier(tool_names=["gmail_fetch_mails"])
def gmail_post_modifier(output:ToolOutput):
    # only return the first email snippet
    # should return a dict
    return {"response":output['messages'][0]['snippet']}

@connect.pre_modifier(tool_names=["gmail_fetch_mails"])
def gmail_pre_modifier(tool_input: ToolInput):
    tool_input['query'] = 'is:unread'
    return tool_input


response = scalekit.connect.execute_tool(
    tool_name="gmail_fetch_mails",
    identifier="default",
    tool_input={
        "max_results" : 1
    },
)

print(response)