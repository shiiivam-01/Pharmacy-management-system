import pytest
from datetime import date
from pms.validators import (
    validate_non_empty_text,
    validate_positive_int,
    validate_date,
    validate_phone,
    validate_email,
    validate_password_strength,
)
from pms.exceptions import ValidationError

def test_validate_non_empty_text():
    assert validate_non_empty_text(" hello ", "Name") == "hello"
    with pytest.raises(ValidationError):
        validate_non_empty_text("", "Name")
    with pytest.raises(ValidationError):
        validate_non_empty_text("   ", "Name")

def test_validate_positive_int():
    assert validate_positive_int("5", "Qty") == 5
    assert validate_positive_int(10, "Qty") == 10
    assert validate_positive_int("0", "Qty", allow_zero=True) == 0
    with pytest.raises(ValidationError):
        validate_positive_int("0", "Qty", allow_zero=False)
    with pytest.raises(ValidationError):
        validate_positive_int("-5", "Qty", allow_zero=True)
    with pytest.raises(ValidationError):
        validate_positive_int("abc", "Qty")

def test_validate_date():
    assert validate_date("2026-10-03", "Date") == date(2026, 10, 3)
    with pytest.raises(ValidationError):
        validate_date("03-10-2026", "Date")
    with pytest.raises(ValidationError):
        validate_date("not a date", "Date")

def test_validate_phone():
    assert validate_phone("+1 234-567") == "+1 234-567"
    assert validate_phone("") == ""
    with pytest.raises(ValidationError):
        validate_phone("abc")

def test_validate_email():
    assert validate_email("test@example.com") == "test@example.com"
    assert validate_email("") == ""
    with pytest.raises(ValidationError):
        validate_email("not-an-email")

def test_validate_password_strength():
    assert validate_password_strength("12345678") == "12345678"
    with pytest.raises(ValidationError):
        validate_password_strength("short")
