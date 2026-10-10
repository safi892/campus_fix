"""
CampusFix AI — Form Validation Layer
Centralizes input validation logic with clear error messages.
"""

from typing import Tuple

# Allowlisted categories and buildings (security constraint)
ALLOWED_CATEGORIES = {
    "HVAC",
    "Electrical",
    "Plumbing",
    "Furniture",
    "Cleanliness",
    "Safety"
}

ALLOWED_BUILDINGS = {
    "Engineering Complex",
    "Central Library",
    "Science Laboratory B",
    "Student Center & Cafeteria",
    "Residential Hall West"
}

# Complaint lifecycle, in workflow order (used for dropdowns and validation)
STATUS_FLOW = ("Submitted", "Under Review", "In Progress", "Resolved")
ALLOWED_STATUSES = set(STATUS_FLOW)

# Input length constraints (DoS protection)
MIN_TITLE_LENGTH = 5
MAX_TITLE_LENGTH = 150
MIN_DESC_LENGTH = 10
MAX_DESC_LENGTH = 2000
MAX_ROOM_LENGTH = 100


def validate_complaint_submission(data: dict) -> Tuple[bool, str]:
    """
    Validates complaint submission form data.
    
    Args:
        data: Dictionary containing form fields
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message is empty string.
    """
    # Extract and sanitize inputs
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "").strip()
    building = (data.get("building") or "").strip()
    room = (data.get("room") or "").strip()
    
    # Validate title
    if not title:
        return False, "Title is required."
    if len(title) < MIN_TITLE_LENGTH:
        return False, f"Title must be at least {MIN_TITLE_LENGTH} characters."
    if len(title) > MAX_TITLE_LENGTH:
        return False, f"Title must not exceed {MAX_TITLE_LENGTH} characters."
    
    # Validate description
    if not description:
        return False, "Description is required."
    if len(description) < MIN_DESC_LENGTH:
        return False, f"Description must be at least {MIN_DESC_LENGTH} characters."
    if len(description) > MAX_DESC_LENGTH:
        return False, f"Description must not exceed {MAX_DESC_LENGTH} characters."
    
    # Validate category (allowlist)
    if category not in ALLOWED_CATEGORIES:
        return False, "Invalid category selected."
    
    # Validate building (allowlist)
    if building not in ALLOWED_BUILDINGS:
        return False, "Invalid campus building selected."
    
    # Validate room (optional but length-limited)
    if room and len(room) > MAX_ROOM_LENGTH:
        return False, f"Room/location must not exceed {MAX_ROOM_LENGTH} characters."
    
    return True, ""


def sanitize_complaint_data(data: dict) -> dict:
    """
    Sanitizes and normalizes form data after validation.
    
    Args:
        data: Raw form data dictionary
        
    Returns:
        Cleaned dictionary with consistent formatting
    """
    return {
        "title": data.get("title", "").strip(),
        "description": data.get("description", "").strip(),
        "category": data.get("category", "").strip(),
        "building": data.get("building", "").strip(),
        "room": data.get("room", "").strip() or None,  # Convert empty string to None
    }
