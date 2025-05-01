# contacts_helper.py

from graph_tools.graph_client import graph_get, graph_post

# ----------------------------------------------------
# Function: Add a new contact using Microsoft Graph API
# ----------------------------------------------------
def add_contact(contact_details: dict) -> str:
    """
    Add a new contact to the user's Microsoft 365 contact list.

    Args:
        contact_details (dict): Should include fields like displayName, emailAddresses, businessPhones, etc.

    Returns:
        str: Success or failure message based on response status.
    """
    response = graph_post("me/contacts", contact_details)

    if response.status_code == 201:
        return "✅ Contact added successfully!"
    else:
        return f"❌ Failed to add contact. Status Code: {response.status_code} - {response.text}"

# ----------------------------------------------------
# Function: Fetch all contacts for the signed-in user
# ----------------------------------------------------
def get_contacts() -> dict:
    """
    Retrieve all contacts from the signed-in user's Microsoft 365 account.

    Returns:
        dict: Raw response data from Graph API (typically includes 'value' key with contacts).
    """
    return graph_get("me/contacts")
