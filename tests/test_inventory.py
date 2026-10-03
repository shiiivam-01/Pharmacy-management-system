import pytest
from datetime import date
from decimal import Decimal
from pms.services.inventory_service import InventoryService
from pms.services.medicine_service import MedicineService
from pms.exceptions import ValidationError, DuplicateError, AuthorizationError

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
