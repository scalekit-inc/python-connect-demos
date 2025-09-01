
import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
connection_name = "freshdesk"
identifier = "default"


scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect



connected_account = connect.get_or_create_connected_account(
    connection_name=connection_name,
    identifier=identifier,
    authorization_details= {
        "static_auth": {
            "domain": "avinashmkamath.freshdesk.com",
            "password": "ikipj7k9UJJWRXZganAk",
            "username": "ikipj7k9UJJWRXZganAk"
        }
    }

).connected_account


response = scalekit.connect.execute_tool(
    tool_name="freshdesk_create_ticket",
    identifier=identifier,
    tool_input={

            "name": "Create Support Ticket from Example",
            "email": "john.doe@example.com",
            "subject": "This is a test ticket",
            "description": "<div>Hi,<br><br>this is a support ticket create from SDK<br><br>Thanks,<br>John</div>",
            "type": "Problem",
            "cc_emails": [
                "manager@example.com",
                "support-backup@example.com"
            ],
            "tags": [
                "login-issue",
                "password-reset",
                "urgent"
            ]
    },
)

print(response)