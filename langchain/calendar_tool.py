from langchain.tools import tool
from scalekit_client import scalekit_client
from typing import Optional

@tool
def create_calendar_event(
    summary: str,
    start_datetime: str,
    event_duration_minutes: int = 30,
    identifier: str = "avinash.kamath@scalekit.com",
    calendar_id: str = "primary",
    description: str = "",
    location: str = "",
    attendees: str = "",
    timezone: str = "UTC",
    event_type: str = "default",
    visibility: str = "default",
    transparency: str = "opaque",
    recurrence: str = "",
    create_meeting_room: bool = False,
    guests_can_invite_others: bool = False,
    guests_can_modify: bool = False,
    guests_can_see_other_guests: bool = False,
    send_updates: bool = False
) -> str:
    """Create a Google Calendar event. The start_datetime must be in RFC3339 format.
    
    Examples of valid RFC3339 format:
    - "2025-08-06T17:00:00Z" (UTC time)
    - "2025-08-06T17:00:00-07:00" (with timezone offset)
    - "2025-08-06T17:00:00+05:30" (with timezone offset)
    
    Args:
        summary: Event title/summary
        start_datetime: Event start time in RFC3339 format (REQUIRED - must include timezone info)
        event_duration_minutes: Duration in minutes
        identifier: The user identifier for the scalekit connection
        calendar_id: Calendar to create event in
        description: Event description
        location: Event location  
        attendees: Comma-separated list of attendee emails
        timezone: Timezone for the event
        event_type: Type of event
        visibility: Event visibility
        transparency: Event transparency
        recurrence: Recurrence rule
        create_meeting_room: Whether to create a meeting room
        guests_can_invite_others: Whether guests can invite others
        guests_can_modify: Whether guests can modify the event
        guests_can_see_other_guests: Whether guests can see other guests
        send_updates: Whether to send update notifications
    
    Returns:
        Success message or error details
    """
    try:
        response = scalekit_client.connect.execute_tool(
            tool_name="googlecalendar_create_event",
            identifier=identifier,
            tool_input={
                "attendees": attendees,
                "calendar_id": calendar_id,
                "description": description,
                "event_duration_hour": "",
                "event_duration_minutes": event_duration_minutes,
                "event_type": event_type,
                "location": location,
                "recurrence": recurrence,
                "start_datetime": start_datetime,
                "summary": summary,
                "timezone": timezone,
                "transparency": transparency,
                "visibility": visibility,
                "create_meeting_room": create_meeting_room,
                "guests_can_invite_others": guests_can_invite_others,
                "guests_can_modify": guests_can_modify,
                "guests_can_see_other_guests": guests_can_see_other_guests,
                "schema_version": "1",
                "send_updates": send_updates,
                "tool_version": "1"
            }
        )
        print(response)
        return f"Calendar event '{summary}' created successfully"
    except Exception as e:
        return f"Error creating calendar event: {str(e)}"

# Export the tool for easy import
calendar_tool = create_calendar_event