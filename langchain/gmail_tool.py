import scalekit.client
from langchain.tools import tool
from typing import Optional

# Initialize scalekit client
scalekit_client = scalekit.client.ScalekitClient(
    client_id="skc_53814741268693059",
    client_secret="test_ZBeqNRT3fQjTfGzFmFObkTDMlMbndBjZ3jOBADvd5OONZFBWzeOBmXiWwjlGLqCu",
    env_url="https://kindle-dev.scalekit.cloud",
)

@tool
def fetch_gmail_emails(max_results: int = 10, identifier: str = "avinash.kamath@scalekit.com") -> str:
    """
    Fetch Gmail emails using Scalekit API.
    
    Args:
        max_results: Maximum number of emails to fetch (default: 10)
        identifier: The user identifier for the scalekit connection (default: default)
    
    Returns:
        The fetched emails from Gmail
    """
    try:
        response = scalekit_client.connect.execute_tool(
            tool_name="GMAIL.FETCH_MAILS",
            identifier=identifier,
            tool_input={
                "max_results": max_results,
            },
        )
        return response
    except Exception as e:
        return f"Error fetching emails: {str(e)}"

# Export the tool for easy import
gmail_tool = fetch_gmail_emails