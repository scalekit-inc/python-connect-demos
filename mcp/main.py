
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

async def main():

    #create connected account for identifier default and connection name GMAIL,CALENDAR
    authenticate_tool(connect,"GMAIL", "user_1234567890")
    authenticate_tool(connect,"GCAL", "user_1234567890")

    mcp_response = connect.create_mcp(
        identifier = "user_1234567890",
        tool_mappings = [
            ToolMapping(
                tool_names=["gmail_fetch_mails", "gmail_send_mails"],
                connection_name="GMAIL",
            ),
            ToolMapping(
                tool_names=["googlecalendar_list_events", "googlecalendar_create_event"],
                connection_name="GCAL",
            )
        ]
    )

    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langgraph.prebuilt import create_react_agent

    # Print the URL of the created MCP
    print("MCP created successfully:", mcp_response.url)

    client = MultiServerMCPClient(
        {
            "gcal_demo": {
                "transport": "streamable_http",
                "url": mcp_response.url
            },
        }
    )
    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4.1", tools)
    gcal_response = await agent.ainvoke({"messages": "show me my calendar events for today"})

    print(gcal_response)


asyncio.run(main())

