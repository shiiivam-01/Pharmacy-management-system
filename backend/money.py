"""
Money handling for the Pharmacy Management System.
Converts between Decimal and integer minor units.
"""
from decimal import Decimal, ROUND_HALF_UP

def to_minor(amount: Decimal) -> int:
    """
    Converts a Decimal amount (e.g. dollars/rupees) to integer minor units (e.g. cents/paise).
    Rounds half up to the nearest minor unit.
    """
    rounded = (amount * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return int(rounded)

def to_decimal(minor_amount: int) -> Decimal:
    """
    Converts integer minor units back to a Decimal amount.
    """
    return Decimal(minor_amount) / Decimal('100')

def round_half_up(amount: Decimal) -> Decimal:
    """
    Rounds a Decimal amount half up to two decimal places.
    """
    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
