# contacts_api_router.py

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from contacts_helper import add_contact, get_contacts

# Initialize router
router = APIRouter()

# ---------------------------------------------
# Pydantic Model: Incoming contact data format
# ---------------------------------------------
class Contact(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    birthday: Optional[str] = None  # Format: "YYYY-MM-DD"
    company_name: Optional[str] = None

# ---------------------------------------------
# Endpoint: Add new contact to Microsoft Graph
# ---------------------------------------------
@router.post("/add_contact", summary="Add a new contact", response_model=dict)
async def create_contact(contact: Contact):
    """
    Add a contact to the user's Microsoft 365 contact list.

    Args:
        contact (Contact): Contains name, email, mobile, and optional birthday/company.

    Returns:
        dict: Status message from the Graph API tool.
    """
    contact_data = {
        "displayName": contact.name,
        "emailAddresses": [{"address": contact.email}],
        "businessPhones": [contact.mobile],
    }

    if contact.birthday:
        contact_data["birthday"] = contact.birthday
    if contact.company_name:
        contact_data["companyName"] = contact.company_name

    status_message = add_contact(contact_data)
    return {"message": status_message}

# ---------------------------------------------
# Endpoint: Fetch all contacts of signed-in user
# ---------------------------------------------
@router.get("/contacts", summary="Fetch all user contacts", response_model=dict)
async def fetch_contacts():
    """
    Retrieve all contacts associated with the signed-in Microsoft account.

    Returns:
        dict: A list of contact objects and total count.
    """
    contacts = get_contacts()
    return {
        "contacts": contacts.get('value', []),
        "contact_count": len(contacts.get('value', []))
    }
