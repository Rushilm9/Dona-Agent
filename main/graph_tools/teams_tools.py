# teams_tools.py

from graph_tools.graph_client import graph_get, graph_post
from langchain.tools import tool

# --------------------------------------------------
# Tool: List all Teams the user has joined
# --------------------------------------------------
@tool
def list_joined_teams() -> dict:
    """
    List all Microsoft Teams that the signed-in user has joined.

    Returns:
        dict: A list of joined Teams.
    """
    return graph_get("me/joinedTeams")

# --------------------------------------------------
# Tool: Join a Team using a join code
# --------------------------------------------------
@tool
def join_team(join_code: str) -> str:
    """
    Join a Microsoft Team using a provided join code.

    Args:
        join_code (str): The team code shared with the user.

    Returns:
        str: Status message indicating success or failure.
    """
    payload = {
        "classCode": join_code  # Microsoft Teams education use-case (e.g. class team)
    }

    response = graph_post("me/joinedTeams", payload)

    if response.status_code in (200, 204):
        return "✅ Successfully joined the team!"
    else:
        return f"❌ Failed to join team. Status Code: {response.status_code} - {response.text}"

# --------------------------------------------------
# Tool: Send a private 1:1 message to a user via chat
# --------------------------------------------------
@tool
def send_private_message_to_user(user_id: str, message: str) -> str:
    """
    Send a direct (1:1) message to a Microsoft Teams user.

    Args:
        user_id (str): User ID of the recipient.
        message (str): Message text content.

    Returns:
        str: Status message indicating result.
    """
    # Step 1: Create 1:1 chat if not already exists
    payload_create_chat = {
        "chatType": "oneOnOne",
        "members": [
            {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "roles": ["owner"],
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{user_id}')"
            }
        ]
    }

    create_chat_response = graph_post("chats", payload_create_chat)

    if create_chat_response.status_code not in (200, 201):
        return f"❌ Failed to create chat: {create_chat_response.text}"

    chat_id = create_chat_response.json().get("id")
    if not chat_id:
        return "❌ Chat ID not found after creation."

    # Step 2: Send message to the chat
    payload_send_message = {
        "body": {
            "content": message
        }
    }

    send_message_response = graph_post(f"chats/{chat_id}/messages", payload_send_message)

    if send_message_response.status_code == 201:
        return "✅ Private message sent successfully!"
    else:
        return f"❌ Failed to send private message. Status Code: {send_message_response.status_code} - {send_message_response.text}"

# --------------------------------------------------
# Export tools for use in agent or UI integration
# --------------------------------------------------
tools = [
    list_joined_teams,
    join_team,
    send_private_message_to_user
]
