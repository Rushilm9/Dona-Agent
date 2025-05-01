# presence_tools.py

from graph_tools.graph_client import graph_get, graph_post
from langchain.tools import tool
import os

# ---------------------------------------------
# CLIENT_ID is required as sessionId in payload
# ---------------------------------------------
CLIENT_ID = os.getenv("CLIENT_ID")

# ----------------------------------------------------------
# Tool: Get current presence (status + activity) of the user
# ----------------------------------------------------------
@tool
def get_user_presence() -> dict:
    """
    Fetch the signed-in user's presence info.

    Returns:
        dict: Includes availability (e.g. 'Available', 'Busy') and activity (e.g. 'InACall', 'Away').
    """
    return graph_get("me/presence")

# ----------------------------------------------------------
# Tool: Set custom presence with expiration time
# ----------------------------------------------------------
@tool
def set_user_presence(activity: str, availability: str, expiration_minutes: int = 60) -> str:
    """
    Set the user's custom presence (activity + availability) temporarily.

    Args:
        activity (str): Activity like 'InAMeeting', 'Away', etc.
        availability (str): Availability like 'Available', 'DoNotDisturb', etc.
        expiration_minutes (int): Duration in minutes before it expires.

    Returns:
        str: Status message indicating success or failure.
    """
    if not CLIENT_ID:
        return "❌ CLIENT_ID not found. Please check your environment variables."

    payload = {
        "sessionId": CLIENT_ID,  # Azure requires this to track session presence
        "availability": availability,
        "activity": activity,
        "expirationDuration": f"PT{expiration_minutes}M"  # ISO8601 format
    }

    response = graph_post("me/presence/setPresence", payload)

    if response.status_code in (200, 202):
        return "✅ Presence updated successfully!"
    else:
        return f"❌ Failed to update presence. Status Code: {response.status_code} - {response.text}"

# ------------------------------------------
# Export presence tools for agent inclusion
# ------------------------------------------
tools = [
    get_user_presence,
    set_user_presence
]
