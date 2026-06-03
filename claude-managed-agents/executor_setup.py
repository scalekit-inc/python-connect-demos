import os
import sys
import tty
import termios
import uuid
from dotenv import load_dotenv
from scalekit import ScalekitClient

load_dotenv()

os.makedirs("datastore", exist_ok=True)

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


if not os.path.exists("datastore/config_id.txt"):
    print("ERROR: config_id.txt not found. Run builder.py first.")
    sys.exit(1)

config_id = open("datastore/config_id.txt").read().strip()
identifier = str(uuid.uuid4())

with open("datastore/identifier.txt", "w") as f:
    f.write(identifier)

print("End-user setup flow")
print("This is a one-time step — analogous to an Integrations screen in a web app.")
print("The end-user connects their accounts once, and all future agent sessions use those connections.\n")
print(f"  Config ID  : {config_id}")
print(f"  Identifier : {identifier}\n")

accounts_response = sk_client.actions.mcp.list_mcp_connected_accounts(
    config_id=config_id,
    identifier=identifier,
    include_auth_link=True,
)

for account in accounts_response.connected_accounts:
    print(f"  Connection : {account.connection_name}")
    print(f"  Account ID : {account.connected_account_id or '(none yet)'}")
    print(f"  Status     : {account.connected_account_status}")
    print(f"  Auth Link  : {account.authentication_link}")
    print()

print("Click each link above to complete authorization, then come back here.")

wait_for_keypress()

accounts_response = sk_client.actions.mcp.list_mcp_connected_accounts(
    config_id=config_id,
    identifier=identifier,
    include_auth_link=False,
)

print("Connected account status:\n")
for account in accounts_response.connected_accounts:
    is_active = account.connected_account_status.lower() == "active"
    mark = "✓" if is_active else "✗"
    print(f"  {mark} {account.connection_name} — {account.connected_account_status}")
