import pytest
from datetime import date
from backend.models import Batch
from backend.services.fefo import allocate_fefo
from backend.exceptions import InsufficientStockError

@pytest.fixture
def today():
    return date(2026, 10, 3)

def create_batch(id, qty, exp_date):
    return Batch(
        id=id, medicine_id=1, supplier_id=None, batch_no=f"B{id}",
        quantity=qty, initial_quantity=qty, purchase_price_minor=100,
        expiry_date=exp_date, received_on="2026-01-01", received_by=1
    )

def test_allocate_single_batch(today):
    batches = [
        create_batch(1, 100, "2027-01-01")
    ]
    alloc = allocate_fefo(batches, 10, today)
    assert len(alloc) == 1
    assert alloc[0][0].id == 1
    assert alloc[0][1] == 10

def test_allocate_spanning_batches(today):
    batches = [
        create_batch(1, 10, "2027-01-01"),
        create_batch(2, 20, "2027-02-01")
    ]
    alloc = allocate_fefo(batches, 15, today)
    assert len(alloc) == 2
    assert alloc[0][0].id == 1
    assert alloc[0][1] == 10
    assert alloc[1][0].id == 2
    assert alloc[1][1] == 5

def test_expired_skipped(today):
    batches = [
        create_batch(1, 10, "2026-09-01"), # Expired
        create_batch(2, 20, "2027-01-01")
    ]
    alloc = allocate_fefo(batches, 5, today)
    assert len(alloc) == 1
    assert alloc[0][0].id == 2
    assert alloc[0][1] == 5

def test_tie_on_expiry(today):
    batches = [
        create_batch(2, 10, "2027-01-01"),
        create_batch(1, 10, "2027-01-01")
    ]
    alloc = allocate_fefo(batches, 5, today)
    # Should pick id 1 first
    assert len(alloc) == 1
    assert alloc[0][0].id == 1
    assert alloc[0][1] == 5

def test_insufficient_stock(today):
    batches = [
        create_batch(1, 10, "2027-01-01")
    ]
    with pytest.raises(InsufficientStockError) as exc:
        allocate_fefo(batches, 15, today)
    assert exc.value.available == 10
