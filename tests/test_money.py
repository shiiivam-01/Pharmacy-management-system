import pytest
from decimal import Decimal
from pms.money import to_minor, to_decimal, round_half_up

def test_to_minor():
    assert to_minor(Decimal('1.25')) == 125
    assert to_minor(Decimal('10.00')) == 1000
    assert to_minor(Decimal('1.255')) == 126
    assert to_minor(Decimal('1.254')) == 125

def test_to_decimal():
    assert to_decimal(125) == Decimal('1.25')
    assert to_decimal(1000) == Decimal('10.00')

def test_round_half_up():
    assert round_half_up(Decimal('1.255')) == Decimal('1.26')
    assert round_half_up(Decimal('1.254')) == Decimal('1.25')
