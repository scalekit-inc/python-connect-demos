import os
import sys
import tty
import termios
from datetime import datetime, timezone, timedelta
import anthropic
from dotenv import load_dotenv
from scalekit import ScalekitClient

load_dotenv()

os.makedirs("datastore", exist_ok=True)

anthropic_client = anthropic.Anthropic()
sk_client = ScalekitClient(
    env_url=os.environ["SCALEKIT_ENV_URL"],
    client_id=os.environ["SCALEKIT_CLIENT_ID"],
    client_secret=os.environ["SCALEKIT_CLIENT_SECRET"],
)


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


for fname in ("datastore/config_id.txt", "datastore/identifier.txt", "datastore/agent_id.txt"):
    if not os.path.exists(fname):
        print(f"ERROR: {fname} not found. Run builder.py and executor_setup.py first.")
        sys.exit(1)

config_id  = open("datastore/config_id.txt").read().strip()
identifier = open("datastore/identifier.txt").read().strip()
agent_id   = open("datastore/agent_id.txt").read().strip()

print("Running background claude managed agent...\n")
print(f"  Agent ID   : {agent_id}")
print(f"  Identifier : {identifier}\n")

print("Checking connected account status...")
accounts_response = sk_client.actions.mcp.list_mcp_connected_accounts(
    config_id=config_id,
    identifier=identifier,
    include_auth_link=False,
)
inactive = [
    a.connection_name
    for a in accounts_response.connected_accounts
    if a.connected_account_status.lower() != "active"
]
if inactive:
    print(f"\nConnected accounts for identifier '{identifier}' are not in active state:")
    for name in inactive:
        print(f"  ✗ {name}")
    print("\nPlease run executor_setup.py to authorize the required connections.")
    sys.exit(1)
print("All connected accounts are active.\n")

print("Minting token using Scalekit and storing in CMA user vault...")

configs_response = sk_client.actions.mcp.list_configs(filter_id=config_id)
mcp_server_url = configs_response.configs[0].mcp_server_url

token_response = sk_client.actions.mcp.create_session_token(
    mcp_config_id=config_id,
    identifier=identifier,
    expiry=timedelta(seconds=3600),
)
token = token_response.token

if os.path.exists("datastore/vault_id.txt") and os.path.exists("datastore/credential_id.txt"):
    vault_id      = open("datastore/vault_id.txt").read().strip()
    credential_id = open("datastore/credential_id.txt").read().strip()
    anthropic_client.beta.vaults.credentials.update(
        credential_id,
        vault_id=vault_id,
        auth={
            "type": "mcp_oauth",
            "access_token": token,
        },
    )
else:
    vault = anthropic_client.beta.vaults.create(display_name=f"email-meeting-{identifier[:8]}")
    vault_id = vault.id

    credential = anthropic_client.beta.vaults.credentials.create(
        vault_id,
        display_name=f"email-meeting-{identifier[:8]}-credential",
        auth={
            "type": "mcp_oauth",
            "mcp_server_url": mcp_server_url,
            "access_token": token,
        },
    )
    credential_id = credential.id

    with open("datastore/vault_id.txt", "w") as f:
        f.write(vault_id)
    with open("datastore/credential_id.txt", "w") as f:
        f.write(credential_id)

print(f"Token stored in CMA vault for {mcp_server_url} MCP.")

wait_for_keypress()

print("Starting Agent Session now...\n")

IST            = timezone(timedelta(hours=5, minutes=30))
now_ist        = datetime.now(IST)
reminder_start = now_ist + timedelta(minutes=60)

prompt = (
    f"Current time in IST is {now_ist.isoformat()}. "
    "Fetch the single most recent unread email from Gmail (query: 'is:unread in:inbox'), "
    "summarize it in 2-3 sentences, then create a Google Calendar event with:\n"
    "  - Title: 'Action Required: <email subject>'\n"
    f"  - Start: {reminder_start.isoformat()}\n"
    "  - Duration: 30 minutes (use event_duration_minutes=30, do NOT pass end_datetime)\n"
    "  - Description: your 2-3 sentence email summary\n"
    "Report the email subject, your summary, and confirm the calendar event was created."
)

session = anthropic_client.beta.sessions.create(
    agent=agent_id,
    environment_id=os.environ["ANTHROPIC_ENVIRONMENT_ID"],
    vault_ids=[vault_id],
)

agent_response   = []
session_ended_ok = False

try:
    with anthropic_client.beta.sessions.events.stream(session_id=session.id) as stream:
        anthropic_client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
                        agent_response.append(block.text)

            elif event.type == "agent.mcp_tool_use":
                print(f"\n→ {event.name}", flush=True)

            elif event.type == "agent.mcp_tool_result":
                content = getattr(event, "content", None)
                if isinstance(content, list):
                    result_text = "".join(b.text if hasattr(b, "text") else str(b) for b in content)
                else:
                    result_text = str(content) if content else ""
                snippet = result_text[:200] + ("..." if len(result_text) > 200 else "")
                print(f"← {snippet}", flush=True)

            elif event.type == "session.requires_action":
                confirmations = [
                    {"type": "user.tool_confirmation", "tool_event_id": a.tool_event_id, "confirmed": True}
                    for a in event.required_actions
                    if hasattr(a, "tool_event_id")
                ]
                if confirmations:
                    anthropic_client.beta.sessions.events.send(session_id=session.id, events=confirmations)

            elif event.type in ("session.status_idle", "session.status_terminated"):
                session_ended_ok = event.type == "session.status_idle"
                print()
                break

except Exception as exc:
    print(f"\nStream error: {exc}")
    session_ended_ok = False

if session_ended_ok and agent_response:
    print("\n✓ Agent execution succeeded.")
else:
    print("\n✗ Agent execution failed.")

wait_for_keypress()

try:
    anthropic_client.beta.sessions.archive(session_id=session.id)
    print("Session successfully archived.")
except Exception as exc:
    print(f"Archive failed: {exc}")
