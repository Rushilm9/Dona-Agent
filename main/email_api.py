# email_team_api.py

from fastapi import APIRouter
from graph_tools.graph_client import graph_get, graph_post
from typing import List

# Initialize API router
router = APIRouter()

# ---------------------------------------------------------------------
# Endpoint: /emails
# Description: Get recent emails from the signed-in user's inbox
# ---------------------------------------------------------------------
@router.get("/emails", summary="Get recent emails in JSON format")
async def get_recent_emails(max_results: int = 12):
    """
    Fetch recent emails from Microsoft Outlook inbox using Microsoft Graph.

    Args:
        max_results (int): Number of emails to retrieve (default 12).

    Returns:
        dict: List of formatted email metadata and count.
    """
    response = graph_get(f"me/mailFolders/Inbox/messages?$top={max_results}&$orderby=receivedDateTime DESC")
    emails = response.get('value', [])

    email_list = []
    for email in emails:
        email_list.append({
            "email_id": email.get("id"),
            "subject": email.get("subject"),
            "sender_name": email.get("from", {}).get("emailAddress", {}).get("name", ""),
            "sender_email": email.get("from", {}).get("emailAddress", {}).get("address", ""),
            "received_datetime": email.get("receivedDateTime"),
            "body_preview": email.get("bodyPreview"),
            "is_read": email.get("isRead", False)
        })

    return {
        "emails": email_list,
        "email_count": len(email_list)
    }

# ---------------------------------------------------------------------
# Endpoint: /teams_messages
# Description: Get 1:1 Teams messages from recent chats
# ---------------------------------------------------------------------
@router.get("/teams_messages", summary="List recent Teams chat messages (1:1)")
async def list_recent_teams_messages():
    """
    Retrieve chat messages from recent 1:1 Microsoft Teams conversations.

    Returns:
        dict: List of chat messages across direct chats and message count.
    """
    response = graph_get("me/chats?$filter=chatType eq 'oneOnOne'")
    chats = response.get('value', [])

    messages_list = []

    for chat in chats:
        chat_id = chat.get('id')
        if not chat_id:
            continue

        # Fetch messages from each 1:1 chat
        chat_messages_response = graph_get(f"chats/{chat_id}/messages")
        messages = chat_messages_response.get('value', [])

        for message in messages:
            messages_list.append({
                "chat_id": chat_id,
                "message_id": message.get('id'),
                "from_user": message.get('from', {}).get('user', {}).get('displayName', ""),
                "from_user_id": message.get('from', {}).get('user', {}).get('id', ""),
                "created_datetime": message.get('createdDateTime'),
                "message_content": message.get('body', {}).get('content', "")
            })

    return {
        "teams_messages": messages_list,
        "message_count": len(messages_list)
    }
