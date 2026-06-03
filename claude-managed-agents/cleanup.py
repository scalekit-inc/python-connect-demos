import os
import sys
import tty
import termios
import anthropic
from dotenv import load_dotenv
from scalekit import ScalekitClient

load_dotenv()

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


def read(path):
    return open(path).read().strip() if os.path.exists(path) else None


config_id     = read("datastore/config_id.txt")
agent_id      = read("datastore/agent_id.txt")
vault_id      = read("datastore/vault_id.txt")
credential_id = read("datastore/credential_id.txt")

print("Cleanup summary:\n")
print(f"  MCP Config   : {config_id or '(not found)'}")
print(f"  Agent        : {agent_id or '(not found)'}")
print(f"  Vault        : {vault_id or '(not found)'}")
print(f"  Credential   : {credential_id or '(not found)'}")

wait_for_keypress()

if config_id:
    sk_client.actions.delete_config(config_id=config_id)
    print(f"✓ MCP config deleted   : {config_id}")
else:
    print("  MCP config skipped   : no config_id.txt")

if credential_id and vault_id:
    anthropic_client.beta.vaults.credentials.delete(credential_id, vault_id=vault_id)
    print(f"✓ Vault credential deleted : {credential_id}")
else:
    print("  Vault credential skipped : not found")

if vault_id:
    anthropic_client.beta.vaults.delete(vault_id)
    print(f"✓ Vault deleted        : {vault_id}")
else:
    print("  Vault skipped        : no vault_id.txt")

if agent_id:
    anthropic_client.beta.agents.archive(agent_id)
    print(f"✓ Agent archived       : {agent_id}")
else:
    print("  Agent skipped        : no agent_id.txt")

for fname in ("config_id.txt", "agent_id.txt", "vault_id.txt", "credential_id.txt", "identifier.txt"):
    path = f"datastore/{fname}"
    if os.path.exists(path):
        os.remove(path)

print("\nDatastore cleared.")
print("Cleanup complete.")
