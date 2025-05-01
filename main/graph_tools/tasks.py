# tasks.py

from graph_tools.graph_client import graph_get, graph_post, graph_delete
from graph_tools.utils import safe_parse_datetime
from langchain.tools import tool
from datetime import datetime
from typing import List, Dict

# -----------------------------------------------------
# Internal Utility: Fetch all task lists for the user
# -----------------------------------------------------
def get_all_task_lists() -> List[Dict]:
    """Fetch all Microsoft To-Do task lists for the user."""
    response = graph_get("me/todo/lists")
    return response.get('value', [])

# -----------------------------------------------------
# Internal Utility: Fetch all tasks from a given list
# -----------------------------------------------------
def get_tasks_in_list(list_id: str) -> List[Dict]:
    """Fetch all tasks inside a specific task list."""
    response = graph_get(f"me/todo/lists/{list_id}/tasks")
    return response.get('value', [])

# -----------------------------------------------------
# Tool: List all tasks across all task lists
# -----------------------------------------------------
@tool
def list_all_tasks_tool(input_text: str = "") -> dict:
    """
    List all tasks across all task lists.

    Returns:
        A dictionary with all task metadata.
    """
    all_tasks = []
    task_lists = get_all_task_lists()

    for task_list in task_lists:
        list_id = task_list['id']
        tasks = get_tasks_in_list(list_id)

        for task in tasks:
            all_tasks.append({
                "task_list_name": task_list.get("displayName"),
                "task_list_id": list_id,
                "task_id": task.get("id"),
                "title": task.get("title"),
                "status": task.get("status"),
                "due_date": task.get("dueDateTime", {}).get("dateTime")
            })

    return {"tasks": all_tasks}

# -----------------------------------------------------
# Tool: List tasks due today across all task lists
# -----------------------------------------------------
@tool
def list_tasks_today_tool(input_text: str = "") -> dict:
    """
    List tasks that are due today across all task lists.

    Returns:
        A dictionary of tasks due today.
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
                        "task_list_name": task_list.get("displayName"),
                        "task_list_id": list_id,
                        "task_id": task.get("id"),
                        "title": task.get("title"),
                        "status": task.get("status"),
                        "due_date": due_date_str
                    })

    return {"tasks_due_today": today_tasks}

# -----------------------------------------------------
# Tool: Create a new task (optional due date)
# -----------------------------------------------------
@tool
def create_task(task_list_id: str, task_title: str, due_datetime: str = None) -> str:
    """
    Create a new task in a specific task list.

    Args:
        task_list_id: The list in which the task should be created.
        task_title: The title of the task.
        due_datetime: Optional due date in ISO format.

    Returns:
        A status message.
    """
    payload = {"title": task_title}
    if due_datetime:
        payload["dueDateTime"] = {
            "dateTime": due_datetime,
            "timeZone": "UTC"
        }
    response = graph_post(f"me/todo/lists/{task_list_id}/tasks", payload)
    return f"Create Task Status: {response.status_code}"

# -----------------------------------------------------
# Tool: Delete a task by ID
# -----------------------------------------------------
@tool
def delete_task(task_list_id: str, task_id: str) -> str:
    """
    Delete a task from a specific task list.

    Args:
        task_list_id: ID of the task list.
        task_id: ID of the task to delete.

    Returns:
        A status message.
    """
    response = graph_delete(f"me/todo/lists/{task_list_id}/tasks/{task_id}")
    return f"Delete Task Status: {response.status_code}"

# -----------------------------------------------------
# Optional tools: List task lists or tasks in list
# (Commented out by default for clarity)
# -----------------------------------------------------
@tool
def list_task_lists(input_text: str = "") -> dict:
    """List all task lists."""
    task_lists = get_all_task_lists()
    return {"task_lists": task_lists}

@tool
def list_tasks_in_list_tool(task_list_id: str) -> dict:
    """List tasks in a specific task list."""
    tasks = get_tasks_in_list(task_list_id)
    return {"tasks": tasks}

# -----------------------------------------------------
# Exported tools for use in LangChain or FastAPI
# -----------------------------------------------------
tools = [
    # list_task_lists,
    # list_tasks_in_list_tool,
    list_all_tasks_tool,
    list_tasks_today_tool,
    create_task,
    delete_task
]
