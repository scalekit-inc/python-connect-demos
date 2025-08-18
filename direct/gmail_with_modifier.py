import scalekit.client
import os
from dotenv import load_dotenv
from scalekit.connect.types import ToolInput, ToolOutput


# Load environment variables
load_dotenv()
user_id = "user_1234567890"
scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect

def authenticate_tool(connection_name, identifier):
    
    try:
        response = connect.get_connected_account(
            connection_name=connection_name,
            identifier=identifier
        )
        if(response.connected_account.status != "ACTIVE"):
            print(f"{connection_name} is not connected: {response.connected_account.status}")
            link_response = connect.get_authorization_link(
                connection_name=connection_name,
                identifier=identifier
            )
            print(f"🔗click on the link to authorize {connection_name}", link_response.link)
            input(f"⎆ Press Enter after authorizing {connection_name}...")
    except Exception as e:
        link_response = connect.get_authorization_link(
            connection_name=connection_name,
            identifier=identifier
        )
        print(f"🔗 click on the link to authorize {connection_name}", link_response.link)
        input(f"⎆ Press Enter after authorizing {connection_name}...")
    
    return True

authenticate_tool("GMAIL", user_id)


@connect.post_modifier(tool_names=["gmail_fetch_mails"])
def gmail_post_modifier(output:ToolOutput):
    # only return the first email snippet
    # should return a dict
    return {"response":output['messages'][0]['snippet']}

@connect.pre_modifier(tool_names=["gmail_fetch_mails"])
def gmail_pre_modifier(tool_input: ToolInput):
    tool_input['query'] = 'is:unread'
    return tool_input


response = connect.execute_tool(
    tool_name="gmail_fetch_mails",
    identifier=user_id,
    tool_input={
        "max_results" : 1
    },
)

print(f"✅ Results: {response}")