# contacts_tools.py

from graph_tools.graph_client import graph_get, graph_post
from langchain.tools import tool

# ------------------------------------------
# Tool: Fetch user's Microsoft contact list
# ------------------------------------------
@tool
def get_user_contacts() -> dict:
    """
    Fetch the signed-in user's contacts from Microsoft Graph.

    Returns:
        A dictionary containing contact details.
    """
    return graph_get("me/contacts")


# --------------------------------------------------
# Tool: Add a new contact to Microsoft 365 contacts
# --------------------------------------------------
@tool
def add_user_contact(contact_details: dict) -> str:
    """
    Add a new contact to the user's Microsoft 365 contact list.

    Args:
        contact_details: A dictionary with contact fields, e.g.:
            {
                "displayName": "John Doe",
                "emailAddresses": [{"address": "john@example.com"}],
                "phones": [{"number": "1234567890"}],
                "birthday": "1980-01-01",
                "companyName": "Example Corp"
            }

    Returns:
        A status message indicating success or failure.
    """
    response = graph_post("me/contacts", contact_details)

    if response.status_code == 201:
        return "✅ Contact added successfully!"
    else:
        return f"❌ Failed to add contact. Status Code: {response.status_code} - {response.text}"


# -------------------------------
# Export tools for external use
# -------------------------------
tools = [
    get_user_contacts,
    add_user_contact
]
