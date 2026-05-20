import scalekit.client
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET"),
)
connect = scalekit.connect

connection_name = "atlassianmcp"
identifier = "your_atlassian_user"

# Step 1 — authorize the connection
link_response = connect.get_authorization_link(
    connection_name=connection_name,
    identifier=identifier,
)

print("Click the link to authorize Atlassian Rovo MCP:", link_response.link)
input("Press Enter after authorizing...")

# Step 2 — get accessible Atlassian resources to retrieve the cloudId
#
# Most Atlassian Rovo MCP tools require a `cloudId` — the UUID that identifies
# your Atlassian cloud site. Call this tool once and use the `id` field from
# the response as the `cloudId` input in all subsequent tool calls.
response = connect.execute_tool(
    tool_name="atlassianmcp_getaccessibleatlassianresources",
    identifier=identifier,
    tool_input={},
)

resources = json.loads(response.data["content"][0]["text"])

print("\nAccessible Atlassian resources:")
for resource in resources:
    print(f"  id   : {resource['id']}")
    print(f"  name : {resource['name']}")
    print(f"  url  : {resource['url']}")
    print()

# Use the first site's id as cloudId in subsequent calls
cloud_id = resources[0]["id"]
print(f"cloudId to use in subsequent tool calls: {cloud_id}")
