import scalekit.client, os
from dotenv import load_dotenv
load_dotenv()
connection_name = "gmail"
identifier = "sdk_test_user_001"

# Get your credentials from app.scalekit.com → Developers → Settings → API Credentials
scalekit_client = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
actions = scalekit_client.actions

# Authenticate the user
link_response = actions.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier
)
# present this link to your user for authorization, or click it yourself for testing
print("🔗 Authorize Gmail:", link_response.link)
input("Press Enter after authorizing Gmail...")

# Make a request via Scalekit proxy
result = actions.request(
    connection_name=connection_name,
    identifier=identifier,
    path="/v1/users/me/profile",
    method="GET"
)

print(result)