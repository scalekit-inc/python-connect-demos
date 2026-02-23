import scalekit.client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

scalekit = scalekit.client.ScalekitClient(
    client_id=os.getenv("SCALEKIT_CLIENT_ID"),
    client_secret=os.getenv("SCALEKIT_CLIENT_SECRET"),
    env_url=os.getenv("SCALEKIT_ENV_URL"),
)
connect = scalekit.connect

# Set identifier as a variable
IDENTIFIER = "venu-pro-account"

link_response = scalekit.connect.get_authorization_link(
    connection_name="OUTLOOK-TUHNCOGF",
    identifier=IDENTIFIER,
)
print("click on the link to authorize outlook", link_response.link)
input("Press Enter after authorizing outlook...")

print("\n" + "=" * 80)
print("OUTLOOK CALENDAR - LIST EVENTS TESTS")
print("=" * 80)
print("Testing outlook_list_calendar_events tool with various filters and options")
print("=" * 80)
input("\nPress Enter to continue to Test Case 1...")

# Test Case 1: Basic List with Pagination
print("\n" + "=" * 80)
print("TEST CASE 1: Basic List with Pagination")
print("=" * 80)
print("Description: List first 5 calendar events")
print(
    "Expected: Returns up to 5 events with all fields, includes nextLink for pagination"
)
print("-" * 80)

response1 = scalekit.connect.execute_tool(
    tool_name="outlook_list_calendar_events",
    identifier=IDENTIFIER,
    tool_input={"top": 5},
)

print("\n✓ Test Case 1 Response:")
print(response1)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 2...")

# Test Case 2: Filter and Select Specific Fields
print("\n" + "=" * 80)
print("TEST CASE 2: Filter and Select Specific Fields")
print("=" * 80)
print("Description: Select only key fields (subject, start, end, location)")
print("Expected: Returns events with only selected fields (smaller response)")
print("-" * 80)

response2 = scalekit.connect.execute_tool(
    tool_name="outlook_list_calendar_events",
    identifier=IDENTIFIER,
    tool_input={
        "select": "subject,start,end,location,organizer,id",
        "top": 10,
    },
)

print("\n✓ Test Case 2 Response:")
print(response2)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 3...")

# Test Case 3: Order By Start Time Descending
print("\n" + "=" * 80)
print("TEST CASE 3: Order By Start Time Descending")
print("=" * 80)
print("Description: List events ordered by start time (newest first)")
print("Expected: Events sorted with most recent at the top")
print("-" * 80)

response3 = scalekit.connect.execute_tool(
    tool_name="outlook_list_calendar_events",
    identifier=IDENTIFIER,
    tool_input={
        "orderby": "start/dateTime desc",
        "select": "subject,start,end,id",
        "top": 5,
    },
)

print("\n✓ Test Case 3 Response:")
print(response3)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 4...")

# Test Case 4: Filter Events Not Cancelled
print("\n" + "=" * 80)
print("TEST CASE 4: Filter Events Not Cancelled")
print("=" * 80)
print("Description: Filter to show only active (non-cancelled) events")
print("Expected: Returns only events where isCancelled is false")
print("-" * 80)

response4 = scalekit.connect.execute_tool(
    tool_name="outlook_list_calendar_events",
    identifier=IDENTIFIER,
    tool_input={
        "filter": "isCancelled eq false",
        "select": "subject,start,end,isCancelled,id",
        "top": 10,
    },
)

print("\n✓ Test Case 4 Response:")
print(response4)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 5...")

# Test Case 5: Pagination with Skip
print("\n" + "=" * 80)
print("TEST CASE 5: Pagination with Skip")
print("=" * 80)
print("Description: Get events 6-10 (skip first 5)")
print("Expected: Returns events starting from the 6th event")
print("-" * 80)

response5 = scalekit.connect.execute_tool(
    tool_name="outlook_list_calendar_events",
    identifier=IDENTIFIER,
    tool_input={
        "top": 5,
        "skip": 5,
        "select": "subject,start,end,id",
    },
)

print("\n✓ Test Case 5 Response:")
print(response5)
print("\n" + "=" * 80)
print("\n🎉 All list test cases completed!")
print("=" * 80)
