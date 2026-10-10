"""
CampusFix AI — Display formatting helpers, registered as Jinja filters in app.py.
"""

from datetime import datetime

DATE_DISPLAY_FORMAT = "%b %d, %Y at %I:%M %p"


def friendly_date(value: str | None) -> str:
    """'2026-10-10 12:43:01' -> 'Oct 10, 2026 at 12:43 PM'. Falls back to the raw value."""
    if not value:
        return ""
    try:
        return datetime.fromisoformat(str(value)).strftime(DATE_DISPLAY_FORMAT)
    except ValueError:
        return str(value)
