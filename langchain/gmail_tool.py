from langchain.tools import tool
from typing import Optional
from scalekit_client import scalekit_client

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