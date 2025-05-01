# user_management_tools.py

from graph_tools.graph_client import graph_get, graph_post, graph_patch, graph_delete
from langchain.tools import tool

# ------------------------------------------------------
# Tool: Fetch profile info of signed-in Microsoft user
# ------------------------------------------------------
@tool
def get_signed_in_user_profile() -> dict:
    """
    Get the profile of the currently signed-in user.

    Returns:
        dict: User profile details such as name, email, ID, etc.
    """
    return graph_get("me")

# ------------------------------------------------------
# Tool: List all users in the organization directory
# ------------------------------------------------------
@tool
def list_all_users() -> dict:
    """
    List all users in the Microsoft 365 organization.

    Returns:
        dict: A list of user profiles.
    """
    return graph_get("users")

# ------------------------------------------------------
# Tool: Create a new user in the Microsoft tenant
# ------------------------------------------------------
@tool
def create_new_user(user_details: dict) -> str:
    """
    Create a new user in the organization.

    Args:
        user_details (dict): Full JSON payload for user creation, including fields like:
            - accountEnabled
            - displayName
            - mailNickname
            - userPrincipalName
            - passwordProfile

    Returns:
        str: Status message indicating success or failure.
    """
    response = graph_post("users", user_details)

    if response.status_code == 201:
        return "✅ User created successfully!"
    else:
        return f"❌ Failed to create user. Status Code: {response.status_code} - {response.text}"

# ------------------------------------------------------
# Tool: Update the display name of an existing user
# ------------------------------------------------------
@tool
def update_user_display_name(user_id: str, new_display_name: str) -> str:
    """
    Update a user's display name.

    Args:
        user_id (str): The ID of the user to update.
        new_display_name (str): New display name to set.

    Returns:
        str: Status message indicating the result.
    """
    payload = {"displayName": new_display_name}
    response = graph_patch(f"users/{user_id}", payload)

    if response.status_code == 204:
        return "✅ User display name updated successfully!"
    else:
        return f"❌ Failed to update user. Status Code: {response.status_code} - {response.text}"

# ------------------------------------------------------
# Tool: Delete a user from Microsoft 365 directory
# ------------------------------------------------------
@tool
def delete_user(user_id: str) -> str:
    """
    Delete a user from the organization.

    Args:
        user_id (str): The ID of the user to delete.

    Returns:
        str: Status message indicating result.
    """
    response = graph_delete(f"users/{user_id}")

    if response.status_code == 204:
        return "✅ User deleted successfully!"
    else:
        return f"❌ Failed to delete user. Status Code: {response.status_code} - {response.text}"

# ------------------------------------------------------
# Export tools for LangChain or API integration
# ------------------------------------------------------
tools = [
    get_signed_in_user_profile,
    list_all_users,
    create_new_user,
    update_user_display_name,
    delete_user
]
