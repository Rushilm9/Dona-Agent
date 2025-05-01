# graph_routes.py

from fastapi import APIRouter
from tasks import list_tasks_today_tool
from events import get_events
from models import TasksResponse, EventsResponse, AggregatedDataResponse

# -----------------------------------------------
# Setup FastAPI router with Microsoft Graph tag
# -----------------------------------------------
router = APIRouter(
    prefix="/graph",
    tags=["Microsoft Graph API"]
)

# -------------------------------------------------------
# Endpoint: GET /graph/tasks/today
# Description: Fetch today's tasks using Graph API
# -------------------------------------------------------
@router.get("/tasks/today", response_model=TasksResponse)
async def get_tasks_today():
    """
    Fetch tasks due today from Microsoft To-Do via Graph API.

    Returns:
        A list of task items due today.
    """
    tasks_data = list_tasks_today_tool()
    return TasksResponse(tasks=tasks_data.get("tasks_due_today", []))


# -------------------------------------------------------
# Endpoint: GET /graph/events
# Description: Fetch upcoming calendar events
# -------------------------------------------------------
@router.get("/events", response_model=EventsResponse)
async def get_upcoming_events():
    """
    Fetch upcoming calendar events for the user.

    Returns:
        A list of event objects.
    """
    events_data = get_events()
    return EventsResponse(events=events_data.get("value", []))


# ------------------------------------------------------------------
# Endpoint: GET /graph/aggregated
# Description: Combine tasks due today and calendar events together
# ------------------------------------------------------------------
@router.get("/aggregated", response_model=AggregatedDataResponse)
async def get_aggregated_graph_data():
    """
    Fetch both calendar events and today's tasks in one request.

    Returns:
        An aggregated response with tasks and events.
    """
    tasks_data = list_tasks_today_tool()
    events_data = get_events()

    return AggregatedDataResponse(
        tasks=TasksResponse(tasks=tasks_data.get("tasks_due_today", [])),
        events=EventsResponse(events=events_data.get("value", [])),
    )
