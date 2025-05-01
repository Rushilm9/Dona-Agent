# graph_tools.py

# -------------------------------
# Imports and Environment Config
# -------------------------------
import os
import sys
import json
import requests
from dotenv import load_dotenv
from langchain.tools import tool
import msal
from typing import List, Dict
from msal_extensions import *
from datetime import datetime

# Load environment variables
load_dotenv()

# Microsoft Graph API Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
USERNAME = os.getenv("USERNAME")
GRAPH_SCOPE = [
    "User.Read", "User.ReadWrite", "Group.Read.All", "Group.ReadWrite.All",
    "Mail.ReadWrite", "Calendars.ReadWrite", "Contacts.ReadWrite", 
    "Files.ReadWrite", "Team.ReadBasic.All", "Notes.ReadWrite", "Tasks.ReadWrite", 
    "People.Read", "Presence.Read", "Notifications.ReadWrite.CreatedByApp",
    "DeviceManagementApps.ReadWrite.All", "EduAdministration.ReadWrite", 
    "Bookings.ReadWrite.All", "Reports.Read.All", "SecurityEvents.Read.All"
]
GRAPH_API = "https://graph.microsoft.com/v1.0"

# ------------------------------------
# Utility: Safely parse datetime values
# ------------------------------------
def safe_parse_datetime(date_str: str) -> datetime:
    if '.' in date_str:
        date_part, fractional = date_str.split('.')
        fractional = fractional[:6]  # Limit to microseconds
        date_str = f"{date_part}.{fractional}"
    return datetime.fromisoformat(date_str)

# ----------------------------------------
# Token management using MSAL + persistence
# ----------------------------------------
def msal_persistence(location: str):
    if sys.platform.startswith('win'):
        return FilePersistenceWithDataProtection(location)
    elif sys.platform.startswith('darwin'):
        return KeychainPersistence(location, "service", "account")
    else:
        return FilePersistence(location)

def get_token() -> str:
    persistence = msal_persistence("token_cache.bin")
    cache = PersistedTokenCache(persistence)

    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )

    accounts = app.get_accounts(username=USERNAME)

    if accounts:
        result = app.acquire_token_silent(GRAPH_SCOPE, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    flow = app.initiate_device_flow(scopes=GRAPH_SCOPE)
    if "user_code" not in flow:
        raise ValueError("Device flow failed. Could not retrieve user code.")

    print("\n🔵 Microsoft Login Required:")
    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise ValueError("Authentication failed.")

# ---------------------------
# Microsoft Graph API methods
# ---------------------------
def graph_get(endpoint: str) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GRAPH_API}/{endpoint}", headers=headers)
    return response.json()

def graph_post(endpoint: str, payload: dict) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.post(f"{GRAPH_API}/{endpoint}", headers=headers, json=payload)

def graph_patch(endpoint: str, payload: dict) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.patch(f"{GRAPH_API}/{endpoint}", headers=headers, json=payload)

def graph_delete(endpoint: str) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{GRAPH_API}/{endpoint}", headers=headers)

def graph_put(endpoint: str, payload: str) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "text/plain"}
    return requests.put(f"{GRAPH_API}/{endpoint}", headers=headers, data=payload)

# ---------------------------------------------------
# Tools: Users, Groups, Email, Calendar, Contacts, etc.
# ---------------------------------------------------
@tool
def get_user_profile() -> dict:
    return graph_get("me")

@tool
def list_all_users() -> dict:
    return graph_get("users")

@tool
def create_user(user_details: dict) -> str:
    response = graph_post("users", user_details)
    return f"Create User Status: {response.status_code}"

@tool
def delete_user(user_id: str) -> str:
    response = graph_delete(f"users/{user_id}")
    return f"Delete User Status: {response.status_code}"

@tool
def update_user_display_name(user_id: str, new_display_name: str) -> str:
    payload = {"displayName": new_display_name}
    response = graph_patch(f"users/{user_id}", payload)
    return f"Update User Status: {response.status_code}"

@tool
def list_groups() -> dict:
    return graph_get("groups")

@tool
def create_group(display_name: str, description: str) -> str:
    payload = {
        "displayName": display_name,
        "description": description,
        "groupTypes": ["Unified"],
        "mailEnabled": True,
        "securityEnabled": False
    }
    response = graph_post("groups", payload)
    return f"Create Group Status: {response.status_code}"

@tool
def delete_group(group_id: str) -> str:
    response = graph_delete(f"groups/{group_id}")
    return f"Delete Group Status: {response.status_code}"

@tool
def send_mail(subject: str, body: str, email: str) -> str:
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": email}}]
        }
    }
    response = graph_post("me/sendMail", payload)
    return f"Mail Sent Status: {response.status_code}"

@tool
def get_events() -> dict:
    return graph_get("me/events")

@tool
def add_calendar_event(subject: str, body_content: str, start_datetime: str, end_datetime: str, location: str = "", attendee_emails: list = [], timezone: str = "UTC") -> str:
    payload = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": body_content},
        "start": {"dateTime": start_datetime, "timeZone": timezone},
        "end": {"dateTime": end_datetime, "timeZone": timezone}
    }

    if location:
        payload["location"] = {"displayName": location}

    if attendee_emails:
        payload["attendees"] = [
            {"emailAddress": {"address": email, "name": email.split('@')[0]}, "type": "required"}
            for email in attendee_emails
        ]

    response = graph_post("me/events", payload)
    return "✅ Event created successfully!" if response.status_code == 201 else f"❌ Failed: {response.status_code}"

@tool
def get_contacts() -> dict:
    return graph_get("me/contacts")

@tool
def list_drive_files() -> dict:
    return graph_get("me/drive/root/children")

@tool
def upload_file_to_onedrive(filename: str, content: str) -> str:
    response = graph_put(f"me/drive/root:/{filename}:/content", content)
    return f"Upload File Status: {response.status_code}"

@tool
def delete_file(file_id: str) -> str:
    response = graph_delete(f"me/drive/items/{file_id}")
    return f"Delete File Status: {response.status_code}"

@tool
def list_joined_teams() -> dict:
    return graph_get("me/joinedTeams")

@tool
def list_onenote_notebooks() -> dict:
    return graph_get("me/onenote/notebooks")

# Additional tools and task-related helpers are defined in continuation (not shown here to limit length).
# Would you like me to continue commenting and structuring the remaining sections (tasks, presence, reports, etc.)?