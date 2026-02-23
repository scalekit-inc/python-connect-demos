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

# # Test Case 1: Comprehensive Recurring Meeting
# print("\n" + "=" * 80)
# print("TEST CASE 1: Comprehensive Recurring Meeting")
# print("=" * 80)
# print("Description: Weekly recurring meeting with all major fields")
# print("Expected: Recurring meeting every Monday from Feb 15 to May 31, 2026")
# print("Time: 2:30 PM - 4:00 PM IST, with Teams link, 30-min reminder")
# print("-" * 80)
#
# response1 = scalekit.connect.execute_tool(
#     tool_name="outlook_create_calendar_event",
#     identifier=IDENTIFIER,
#     tool_input={
#         "subject": "Quarterly Product Review Meeting",
#         "start_datetime": "2026-02-15T14:30:00",
#         "start_timezone": "Asia/Kolkata",
#         "end_datetime": "2026-02-15T16:00:00",
#         "end_timezone": "Asia/Kolkata",
#         "body_content": "<h2>Agenda</h2><ul><li>Q1 Performance Review</li><li>Product Roadmap Discussion</li><li>Budget Planning for Q2</li><li>Team Updates</li></ul><p>Please come prepared with your department reports.</p>",
#         "body_contentType": "HTML",
#         "location": "Conference Room 3A, Bangalore Office",
#         "attendees_required": "priya.sharma@example.com,raj.kumar@example.com,anil.mehta@example.com",
#         "attendees_optional": "sneha.patel@example.com,vikram.singh@example.com",
#         "attendees_resource": "conf-room-3a@example.com,projector-bangalore@example.com",
#         "hideAttendees": False,
#         "recurrence_type": "weekly",
#         "recurrence_interval": 1,
#         "recurrence_days_of_week": "monday",
#         "recurrence_range_type": "endDate",
#         "recurrence_start_date": "2026-02-15",
#         "recurrence_end_date": "2026-05-31",
#         "isReminderOn": True,
#         "reminderMinutesBeforeStart": 30,
#         "isOnlineMeeting": True,
#         "onlineMeetingProvider": "teamsForBusiness",
#         "importance": "high",
#         "sensitivity": "normal",
#         "showAs": "busy",
#         "isAllDay": False,
#     },
# )
#
# print("\n✓ Test Case 1 Response:")
# print(response1)
# print("\n" + "=" * 80)
# input("\nPress Enter to continue to Test Case 2...")
#
# # Test Case 2: Event with Multiple Locations
# print("\n" + "=" * 80)
# print("TEST CASE 2: Event with Multiple Locations")
# print("=" * 80)
# print("Description: One-time event with multiple physical locations")
# print("Expected: Single event on Oct 24, 2026 from 6:00 PM - 10:00 PM IST")
# print("Two locations with full address, 2-hour reminder, shows as 'free'")
# print("-" * 80)
#
# response2 = scalekit.connect.execute_tool(
#     tool_name="outlook_create_calendar_event",
#     identifier=IDENTIFIER,
#     tool_input={
#         "subject": "Team Diwali Celebration 2026",
#         "start_datetime": "2026-10-24T18:00:00",
#         "start_timezone": "Asia/Kolkata",
#         "end_datetime": "2026-10-24T22:00:00",
#         "end_timezone": "Asia/Kolkata",
#         "body_content": "Join us for our annual Diwali celebration! Dinner, games, and festivities. Dress code: Traditional attire encouraged.",
#         "body_contentType": "Text",
#         "locations": '[{"displayName":"Leela Palace Hotel","address":{"street":"23 HAL Old Airport Road","city":"Bengaluru","state":"Karnataka","countryOrRegion":"India","postalCode":"560008"},"coordinates":{"latitude":12.9716,"longitude":77.5946}},{"displayName":"Virtual Attendance Available"}]',
#         "attendees_required": "all-bangalore@example.com",
#         "isReminderOn": True,
#         "reminderMinutesBeforeStart": 120,
#         "isOnlineMeeting": False,
#         "importance": "high",
#         "sensitivity": "normal",
#         "showAs": "free",
#         "isAllDay": False,
#     },
# )
#
# print("\n✓ Test Case 2 Response:")
# print(response2)
# print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 3...")

# Test Case 3: Daily Recurring Standup
print("\n" + "=" * 80)
print("TEST CASE 3: Daily Recurring Standup")
print("=" * 80)
print("Description: Daily recurring meeting with limited occurrences")
print("Expected: Daily standup for 60 occurrences, 10:00-10:15 AM IST")
print("Teams meeting with 5-minute reminder")
print("-" * 80)

response3 = scalekit.connect.execute_tool(
    tool_name="outlook_create_calendar_event",
    identifier=IDENTIFIER,
    tool_input={
        "subject": "Daily Standup - Engineering Team",
        "start_datetime": "2026-01-28T10:00:00",
        "start_timezone": "Asia/Kolkata",
        "end_datetime": "2026-01-28T10:15:00",
        "end_timezone": "Asia/Kolkata",
        "body_content": "Daily standup meeting. What did you do yesterday? What will you do today? Any blockers?",
        "body_contentType": "Text",
        "location": "Online - Teams",
        "attendees_required": "dev-team@example.com",
        "recurrence_type": "daily",
        "recurrence_interval": 1,
        "recurrence_range_type": "numbered",
        "recurrence_start_date": "2026-01-28",
        "recurrence_occurrences": 60,
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 5,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "importance": "normal",
        "sensitivity": "normal",
        "showAs": "busy",
        "isAllDay": False,
    },
)

