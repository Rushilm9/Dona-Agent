# task_event_api.py

from fastapi import APIRouter
from typing import List
from datetime import datetime
from graph_tools.graph_client import graph_get
from graph_tools.utils import safe_parse_datetime

# Initialize FastAPI router
router = APIRouter()

# ---------------------------
# Helper Functions
# ---------------------------

def get_all_task_lists():
    """Fetch all Microsoft To-Do task lists."""
    response = graph_get("me/todo/lists")
    return response.get('value', [])

def get_tasks_in_list(list_id: str):
    """Fetch all tasks from a specific task list."""
    response = graph_get(f"me/todo/lists/{list_id}/tasks")
    return response.get('value', [])

# ---------------------------
# API Endpoints
# ---------------------------

@router.get("/tasks_today", summary="Get all tasks due today in JSON format")
async def get_tasks_due_today():
    """
    Return all tasks due today across all task lists.
    """
    today = datetime.utcnow().date()
    today_tasks = []

    task_lists = get_all_task_lists()
    for task_list in task_lists:
        list_id = task_list['id']
        tasks = get_tasks_in_list(list_id)
        for task in tasks:
            due_date_str = task.get('dueDateTime', {}).get('dateTime')
            if due_date_str:
                due_date = safe_parse_datetime(due_date_str).date()
                if due_date == today:
                    today_tasks.append({
                        "task_id": task.get("id"),
                        "task_title": task.get("title"),
                        "status": task.get("status"),
                        "due_date": due_date_str,
                        "task_list_id": list_id,
                        "task_list_name": task_list.get("displayName"),
                        "importance": task.get("importance", "normal"),
                        "is_reminder_on": task.get("reminderDateTime") is not None
                    })

    return {
        "tasks_due_today": today_tasks,
        "task_count": len(today_tasks),
        "date": today.isoformat()
    }

@router.get("/tasks_all", summary="Get all tasks across all task lists in JSON format")
async def get_all_tasks():
    """
    Return all tasks from all task lists.
    """
    all_tasks = []

    task_lists = get_all_task_lists()
    for task_list in task_lists:
        list_id = task_list['id']
        tasks = get_tasks_in_list(list_id)
        for task in tasks:
            all_tasks.append({
                "task_id": task.get("id"),
                "task_title": task.get("title"),
                "status": task.get("status"),
                "due_date": task.get("dueDateTime", {}).get("dateTime"),
                "task_list_id": list_id,
                "task_list_name": task_list.get("displayName"),
                "importance": task.get("importance", "normal"),
                "is_reminder_on": task.get("reminderDateTime") is not None
            })

    return {
        "all_tasks": all_tasks,
        "task_count": len(all_tasks)
    }

@router.get("/events_today", summary="Get all calendar events scheduled for today in JSON format")
async def get_events_today():
    """
    Return all calendar events that occur today.
    """
    today = datetime.utcnow().date()
    events_today = []

    # Fetch all events
    response = graph_get("me/events")
    events = response.get('value', [])

    for event in events:
        start_datetime_str = event.get('start', {}).get('dateTime')
        if start_datetime_str:
            event_date = safe_parse_datetime(start_datetime_str).date()
            if event_date == today:
                online_meeting_info = event.get('onlineMeeting')
                online_meeting_url = online_meeting_info.get('joinUrl') if online_meeting_info else None

                events_today.append({
                    "event_id": event.get("id"),
                    "subject": event.get("subject"),
                    "start_time": event.get('start', {}).get('dateTime'),
                    "end_time": event.get('end', {}).get('dateTime'),
                    "location": event.get('location', {}).get('displayName', ""),
                    "organizer": event.get('organizer', {}).get('emailAddress', {}).get('name', ""),
                    "organizer_email": event.get('organizer', {}).get('emailAddress', {}).get('address', ""),
                    "attendees": [
                        attendee.get('emailAddress', {}).get('address', '')
                        for attendee in event.get('attendees', [])
                    ],
                    "is_online_meeting": event.get('isOnlineMeeting', False),
                    "online_meeting_url": online_meeting_url
                })

    return {
        "events_today": events_today,
        "event_count": len(events_today),
        "date": today.isoformat()
    }

@router.get("/events_all", summary="Get all calendar events in JSON format")
async def get_all_events():
    """
    Return all calendar events from Microsoft Outlook.
    """
    events_list = []

    # Fetch all events
    response = graph_get("me/events")
    events = response.get('value', [])

    for event in events:
        start_datetime_str = event.get('start', {}).get('dateTime')
        end_datetime_str = event.get('end', {}).get('dateTime')

        online_meeting_info = event.get('onlineMeeting')
        online_meeting_url = online_meeting_info.get('joinUrl') if online_meeting_info else None

        events_list.append({
            "event_id": event.get("id"),
            "subject": event.get("subject"),
            "start_time": start_datetime_str,
            "end_time": end_datetime_str,
            "location": event.get('location', {}).get('displayName', ""),
            "organizer": event.get('organizer', {}).get('emailAddress', {}).get('name', ""),
            "organizer_email": event.get('organizer', {}).get('emailAddress', {}).get('address', ""),
            "attendees": [
                attendee.get('emailAddress', {}).get('address', '')
                for attendee in event.get('attendees', [])
            ],
            "is_online_meeting": event.get('isOnlineMeeting', False),
            "online_meeting_url": online_meeting_url
        })

    return {
        "all_events": events_list,
        "event_count": len(events_list)
    }
