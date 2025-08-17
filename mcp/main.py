
import os
from dotenv import load_dotenv
import scalekit.client
from scalekit.connect.types import ToolMapping

load_dotenv()

scalekit_client = scalekit.client.ScalekitClient(

    os.getenv("SCALEKIT_ENV_URL"),
    os.getenv("SCALEKIT_CLIENT_ID"),
    os.getenv("SCALEKIT_CLIENT_SECRET")
)

def main():

    #create connected account for identifier default and connection name GMAIL,CALENDAR


    mcp_response = scalekit_client.connect.create_mcp(
        identifier = "default",
        tool_mappings = [
            ToolMapping(
                tool_names=["gmail_fetch_mails", "gmail_send_mails"],
                connection_name="GMAIL",
            ),
            ToolMapping(
                tool_names=["googlecalendar_list_events", "googlecalendar_create_event"],
                connection_name="CALENDAR",
            )
        ]
    )

    # Print the URL of the created MCP
    print("MCP created successfully:", mcp_response.url)



if __name__ == "__main__":
    main()

