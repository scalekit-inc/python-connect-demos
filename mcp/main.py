import os
from dotenv import load_dotenv
import scalekit.client
from scalekit.actions.models.mcp_config import McpConfigConnectionToolMapping
from scalekit.actions.types import (GetMcpInstanceAuthStateResponse)
from langgraph.prebuilt import create_react_agent
import asyncio

load_dotenv()

CONFIG_NAME = "reminder-manager"
CONFIG_DESCRIPTION = "Summarizes emails and creates calendar reminder event"
CONFIG_DESCRIPTION_UPDATED = "Updated summary and calendar automation config"
CONFIG_MAPPINGS = [
    McpConfigConnectionToolMapping(
        connection_name="MY_GMAIL",
        tools=[],
    ),
    McpConfigConnectionToolMapping(
        connection_name="MY_CALENDAR",
        tools=[
            "googlecalendar_create_event",
            "googlecalendar_delete_event",
        ],
    ),
]
INSTANCE_USER_IDENTIFIER = "john-doe"

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
my_mcp = scalekit.actions.mcp

async def main():
    # First create the MCP config
    config_exists = False
    config_name = None
    try:
        list_resp = my_mcp.list_configs(filter_name=CONFIG_NAME)
        config_exists = False
        if len(list_resp.configs) > 0 and list_resp.configs[0].id:
            config_exists = True
            config_name = list_resp.configs[0].name
            print(f"Config '{CONFIG_NAME}' already exists.")
    except Exception as e:
        print(f"Error checking for existing config: {e}")

    if not config_exists:
        print(f"Creating MCP config '{CONFIG_NAME}'...")
        config_response = my_mcp.create_config(
            name=CONFIG_NAME,
            description=CONFIG_DESCRIPTION,
            connection_tool_mappings=CONFIG_MAPPINGS,
        )
        config_name = config_response.config.name
        print("Config name: ", config_name)

    # Now get or create an MCP instance for a user
    print("Get Or Create MCP instance for user", INSTANCE_USER_IDENTIFIER, "on config", config_name)
    instance_response = my_mcp.ensure_instance(
        config_name=config_name,
        user_identifier=INSTANCE_USER_IDENTIFIER,
        name="reminder-mcp-john",
    )
    print("Instance name:", instance_response.instance.name)
    mcp_url = instance_response.instance.url

    # Now create auth links and load these links in browser to authenticate connections
    auth_state_response = my_mcp.get_instance_auth_state(
        instance_id=instance_response.instance.id,
        include_auth_links=True,
    )
    for conn in getattr(auth_state_response, "connections", []):
        print("Connection Name:", conn.connection_name, " Provider: ", conn.provider, " Auth Link: ", conn.authentication_link, "Auth Status: ", conn.connected_account_status)

    print("Authenticate with above links and type continue to connect the agent to this mcp")

    # while True:
    #     choice = input("Type 'continue' to proceed or 'exit' to quit: ").strip().lower()
    #     if choice == "continue":
    #         break
    #     if choice == "exit":
    #         print("Exiting.")
    #         return
    #     print("Invalid input. Please type 'continue' or 'exit'.")

    # Connect your agent to the MCP
    print("Connecting your agent to MCP:", mcp_url)

    from importlib import import_module
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        mcp_mod = import_module("langchain_mcp_adapters.client")
        MultiServerMCPClient = getattr(mcp_mod, "MultiServerMCPClient")

    client = MultiServerMCPClient(
        {
            "reminder_demo": {
                "transport": "streamable_http",
                "url": mcp_url
            },
        }
    )

    tools = await client.get_tools()

    agent = create_react_agent("openai:gpt-4.1", tools)
    openai_response = await agent.ainvoke({"messages": "get 1 latest email and create a calendar reminder event in next 15 mins for a duration of 15 mins."})

    print(openai_response)

if __name__ == "__main__":
    asyncio.run(main())