print("\n✓ Test Case 3 Response:")
print(response3)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 4...")

# Test Case 4: All-Day Event
print("\n" + "=" * 80)
print("TEST CASE 4: All-Day Event")
print("=" * 80)
print("Description: Simple all-day event for holidays")
print("Expected: All-day event on Jan 26, 2026, no reminder, shows as 'free'")
print("-" * 80)

response4 = scalekit.connect.execute_tool(
    tool_name="outlook_create_calendar_event",
    identifier=IDENTIFIER,
    tool_input={
        "subject": "Company Holiday - Republic Day",
        "start_datetime": "2026-01-26T00:00:00",
        "start_timezone": "Asia/Kolkata",
        "end_datetime": "2026-01-26T23:59:59",
        "end_timezone": "Asia/Kolkata",
        "body_content": "Office closed for Republic Day celebration. Enjoy the holiday!",
        "body_contentType": "Text",
        "isReminderOn": False,
        "importance": "normal",
        "sensitivity": "normal",
        "showAs": "free",
        "isAllDay": True,
    },
)

print("\n✓ Test Case 4 Response:")
print(response4)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 5...")

# Test Case 5: Confidential Meeting with Privacy
print("\n" + "=" * 80)
print("TEST CASE 5: Confidential Meeting with Privacy")
print("=" * 80)
print("Description: High-security board meeting with hidden attendees")
print("Expected: 3-hour meeting 9:00 AM - 12:00 PM IST, confidential sensitivity")
print("Attendees hidden from each other, 1-hour reminder")
print("-" * 80)

response5 = scalekit.connect.execute_tool(
    tool_name="outlook_create_calendar_event",
    identifier=IDENTIFIER,
    tool_input={
        "subject": "Confidential - Board Meeting",
        "start_datetime": "2026-02-01T09:00:00",
        "start_timezone": "Asia/Kolkata",
        "end_datetime": "2026-02-01T12:00:00",
        "end_timezone": "Asia/Kolkata",
        "body_content": "<p><strong>Confidential Discussion Topics:</strong></p><ul><li>Financial Results Q4</li><li>Strategic Acquisitions</li><li>Executive Compensation Review</li></ul><p><em>Please do not share meeting details.</em></p>",
        "body_contentType": "HTML",
        "location": "Executive Board Room",
        "attendees_required": "ceo@example.com,cfo@example.com,board-members@example.com",
        "hideAttendees": True,
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 60,
        "isOnlineMeeting": False,
        "importance": "high",
        "sensitivity": "confidential",
        "showAs": "busy",
        "isAllDay": False,
    },
)

print("\n✓ Test Case 5 Response:")
print(response5)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 6...")

# Test Case 6: Minimal Event (Only Required Fields)
print("\n" + "=" * 80)
print("TEST CASE 6: Minimal Event (Only Required Fields)")
print("=" * 80)
print("Description: Simplest possible event with only required fields")
print("Expected: 30-minute meeting 3:00-3:30 PM IST, default settings")
print("-" * 80)

response6 = scalekit.connect.execute_tool(
    tool_name="outlook_create_calendar_event",
    identifier=IDENTIFIER,
    tool_input={
        "subject": "Quick Sync",
        "start_datetime": "2026-01-29T15:00:00",
        "start_timezone": "Asia/Kolkata",
        "end_datetime": "2026-01-29T15:30:00",
        "end_timezone": "Asia/Kolkata",
    },
)

print("\n✓ Test Case 6 Response:")
print(response6)
print("\n" + "=" * 80)
input("\nPress Enter to continue to Test Case 7...")

# Test Case 7: Weekly Multi-Day Recurrence
print("\n" + "=" * 80)
print("TEST CASE 7: Weekly Multi-Day Recurrence")
print("=" * 80)
print("Description: Meeting that occurs on multiple days each week")
print("Expected: Recurs every Mon/Wed/Fri indefinitely, 4:00-5:00 PM IST")
print("Teams meeting, shows as 'tentative', never ends")
print("-" * 80)

response7 = scalekit.connect.execute_tool(
    tool_name="outlook_create_calendar_event",
    identifier=IDENTIFIER,
    tool_input={
        "subject": "Office Hours - Product Team",
        "start_datetime": "2026-02-02T16:00:00",
        "start_timezone": "Asia/Kolkata",
        "end_datetime": "2026-02-02T17:00:00",
        "end_timezone": "Asia/Kolkata",
        "body_content": "Open office hours for product questions and discussions.",
        "body_contentType": "Text",
        "location": "Online - Teams",
        "recurrence_type": "weekly",
        "recurrence_interval": 1,
        "recurrence_days_of_week": "monday,wednesday,friday",
        "recurrence_range_type": "noEnd",
        "recurrence_start_date": "2026-02-02",
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 15,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "importance": "normal",
        "sensitivity": "normal",
        "showAs": "tentative",
        "isAllDay": False,
    },
)

print("\n✓ Test Case 7 Response:")
print(response7)
print("\n" + "=" * 80)
print("\n🎉 All test cases completed!")
print("=" * 80)
