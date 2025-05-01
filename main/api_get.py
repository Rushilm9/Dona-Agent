# aggregated_data_router.py

from fastapi import APIRouter
from models import AggregatedDataResponse
from graph_tools_main import list_all_tasks_tool, get_events  # Import tools

# Initialize FastAPI router
router = APIRouter()

# ----------------------------------------------------------------
# Endpoint: GET /aggregated-data
# Description: Fetch tasks and calendar events in a single call
# ----------------------------------------------------------------
@router.get("/aggregated-data", response_model=AggregatedDataResponse)
async def get_aggregated_data():
    """
    Aggregate task and event data from Microsoft Graph.

    Returns:
        AggregatedDataResponse: Combined data with:
        - All tasks from To-Do lists
        - All upcoming calendar events
    """
    # Fetch from LangChain tools (sync invoke on async route is acceptable for small use cases)
    tasks_data = list_all_tasks_tool.invoke({})  # ✅ Get all tasks
    events_data = get_events.invoke({})          # ✅ Get calendar events

    # Optional: Extend with contacts or drive files later
    # contacts_data = get_contacts.invoke({})
    # files_data = list_drive_files.invoke({})

    # Return merged response model
    return AggregatedDataResponse(
        tasks={"tasks": tasks_data.get("tasks", [])},
        events={"events": events_data.get("value", [])}
        # contacts={"contacts": contacts_data.get("value", [])},
        # files={"files": files_data.get("value", [])}
    )
