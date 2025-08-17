from langchain.tools import tool
from datetime import datetime, timezone
import pytz

@tool
def get_current_datetime(timezone_name: str = "UTC") -> str:
    """Get the current date and time in RFC3339 format for the specified timezone.
    
    This tool provides the current datetime which is essential for scheduling events
    and understanding relative time references like 'tomorrow', 'next week', etc.
    
    Args:
        timezone_name: Timezone name (e.g., "UTC", "US/Pacific", "US/Eastern", "Asia/Kolkata", "Europe/London")
    
    Returns:
        Current date and time in RFC3339 format (e.g., "2025-08-12T14:30:00Z" or "2025-08-12T14:30:00-07:00")
    """
    try:
        if timezone_name == "UTC":
            current_time = datetime.now(timezone.utc)
            return current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            tz = pytz.timezone(timezone_name)
            current_time = datetime.now(tz)
            return current_time.strftime("%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        # Fallback to UTC if timezone is invalid
        current_time = datetime.now(timezone.utc)
        return f"{current_time.strftime('%Y-%m-%dT%H:%M:%SZ')} (Note: Invalid timezone '{timezone_name}', showing UTC)"

@tool 
def convert_datetime_to_rfc3339(date_str: str, time_str: str = "10:00", timezone_name: str = "UTC") -> str:
    """Convert a human-readable date and time to RFC3339 format.
    
    This tool helps convert relative dates like 'tomorrow', 'next Monday' or absolute dates
    like '2025-08-15' into the proper RFC3339 format needed for calendar events.
    
    Args:
        date_str: Date in various formats (e.g., "2025-08-15", "tomorrow", "next Monday")  
        time_str: Time in HH:MM format (default: "10:00")
        timezone_name: Timezone name (e.g., "UTC", "US/Pacific", "US/Eastern", "Asia/Kolkata")
    
    Returns:
        Date and time in RFC3339 format
    """
    try:
        current_time = datetime.now(timezone.utc)
        
        # Handle relative dates
        if date_str.lower() == "today":
            target_date = current_time.date()
        elif date_str.lower() == "tomorrow":
            from datetime import timedelta
            target_date = (current_time + timedelta(days=1)).date()
        else:
            # Try to parse as absolute date
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Parse time
        time_parts = time_str.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Create datetime object
        if timezone_name == "UTC":
            dt = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            tz = pytz.timezone(timezone_name)
            dt = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
            dt = tz.localize(dt)
            return dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            
    except Exception as e:
        return f"Error converting datetime: {str(e)}"

# Export the tools for easy import
datetime_tool = get_current_datetime
datetime_converter_tool = convert_datetime_to_rfc3339