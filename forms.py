"""
CampusFix AI — Form Validation Layer
Centralizes input validation logic with clear error messages.
"""

from typing import Tuple

# Primary categories from campus_complaints_dataset.csv with metadata
DATASET_CATEGORIES = {
    "Cleaning": {
        "icon": "bi-spray-can",
        "description": "Dirty areas, trash, washroom hygiene, spills",
        "color": "teal",
    },
    "Electrical": {
        "icon": "bi-lightning-charge",
        "description": "Lights, fans, sockets, power outlets, AC power",
        "color": "warning",
    },
    "Furniture": {
        "icon": "bi-inbox",
        "description": "Chairs, desks, tables, benches, podiums",
        "color": "primary",
    },
    "IT": {
        "icon": "bi-pc-display",
        "description": "Projectors, lab PCs, WiFi, internet, printers",
        "color": "info",
    },
    "Plumbing and water": {
        "icon": "bi-droplet",
        "description": "Water coolers, taps, sinks, leaks, washroom water",
        "color": "cyan",
    },
    "Safety": {
        "icon": "bi-shield-exclamation",
        "description": "Sparks, smoke, exposed wires, gas smells, hazards",
        "color": "danger",
    },
    "Other": {
        "icon": "bi-three-dots",
        "description": "General campus maintenance issues",
        "color": "secondary",
    },
}

# Legacy categories supported to preserve backward compatibility
LEGACY_CATEGORIES = {"HVAC", "Plumbing", "Cleanliness"}
ALLOWED_CATEGORIES = set(DATASET_CATEGORIES.keys()) | LEGACY_CATEGORIES

# 31 standardized campus locations from campus_complaints_dataset.csv
DATASET_LOCATIONS = [
    "Admin Area",
    "Boys Common Room",
    "Boys Washroom",
    "Cafeteria",
    "Faculty Area",
    "Girls Common Room",
    "Girls Washroom",
    "LT1", "LT2", "LT3", "LT4", "LT5", "LT6", "LT7", "LT8", "LT9", "LT10", "LT11", "LT12",
    "Lab1", "Lab2", "Lab3", "Lab4", "Lab5", "Lab6", "Lab7", "Lab8", "Lab9", "Lab10",
    "Library",
    "Parking",
]

# Legacy buildings for backward compatibility with initial test suite
LEGACY_BUILDINGS = [
    "Engineering Complex",
    "Central Library",
    "Science Laboratory B",
    "Student Center & Cafeteria",
    "Residential Hall West",
]

ALLOWED_BUILDINGS = set(DATASET_LOCATIONS) | set(LEGACY_BUILDINGS)

# User roles from dataset
USER_TYPES = [
    {"id": "student", "label": "Student", "icon": "bi-mortarboard"},
    {"id": "teacher", "label": "Teacher / Faculty", "icon": "bi-person-video3"},
    {"id": "staff", "label": "Staff Member", "icon": "bi-person-badge"},
]
ALLOWED_USER_TYPES = {u["id"] for u in USER_TYPES}
DEFAULT_USER_TYPE = "student"

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
    building = (data.get("location") or data.get("building") or "").strip()
    room = (data.get("room") or "").strip()
    user_type = (data.get("user_type") or DEFAULT_USER_TYPE).strip().lower()
    
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
    
    # Validate location / building (allowlist)
    if building not in ALLOWED_BUILDINGS:
        return False, "Invalid campus location selected."
    
    # Validate user type (allowlist)
    if user_type and user_type not in ALLOWED_USER_TYPES:
        return False, "Invalid user type selected."
    
    # Validate room (optional but length-limited)
    if room and len(room) > MAX_ROOM_LENGTH:
        return False, f"Room/location detail must not exceed {MAX_ROOM_LENGTH} characters."
    
    return True, ""


def sanitize_complaint_data(data: dict) -> dict:
    """
    Sanitizes and normalizes form data after validation.
    
    Args:
        data: Raw form data dictionary
        
    Returns:
        Cleaned dictionary with consistent formatting
    """
    resolved_loc = (data.get("location") or data.get("building") or "").strip()
    user_type = (data.get("user_type") or DEFAULT_USER_TYPE).strip().lower()
    if user_type not in ALLOWED_USER_TYPES:
        user_type = DEFAULT_USER_TYPE

    return {
        "title": data.get("title", "").strip(),
        "description": data.get("description", "").strip(),
        "category": data.get("category", "").strip(),
        "building": resolved_loc,
        "location": resolved_loc,
        "room": data.get("room", "").strip() or None,  # Convert empty string to None
        "user_type": user_type,
        "image_filename": data.get("image_filename", "").strip() or None,
    }
