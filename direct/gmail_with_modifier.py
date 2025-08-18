import scalekit.client
import os
from dotenv import load_dotenv
from scalekit.connect.types import ToolInput, ToolOutput
from utils import authenticate_tool

# Load environment variables
load_dotenv()
user_id = "user_1234567890"
scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect

# Use Scalekit Connect to authenticate a user against a connection. If the user has already authenticated, this will do nothing.
# otherwise, it will return a link to authorize the connection.
authenticate_tool(connect, "GMAIL", user_id)

# sometimes, the tool input needs to be modified in a deterministic way before the tool is executed.
# For example, we can modify the query to only fetch unread emails regardless of what the user asks for or what the LLM determines.
@connect.pre_modifier(tool_names=["gmail_fetch_mails"])
def gmail_pre_modifier(tool_input: ToolInput):
    tool_input['query'] = 'is:unread'
    return tool_input

# sometimes, the tool output needs to be modified in a deterministic way after the tool is executed.
# For example, we can modify the output to only return the first email snippet regardless of what the tool returns.
# this is an effective way to reduce the amount of data that is returned to the LLM to save on tokens.
@connect.post_modifier(tool_names=["gmail_fetch_mails"])
def gmail_post_modifier(output:ToolOutput):
    # only return the first email snippet
    # should return a dict
    return {"response":output['messages'][0]['snippet']}


# execute the tool for a given user and tool input
response = connect.execute_tool(
    tool_name="gmail_fetch_mails",
    identifier=user_id,
    tool_input={
        "max_results" : 1
    },
)




print(f"✅ Results: {response}")