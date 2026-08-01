
import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
connection_name = "multiheaderconnector"
identifier = "default"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit.actions


# 1. Create a connected account with static headers
connected_account = actions.create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details={
        "static_auth": {
            "X-Marketo-Client-Id": "Cli_!123",
            "X-Marketo-Client-Secret": "Sec.ABC@423",
            "X-Marketo-Munchkin-Id": "Munch123-4.13",
        }
    },
).connected_account

print(f"Connected account created: id={connected_account.id}, status={connected_account.status}")


# 2. Update the connected account with static headers
answer = input("\nWould you like to update the connected account? (y/n): ").strip().lower()
if answer == "y":
    connected_account = actions.update_connected_account(
        connection_name=connection_name,
        identifier=identifier,
        authorization_details={
            "static_auth": {
                "X-Marketo-Client-Id": "2Cli_!123",
                "X-Marketo-Client-Secret": "2Sec.ABC@423",
                "X-Marketo-Munchkin-Id": "2Munch123-4.13",
            }
        },
    ).connected_account

    print(f"Connected account updated: id={connected_account.id}, status={connected_account.status}")


# 3. Delete the connected account
answer = input("\nWould you like to now cleanup? (y/n): ").strip().lower()
if answer == "y":
    actions.delete_connected_account(
        connection_name=connection_name,
        identifier=identifier,
    )
    print("Connected account deleted.")
