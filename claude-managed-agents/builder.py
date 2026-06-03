import os
import sys
import tty
import termios
import anthropic
from dotenv import load_dotenv
from scalekit import ScalekitClient
from scalekit.actions.models.mcp_config import McpConfigConnectionToolMapping
from scalekit.v1.tools.tools_pb2 import Filter

load_dotenv()

os.makedirs("datastore", exist_ok=True)

anthropic_client = anthropic.Anthropic()
sk_client = ScalekitClient(
    env_url=os.environ["SCALEKIT_ENV_URL"],
    client_id=os.environ["SCALEKIT_CLIENT_ID"],
    client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
)

GMAIL_TOOLS = ["gmail_fetch_mails"]
GCAL_TOOLS = [
    "googlecalendar_list_calendars",
    "googlecalendar_list_events",
    "googlecalendar_get_event_by_id",
    "googlecalendar_create_event",
    "googlecalendar_update_event",
]


def wait_for_keypress():
    print("\nPress any key to continue...")
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    print()


connections_response, _ = sk_client.connection.list_app_connections()
connections = list(connections_response.connections)

print("Available apps and tools:\n")
for conn in connections:
    tools_response, _ = sk_client.tools.list_tools(filter=Filter(provider=conn.provider_key))
    print(f"  {conn.provider_key}")
    for tool_name in tools_response.tool_names:
        print(f"    {tool_name}")
    print()

wait_for_keypress()

print("For this demo we will use:\n")
print("  gmail")
for t in GMAIL_TOOLS:
    print(f"    {t}")
print()
print("  googlecalendar")
for t in GCAL_TOOLS:
    print(f"    {t}")
print()

wait_for_keypress()

gmail_conn = next(c for c in connections if "gmail" in c.provider_key.lower())
gcal_conn = next(c for c in connections if "calendar" in c.provider_key.lower())

config_response = sk_client.actions.create_config(
    name="email-calendar-demo",
    connection_tool_mappings=[
        McpConfigConnectionToolMapping(
            connection_name=gmail_conn.key_id,
            tools=GMAIL_TOOLS,
        ),
        McpConfigConnectionToolMapping(
            connection_name=gcal_conn.key_id,
            tools=GCAL_TOOLS,
        ),
    ],
)

mcp_server_url = config_response.config.mcp_server_url
config_id = config_response.config.id

with open("datastore/config_id.txt", "w") as f:
    f.write(config_id)

print(f"MCP Server URL : {mcp_server_url}")
print(f"Config ID      : {config_id}\n")
print("Your virtual MCP server is ready to be attached to an agent.")

wait_for_keypress()

agent = anthropic_client.beta.agents.create(
    name="Email Meeting Manager",
    model="claude-haiku-4-5-20251001",
    system=(
        "You are an email and calendar assistant. When invoked, you will:\n"
        "1. Fetch the single most recent UNREAD email from Gmail (query: 'is:unread in:inbox').\n"
        "2. Summarize it in 2-3 sentences.\n"
        "3. Create a Google Calendar event with:\n"
        "   - Title: 'Action Required: <email subject>'\n"
        "   - Start time: exactly as provided by the user\n"
        "   - End time: exactly as provided by the user\n"
        "   - Description: your 2-3 sentence summary of the email\n"
        "Report clearly: the email subject, your summary, and confirmation that the calendar event was created."
    ),
    mcp_servers=[
        {
            "type": "url",
            "name": "email-calendar-mcp",
            "url": mcp_server_url,
        }
    ],
    tools=[
        {"type": "agent_toolset_20260401", "default_config": {"enabled": True}},
        {
            "type": "mcp_toolset",
            "mcp_server_name": "email-calendar-mcp",
            "default_config": {
                "enabled": True,
                "permission_policy": {"type": "always_allow"},
            },
        },
    ],
)

with open("datastore/agent_id.txt", "w") as f:
    f.write(agent.id)

print(f"\nAgent created.\n")
print(f"  Name      : {agent.name}")
print(f"  ID        : {agent.id}")
print(f"  Version   : {agent.version}")
print(f"  Model     : {agent.model}")
print(f"  MCP URL   : {mcp_server_url}")
print(f"  Config ID : {config_id}")
print(f"\nAgent ID saved to datastore/agent_id.txt")
print(f"Config ID saved to datastore/config_id.txt")
print("\nAgent Builder flow complete.")
