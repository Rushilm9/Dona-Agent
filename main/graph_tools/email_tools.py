# email_tools.py

from graph_tools.graph_client import graph_get, graph_post
from langchain.tools import tool
from typing import List, Dict

# --------------------------------------------------
# Tool: Retrieve a list of recent emails from inbox
# --------------------------------------------------
@tool
def list_emails(max_results: int = 10) -> dict:
    """
    List the most recent received emails from the user's inbox.

    Args:
        max_results (int): Number of emails to retrieve (default is 10).

    Returns:
        dict: A dictionary containing a list of recent emails.
    """
    # Microsoft Graph query: fetch emails ordered by most recent
    response = graph_get(f"me/mailFolders/Inbox/messages?$top={max_results}&$orderby=receivedDateTime DESC")
    emails = response.get('value', [])
    return {"emails": emails}


# ----------------------------------------------
# Tool: Send a new email using Microsoft Graph
# ----------------------------------------------
@tool
def send_email(recipient_email: str, subject: str, body: str) -> str:
    """
    Send an email to a specified recipient.

    Args:
        recipient_email (str): Email address of the recipient.
        subject (str): Subject of the email.
        body (str): Plain text body content of the email.

    Returns:
        str: Status message indicating success or failure.
    """
    # Construct payload in required Microsoft Graph format
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ]
        },
        "saveToSentItems": "true"
    }

    # Send email using POST request
    response = graph_post("me/sendMail", payload)

    # Handle response based on HTTP status
    if response.status_code == 202:
        return "✅ Email sent successfully!"
    else:
        return f"❌ Failed to send email. Status Code: {response.status_code} - {response.text}"


# ----------------------------------------------
# Export tools for use with LangChain or other agents
# ----------------------------------------------
tools = [
    list_emails,
    send_email
]
