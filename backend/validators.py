"""
Input validation functions for the Pharmacy Management System.
"""
import re
from datetime import date
from backend.exceptions import ValidationError

def validate_non_empty_text(value: str, field_name: str) -> str:
    """Validates that text is not empty and returns stripped version."""
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty.")
    return value.strip()

def validate_positive_int(value: int | str, field_name: str, allow_zero: bool = False) -> int:
    """Validates that a value is a positive integer (or zero)."""
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be an integer.")
    
    if allow_zero and val < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    elif not allow_zero and val <= 0:
        raise ValidationError(f"{field_name} must be positive.")
    return val

def validate_date(value: str, field_name: str) -> date:
    """Validates ISO date format YYYY-MM-DD."""
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.")

def validate_phone(value: str, field_name: str = "Phone") -> str:
    """Validates phone number format."""
    val = (value or "").strip()
    if not val:
        return val
    if not re.match(r'^\+?[\d\s\-()]+$', val):
        raise ValidationError(f"{field_name} contains invalid characters.")
    return val

def validate_email(value: str, field_name: str = "Email") -> str:
    """Validates email format."""
    val = (value or "").strip()
    if not val:
        return val
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', val):
        raise ValidationError(f"{field_name} must be a valid email address.")
    return val

def validate_password_strength(password: str) -> str:
    """Validates password length (BR-15)."""
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    return password

def validate_choice(value: str, choices: list, field_name: str) -> str:
    if value not in choices:
        raise ValidationError(f"{field_name} must be one of {', '.join(choices)}.")
    return value
