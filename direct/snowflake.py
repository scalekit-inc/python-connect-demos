import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

snowflake_connection="snowflake-oYGZ7pWJ"
snowflake_identifier="teat-12321"


scalekit = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET")
)
actions = scalekit.actions


link_response = actions.get_authorization_link(
    connection_name=snowflake_connection,
    identifier=snowflake_identifier)

print("click on the link to authorize snowflake", link_response.link)
input("Press Enter after authorizing snowflake...")


response = actions.get_connected_account(
    connection_name=snowflake_connection,
    identifier=snowflake_identifier
)

connected_account = response.connected_account

tokens = connected_account.authorization_details["oauth_token"]
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

print("access token:",access_token)
print("refresh token:",refresh_token)


