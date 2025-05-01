# calendar_tools.py

from graph_tools.graph_client import graph_get, graph_post, graph_delete, graph_patch
from graph_tools.utils import safe_parse_datetime
from langchain.tools import tool
from datetime import datetime, timedelta
from dateutil import parser
from zoneinfo import ZoneInfo  # Python 3.9+
from typing import List

# Default timezone setting
DEFAULT_TIMEZONE = "Asia/Kolkata"

# --------------------------------------
# Tool: Get all events on user's calendar
# --------------------------------------
@tool
def get_events() -> dict:
    """
    Fetch all upcoming events from the user's calendar.

    Returns:
        A dictionary of calendar events.
    """
    return graph_get("me/events")

# --------------------------------------
# Tool: Add new event with availability check
# --------------------------------------
@tool
def add_calendar_event_with_availability_check(
    subject: str,
    body_content: str,
    start_datetime: str,
    end_datetime: str,
    location: str = "",
    attendee_emails: list = [],
    timezone: str = DEFAULT_TIMEZONE
) -> str:
    """
    Create a calendar event only if the selected time slot is free.

    Args:
        subject: Event title.
        body_content: Description or agenda.
        start_datetime: ISO8601 format start time.
        end_datetime: ISO8601 format end time.
        location: Optional location.
        attendee_emails: Optional list of attendees.
        timezone: Time zone for the event.

    Returns:
        Status string.
    """
    # Fetch all existing events
    events_response = graph_get("me/events")
    existing_events = events_response.get('value', [])

    # Parse and localize input datetimes
    new_start = parser.isoparse(start_datetime)
    new_end = parser.isoparse(end_datetime)
    if new_start.tzinfo is None:
        new_start = new_start.replace(tzinfo=ZoneInfo(timezone))
    if new_end.tzinfo is None:
        new_end = new_end.replace(tzinfo=ZoneInfo(timezone))

    # Check for conflicts with existing events
    for event in existing_events:
        event_start = parser.isoparse(event['start']['dateTime'])
        event_end = parser.isoparse(event['end']['dateTime'])

        if event_start.tzinfo is None:
            event_start = event_start.replace(tzinfo=ZoneInfo(event['start'].get('timeZone', timezone)))
        if event_end.tzinfo is None:
            event_end = event_end.replace(tzinfo=ZoneInfo(event['end'].get('timeZone', timezone)))

        if (new_start < event_end) and (new_end > event_start):
            return f"❌ Cannot create event. Conflict with existing meeting from {event_start} to {event_end}."

    # If no conflicts, prepare payload
    payload = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": body_content
        },
        "start": {
            "dateTime": start_datetime,
            "timeZone": timezone
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": timezone
        }
    }

    if location:
        payload["location"] = {"displayName": location}

    if attendee_emails:
        payload["attendees"] = [
            {
                "emailAddress": {"address": email, "name": email.split('@')[0]},
                "type": "required"
            } for email in attendee_emails
        ]

    response = graph_post("me/events", payload)

    if response.status_code == 201:
        return "✅ Event created successfully!"
    else:
        return f"❌ Failed to create event. Status Code: {response.status_code} - {response.text}"

# --------------------------------------
# Tool: Delete a calendar event by ID
# --------------------------------------
@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Delete a calendar event.

    Args:
        event_id: ID of the event to delete.

    Returns:
        Status message.
    """
    response = graph_delete(f"me/events/{event_id}")
    if response.status_code == 204:
        return "✅ Event deleted successfully!"
    else:
        return f"❌ Failed to delete event. Status Code: {response.status_code} - {response.text}"

# --------------------------------------
# Tool: Update calendar event details
# --------------------------------------
@tool
def update_calendar_event(
    event_id: str,
    subject: str = None,
    body_content: str = None,
    start_datetime: str = None,
    end_datetime: str = None,
    location: str = None,
    attendee_emails: list = None,
    timezone: str = DEFAULT_TIMEZONE
) -> str:
    """
    Update fields in an existing calendar event.

    Args:
        event_id: ID of the event.
        subject, body_content, start/end datetime, location, attendee_emails: Optional updated fields.
        timezone: Time zone context.

    Returns:
        Status message.
    """
    payload = {}

    if subject:
        payload["subject"] = subject
    if body_content:
        payload["body"] = {"contentType": "HTML", "content": body_content}
    if start_datetime:
        payload.setdefault("start", {})["dateTime"] = start_datetime
        payload["start"]["timeZone"] = timezone
    if end_datetime:
        payload.setdefault("end", {})["dateTime"] = end_datetime
        payload["end"]["timeZone"] = timezone
    if location:
        payload["location"] = {"displayName": location}
    if attendee_emails is not None:
        payload["attendees"] = [
            {
                "emailAddress": {"address": email, "name": email.split('@')[0]},
                "type": "required"
            } for email in attendee_emails
        ]

    response = graph_patch(f"me/events/{event_id}", payload)

    if response.status_code == 200:
        return "✅ Event updated successfully!"
    else:
        return f"❌ Failed to update event. Status Code: {response.status_code} - {response.text}"

# --------------------------------------
# Tool: Suggest common meeting slots
# --------------------------------------
@tool
def find_available_meeting_times(
    attendee_emails: List[str],
    meeting_duration_minutes: int = 30,
    start_search_window: str = None,
    end_search_window: str = None,
    timezone: str = DEFAULT_TIMEZONE
) -> dict:
    """
    Suggest common meeting times for all attendees.

    Args:
        attendee_emails: List of required participants.
        meeting_duration_minutes: Desired meeting length.
        start_search_window: Start ISO time to look for availability.
        end_search_window: End ISO time to stop looking.
        timezone: Time zone.

    Returns:
        Dictionary with available slots or error message.
    """
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # Approximate IST
    if not start_search_window:
        start_search_window = now.isoformat()
    if not end_search_window:
        end_search_window = (now + timedelta(hours=24)).isoformat()

    payload = {
        "attendees": [
            {
                "type": "required",
                "emailAddress": {
                    "address": email,
                    "name": email.split('@')[0]
                }
            } for email in attendee_emails
        ],
        "timeConstraint": {
            "timeslots": [
                {
                    "start": {"dateTime": start_search_window, "timeZone": timezone},
                    "end": {"dateTime": end_search_window, "timeZone": timezone}
                }
            ]
        },
        "meetingDuration": f"PT{meeting_duration_minutes}M",
        "isOrganizerOptional": False,
        "returnSuggestionReasons": True,
        "minimumAttendeePercentage": 100
    }

    response = graph_post("me/findMeetingTimes", payload)

    if response.status_code == 200:
        suggestions = response.json().get('meetingTimeSuggestions', [])
        if not suggestions:
            return {"message": "❌ No available meeting times found."}
        else:
            available_slots = [
                {
                    "start": slot['meetingTimeSlot']['start']['dateTime'],
                    "end": slot['meetingTimeSlot']['end']['dateTime'],
                    "confidence": slot.get('confidence', 0)
                }
                for slot in suggestions
            ]
            return {"available_slots": available_slots}
    else:
        return {"error": f"Failed to find meeting times. Status Code: {response.status_code} - {response.text}"}

# --------------------------------------
# Exported tools for use in the assistant
# --------------------------------------
tools = [
    add_calendar_event_with_availability_check,
    get_events,
    delete_calendar_event,
    update_calendar_event,
    find_available_meeting_times
]
