import os
import sys
import msal
from dotenv import load_dotenv
from msal_extensions import *

# -------------------------------------
# Load environment variables from .env file
# -------------------------------------
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
USERNAME = os.getenv("USERNAME")

# -------------------------------------
# Define required Microsoft Graph scopes
# These scopes cover access to users, mail, calendar, teams, tasks, and more
# -------------------------------------
GRAPH_SCOPE = [
    "User.Read", "User.Read.All", "User.ReadWrite", "Group.Read.All", "Group.ReadWrite.All",
    "Mail.ReadWrite", "Calendars.ReadWrite", "Contacts.ReadWrite", 
    "Files.ReadWrite", "Team.ReadBasic.All", "Notes.ReadWrite", "Tasks.ReadWrite", "Tasks.Read",
    "People.Read", "Presence.Read", "Presence.ReadWrite", "Notifications.ReadWrite.CreatedByApp",
    "DeviceManagementApps.ReadWrite.All", "EduAdministration.ReadWrite", 
    "Bookings.ReadWrite.All", "Reports.Read.All", "SecurityEvents.Read.All"
]

# -------------------------------------
# Function to create a token persistence strategy
# It ensures cached tokens are securely stored per platform
# -------------------------------------
def msal_persistence(location: str):
    if sys.platform.startswith('win'):
        return FilePersistenceWithDataProtection(location)  # Windows-specific secure storage
    elif sys.platform.startswith('darwin'):
        return KeychainPersistence(location, "service", "account")  # macOS secure keychain
    else:
        return FilePersistence(location)  # Linux fallback (plaintext file)

# -------------------------------------
# Function to acquire a Microsoft Graph access token
# Tries silent login first, else initiates device login flow
# -------------------------------------
def get_token() -> str:
    # Setup token cache persistence
    persistence = msal_persistence("token_cache.bin")
    cache = PersistedTokenCache(persistence)

    # Initialize MSAL public client application
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )

    # Attempt silent login using cached account
    accounts = app.get_accounts(username=USERNAME)
    if accounts:
        result = app.acquire_token_silent(GRAPH_SCOPE, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # If silent login fails, initiate device flow authentication
    flow = app.initiate_device_flow(scopes=GRAPH_SCOPE)
    if "user_code" not in flow:
        raise ValueError("Device flow failed. Could not retrieve user code.")

    # Prompt user to authenticate using device code
    print("\n🔵 Microsoft Login Required:")
    print(flow["message"])
    
    # Wait for user to complete authentication
    result = app.acquire_token_by_device_flow(flow)

    # Return access token if available
    if "access_token" in result:
        return result["access_token"]
    else:
        raise ValueError("Authentication failed.")
