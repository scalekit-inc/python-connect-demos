from langchain.tools import tool
from scalekit_client import scalekit_client

@tool
def send_slack_message(channel: str, text: str, identifier: str = "avinash.kamath@scalekit.com") -> str:
    """
    Send a message to a Slack channel or direct message to a user.
    
    Args:
        channel: The channel ID, channel name (with #), or user ID/@username to send the message to
        text: The message content to send
        identifier: The user identifier for the scalekit connection (default: avinash.kamath@scalekit.com)
    
    Returns:
        The response from the Slack API
    """
    try:
        response = scalekit_client.connect.execute_tool(
            tool_name="slack_send_message",
            identifier=identifier,
            tool_input={
                "channel": channel,
                "text": text,
            },
        )
        return f"Message sent successfully to {channel}: {text}"
    except Exception as e:
        return f"Error sending message: {str(e)}"

# Export the tool for easy import
slack_tool = send_slack_message 