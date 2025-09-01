import os
import asyncio
from dotenv import load_dotenv
import scalekit.client
from scalekit.connect.types import ToolMapping
from utils import authenticate_tool

load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect

def main():


    connected_account = connect.get_or_create_connected_account(
        connection_name="FRESHDESK",
        identifier="avinash",
        authorization_details= {
            "static_auth": {
                "domain": "avinashmkamath.freshdesk.com",
                "username": "ikipj7k9dasd8TsUJJWRXZganAk"
            }
        }
    )

    mcp_response = connect.create_mcp(
        identifier = "avinash",
        tool_mappings = [
            ToolMapping(
                tool_names=["freshdesk_create_ticket","freshdesk_list_tickets"],
                connection_name="FRESHDESK",
            )
        ]
    )

    print(mcp_response.url)

main()