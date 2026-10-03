import pytest
from datetime import date
from decimal import Decimal
from backend.services.inventory_service import InventoryService
from backend.services.medicine_service import MedicineService
from backend.exceptions import ValidationError, DuplicateError, AuthorizationError

@pytest.fixture
def medicine(db, admin):
    med_service = MedicineService(db)
    return med_service.add_medicine(
        admin, name="Paracetamol", form="Tablet", strength="500mg",
        unit_price=Decimal("1.50"), tax_percent=0.0, reorder_level=50,
        requires_prescription=False
    )

def test_receive_stock(db, admin, medicine, today):
    inv_service = InventoryService(db)
    
    batch = inv_service.receive_stock(
        admin, medicine.id, batch_no="B001", quantity=100,
        purchase_price=Decimal("0.50"), expiry_date="2027-01-01",
        today=today
    )
    
    assert batch.id is not None
    assert batch.quantity == 100
    assert batch.purchase_price_minor == 50
    
    # Check medicine available stock
    med_service = MedicineService(db)
    med = med_service.get_medicine(admin, medicine.id, today=today)
    assert med.available_stock == 100

def test_receive_stock_duplicate_batch(db, admin, medicine, today):
    inv_service = InventoryService(db)
    inv_service.receive_stock(
        admin, medicine.id, batch_no="B001", quantity=100,
        purchase_price=Decimal("0.50"), expiry_date="2027-01-01",
        today=today
    )
    with pytest.raises(DuplicateError):
        inv_service.receive_stock(
            admin, medicine.id, batch_no="B001", quantity=50,
            purchase_price=Decimal("0.50"), expiry_date="2027-02-01",
            today=today
        )

def test_receive_expired_stock(db, admin, medicine, today):
    inv_service = InventoryService(db)
    with pytest.raises(ValidationError):
        inv_service.receive_stock(
            admin, medicine.id, batch_no="B002", quantity=100,
            purchase_price=Decimal("0.50"), expiry_date="2026-09-01", # Past date
            today=today
        )

def test_list_batches_and_stock_exclusion(db, admin, medicine, today):
    inv_service = InventoryService(db)
    med_service = MedicineService(db)
    
    inv_service.receive_stock(
        admin, medicine.id, batch_no="B001", quantity=100,
        purchase_price=Decimal("0.50"), expiry_date="2026-12-01",
        today=today
    )
    
    batches = inv_service.list_batches(admin, medicine.id, available_only=True, today=today)
    assert len(batches) == 1
    
    # If we check available stock in 2027, the batch is expired
    future_date = date(2027, 1, 1)
    
    future_batches = inv_service.list_batches(admin, medicine.id, available_only=True, today=future_date)
    assert len(future_batches) == 0
    
    future_med = med_service.get_medicine(admin, medicine.id, today=future_date)
    assert future_med.available_stock == 0

def test_adjust_stock(db, admin, pharmacist, medicine, today):
    inv_service = InventoryService(db)
    batch = inv_service.receive_stock(
        admin, medicine.id, batch_no="B001", quantity=100,
        purchase_price=Decimal("0.50"), expiry_date="2027-01-01",
        today=today
    )
    
    # Pharmacist cannot adjust stock
    with pytest.raises(AuthorizationError):
        inv_service.adjust_stock(pharmacist, batch.id, 90, "DAMAGED")
        
    # Same quantity
    with pytest.raises(ValidationError):
        inv_service.adjust_stock(admin, batch.id, 100, "DAMAGED")
        
    # Valid adjustment
    inv_service.adjust_stock(admin, batch.id, 90, "DAMAGED")
    updated = inv_service.batch_repo.get(batch.id)
    assert updated.quantity == 90
    
def test_write_off_expired(db, admin, medicine, today):
    inv_service = InventoryService(db)
    # Receive in the past so it's expired today
    past_today = date(2025, 1, 1)
    batch = inv_service.receive_stock(
        admin, medicine.id, batch_no="B_EXPIRED", quantity=100,
        purchase_price=Decimal("0.50"), expiry_date="2026-01-01",
        today=past_today
    )
    
    # Try to write off when it's not expired
    with pytest.raises(ValidationError, match="not expired"):
        inv_service.write_off_expired(admin, batch.id, today=date(2025, 12, 31))
        
    # Write off successfully when expired
    inv_service.write_off_expired(admin, batch.id, today=today)
    
    updated = inv_service.batch_repo.get(batch.id)
    assert updated.quantity == 0
    
    # Cannot write off twice
    with pytest.raises(ValidationError, match="already has 0 quantity"):
        inv_service.write_off_expired(admin, batch.id, today=today)
