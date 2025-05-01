# utils.py

from datetime import datetime

def safe_parse_datetime(date_str: str) -> datetime:
    """
    Safely parse ISO 8601 datetime strings from Microsoft Graph API.

    Handles fractional seconds by trimming them to microsecond precision (6 digits),
    which is required by Python's datetime.fromisoformat.

    Args:
        date_str (str): A datetime string (e.g. '2024-05-01T12:34:56.1234567Z').

    Returns:
        datetime: A Python datetime object.
    """
    if '.' in date_str:
        date_part, fractional = date_str.split('.')
        fractional = fractional[:6]  # Limit microseconds to 6 digits
        date_str = f"{date_part}.{fractional}"
    
    return datetime.fromisoformat(date_str)
