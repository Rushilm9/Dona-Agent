# graph_client.py

import requests
from graph_tools.auth import get_token

# Base URL for Microsoft Graph API
GRAPH_API = "https://graph.microsoft.com/v1.0"

# -----------------------------------------------------
# Function: Perform GET request to Microsoft Graph API
# -----------------------------------------------------
def graph_get(endpoint: str) -> dict:
    """
    Perform a GET request to the Microsoft Graph API.

    Args:
        endpoint (str): The API endpoint (e.g., "me/messages").

    Returns:
        dict: Parsed JSON response from the API.
    """
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GRAPH_API}/{endpoint}", headers=headers)
    return response.json()

# -----------------------------------------------------
# Function: Perform POST request to Microsoft Graph API
# -----------------------------------------------------
def graph_post(endpoint: str, payload: dict) -> requests.Response:
    """
    Perform a POST request to Microsoft Graph API.

    Args:
        endpoint (str): API endpoint (e.g., "me/sendMail").
        payload (dict): Request body data.

    Returns:
        Response: The HTTP response object.
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return requests.post(f"{GRAPH_API}/{endpoint}", headers=headers, json=payload)

# -----------------------------------------------------
# Function: Perform PATCH request to update Graph data
# -----------------------------------------------------
def graph_patch(endpoint: str, payload: dict) -> requests.Response:
    """
    Perform a PATCH request to Microsoft Graph API.

    Args:
        endpoint (str): API endpoint (e.g., "me/events/{id}").
        payload (dict): Fields to update.

    Returns:
        Response: The HTTP response object.
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    return requests.patch(f"{GRAPH_API}/{endpoint}", headers=headers, json=payload)

# -----------------------------------------------------
# Function: Perform DELETE request to remove data
# -----------------------------------------------------
def graph_delete(endpoint: str) -> requests.Response:
    """
    Perform a DELETE request to Microsoft Graph API.

    Args:
        endpoint (str): API endpoint (e.g., "me/events/{id}").

    Returns:
        Response: The HTTP response object.
    """
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{GRAPH_API}/{endpoint}", headers=headers)

# -----------------------------------------------------
# Function: Perform PUT request (e.g., for file uploads)
# -----------------------------------------------------
def graph_put(endpoint: str, payload: str) -> requests.Response:
    """
    Perform a PUT request to Microsoft Graph API (typically for file uploads).

    Args:
        endpoint (str): API endpoint.
        payload (str): Raw file/text content to upload.

    Returns:
        Response: The HTTP response object.
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    return requests.put(f"{GRAPH_API}/{endpoint}", headers=headers, data=payload)
