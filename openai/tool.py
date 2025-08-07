import json

# OpenAI Tool Specifications for ScaleKit Integration

# Tool specification for fetching Gmail emails
GMAIL_FETCH_MAILS = {
    "type": "function",
    "name": "GMAIL_FETCH_MAILS",
        "description": "Retrieve emails from Gmail inbox with detailed information including sender, subject, date, and content. Requires an active Gmail connection through Google OAuth.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of emails to retrieve (default: 10, max: 50)",
                    "minimum": 1,
                    "maximum": 50
                },
                "query": {
                    "type": "string",
                    "description": "Gmail search query to filter emails (e.g., 'is:unread', 'from:example@email.com', 'subject:important')"
                }
            },
            "required": [],
            "additionalProperties": False
        }
}


SLACK_SEND_MESSAGE = {
        "type": "function",
        "name": "SLACK_SEND_MESSAGE",
        "description": "Send a message to a Slack channel or direct message to a user. Requires an active Slack connection with appropriate permissions.",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "The channel ID, channel name (with #), or user ID/@username to send the message to"
                },
                "text": {
                    "type": "string",
                    "description": "The message content to send"
                },
            },
            "required": ["channel", "text"],
            "additionalProperties": False
        }
}


# Export all tools for easy import
ALL_TOOLS = [
    GMAIL_FETCH_MAILS,
    SLACK_SEND_MESSAGE
]
