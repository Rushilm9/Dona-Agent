# models.py

from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------
# Shared Model: Aggregated data structure for APIs
# ---------------------------------------------------
class AggregatedDataResponse(BaseModel):
    tasks: Dict[str, List[Dict]]
    events: Dict[str, List[Dict]]
    # Uncomment below to extend with additional data
    # contacts: Optional[Dict[str, List[Dict]]] = None
    # files: Optional[Dict[str, List[Dict]]] = None

# ---------------------------------------------------
# For LLM Interaction with API Endpoint (/ask)
# ---------------------------------------------------
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    question: str
    tool_used: str
    response: str
    human_feedback: str

# ---------------------------------------------------
# For internal use with LangChain agent results
# ---------------------------------------------------
class AgentResult(BaseModel):
    output: str
    tool_used: Optional[str] = "unknown"

# ---------------------------------------------------
# Output schema for structured event extraction
# ---------------------------------------------------
class EventSlots(BaseModel):
    intent: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    missing_fields: Optional[List[str]] = None

# ---------------------------------------------------
# Models for Tasks & Events (for API Responses)
# ---------------------------------------------------
class TaskItem(BaseModel):
    task_list_name: str
    task_list_id: str
    task_id: str
    title: str
    status: str
    due_date: str

class TaskListItem(BaseModel):
    id: str
    displayName: str

class EventItem(BaseModel):
    id: str
    subject: str
    start: Dict
    end: Dict
    location: Optional[Dict] = None

# ---------------------------------------------------
# Wrapper Models for Response Bodies
# ---------------------------------------------------
class TasksTodayResponse(BaseModel):
    tasks_due_today: List[TaskItem]

class TaskListsResponse(BaseModel):
    task_lists: List[TaskListItem]

class EventsResponse(BaseModel):
    events: List[EventItem]
