import pytest
from datetime import date
from decimal import Decimal
from backend.services.medicine_service import MedicineService
from backend.services.inventory_service import InventoryService
from backend.services.billing_service import BillingService
from backend.exceptions import AuthorizationError

def test_integration_flow(db, admin, pharmacist, today):
    med_service = MedicineService(db)
    inv_service = InventoryService(db)
    billing = BillingService(db)
    
    # 1. Admin adds medicine
    med = med_service.add_medicine(
        admin, name="Integration Med", form="Tablet", strength="100mg",
        unit_price=Decimal("1.50"), tax_percent=0.0, reorder_level=10,
        requires_prescription=False
    )
    
    # 2. Pharmacist tries to add medicine (Denied)
    with pytest.raises(AuthorizationError):
        med_service.add_medicine(
            pharmacist, name="Denied Med", form="Tablet", strength="10mg",
            unit_price=Decimal("1.00"), tax_percent=0.0, reorder_level=10,
            requires_prescription=False
        )
        
    # 3. Receive two batches with different expiry dates
    inv_service.receive_stock(admin, med.id, "B1", 10, Decimal("1.00"), "2027-01-01", today=today)
    inv_service.receive_stock(admin, med.id, "B2", 20, Decimal("1.00"), "2027-02-01", today=today)
    
    # Verify stock
    m = med_service.get_medicine(admin, med.id, today)
    assert m.available_stock == 30
    
    # 4. Sell across batches (buy 15, spans B1 and B2)
    cart = []
    cart = billing.add_to_cart(admin, cart, med.id, 15, today)
    sale = billing.create_sale(admin, cart, "Integration Customer", None, 0.0, "CASH", today)
    
    assert sale.total_minor == 2250 # 15 * 1.50 = 22.50 = 2250
    
    # Verify stock after sale
    m = med_service.get_medicine(admin, med.id, today)
    assert m.available_stock == 15 # 30 - 15 = 15
    
    # Verify exact batches
    batches = inv_service.list_batches(admin, med.id, available_only=True, today=today)
    assert len(batches) == 1
    assert batches[0].batch_no == "B2"
    assert batches[0].quantity == 15
