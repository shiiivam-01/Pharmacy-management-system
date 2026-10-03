import pytest
from datetime import date
from pms.models import CartLine
from pms.services.billing_service import BillingService
from pms.services.medicine_service import MedicineService
from pms.services.inventory_service import InventoryService
from pms.exceptions import ValidationError, InsufficientStockError
from decimal import Decimal

@pytest.fixture
def test_data(db, admin, today):
    med_service = MedicineService(db)
    inv_service = InventoryService(db)
    
    med1 = med_service.add_medicine(
        admin, name="Paracetamol", form="Tablet", strength="500mg",
        unit_price=Decimal("1.50"), tax_percent=5.0, reorder_level=50,
        requires_prescription=False
    )
    inv_service.receive_stock(
        admin, med1.id, "B1", 100, Decimal("1.00"), "2027-01-01", today=today
    )
    
    med2 = med_service.add_medicine(
        admin, name="Amoxicillin", form="Capsule", strength="250mg",
        unit_price=Decimal("3.00"), tax_percent=10.0, reorder_level=20,
        requires_prescription=True
    )
    inv_service.receive_stock(
        admin, med2.id, "B2", 50, Decimal("2.00"), "2027-01-01", today=today
    )
    inv_service.receive_stock(
        admin, med2.id, "B3", 50, Decimal("2.00"), "2027-02-01", today=today
    )
    
    return med1, med2

def test_add_to_cart(db, admin, today, test_data):
    med1, med2 = test_data
    billing = BillingService(db)
    
    cart = []
    cart = billing.add_to_cart(admin, cart, med1.id, 2, today)
    assert len(cart) == 1
    assert cart[0].quantity == 2
    
    # Merge
    cart = billing.add_to_cart(admin, cart, med1.id, 3, today)
    assert len(cart) == 1
    assert cart[0].quantity == 5
    
    # Add second med
    cart = billing.add_to_cart(admin, cart, med2.id, 1, today)
    assert len(cart) == 2

def test_insufficient_stock_cart(db, admin, today, test_data):
    med1, med2 = test_data
    billing = BillingService(db)
    cart = []
    
    with pytest.raises(InsufficientStockError) as exc:
        billing.add_to_cart(admin, cart, med1.id, 101, today)
    assert exc.value.available == 100

def test_calculate_totals(db, admin):
    billing = BillingService(db)
    # README example: lines 4000 and 8500 minor units. 5% tax.
    cart = [
        CartLine(1, "M1", 1, 4000, 5.0, False),
        CartLine(2, "M2", 1, 8500, 5.0, False)
    ]
    totals = billing.calculate_totals(cart, 0.0)
    assert totals["subtotal"] == 12500
    assert totals["tax"] == 625 # 200 + 425
    assert totals["discount"] == 0
    assert totals["total"] == 13125
    
    # With 10% discount
    totals_disc = billing.calculate_totals(cart, 10.0)
    assert totals_disc["subtotal"] == 12500
    assert totals_disc["discount"] == 1250 # 400 + 850
    # Tax on 3600 = 180. Tax on 7650 = 382.5 (rounds to 383) -> 180 + 383 = 563
    assert totals_disc["tax"] == 563
    assert totals_disc["total"] == 12500 - 1250 + 563

def test_create_sale_atomic(db, admin, today, test_data):
    med1, med2 = test_data
    billing = BillingService(db)
    
    cart = []
    cart = billing.add_to_cart(admin, cart, med1.id, 10, today)
    cart = billing.add_to_cart(admin, cart, med2.id, 60, today) # Spans B2 (50) and B3 (10)
    
    sale = billing.create_sale(admin, cart, "John Doe", "Dr. Smith", 0.0, "CASH", today)
    assert sale.bill_no == "PMS-20261003-0001"
    
    # Let's check stock
    med_service = MedicineService(db)
    m1 = med_service.get_medicine(admin, med1.id, today)
    assert m1.available_stock == 90
    m2 = med_service.get_medicine(admin, med2.id, today)
    assert m2.available_stock == 40

def test_void_sale(db, admin, today, test_data):
    med1, med2 = test_data
    billing = BillingService(db)
    
    cart = []
    cart = billing.add_to_cart(admin, cart, med1.id, 10, today)
    sale = billing.create_sale(admin, cart, today=today)
    
    med_service = MedicineService(db)
    assert med_service.get_medicine(admin, med1.id, today).available_stock == 90
    
    billing.void_sale(admin, sale.bill_no, "Customer returned")
    
    assert med_service.get_medicine(admin, med1.id, today).available_stock == 100
    
    with pytest.raises(ValidationError, match="already VOIDED"):
        billing.void_sale(admin, sale.bill_no, "Trying again")

def test_sales_history(db, admin, pharmacist, today, test_data):
    med1, _ = test_data
    billing = BillingService(db)
    
    # Create two sales by admin
    cart1 = billing.add_to_cart(admin, [], med1.id, 1, today)
    s1 = billing.create_sale(admin, cart1, today=today)
    
    cart2 = billing.add_to_cart(admin, [], med1.id, 2, today)
    s2 = billing.create_sale(admin, cart2, today=today)
    
    # Admin should see both
    history = billing.get_sales_history(admin)
    assert len(history) == 2
    
    # Pharmacist should see none, since admin created them
    history_pharm = billing.get_sales_history(pharmacist)
    assert len(history_pharm) == 0
    
    # Verify get_sale_details works for admin
    sale, items = billing.get_sale_details(admin, s1.bill_no)
    assert sale.id == s1.id
    assert len(items) == 1
    
    # Pharmacist shouldn't be able to view admin's bill
    with pytest.raises(ValidationError, match="do not have permission"):
        billing.get_sale_details(pharmacist, s1.bill_no)

def test_pharmacist_discount_cap(db, admin, pharmacist, today, test_data):
    med1, _ = test_data
    billing = BillingService(db)
    
    cart = billing.add_to_cart(pharmacist, [], med1.id, 1, today)
    
    # 10% is allowed
    sale1 = billing.create_sale(pharmacist, cart, discount_percent=10.0, today=today)
    assert sale1.discount_percent == 10.0
    
    # 11% is rejected
    with pytest.raises(ValidationError, match="cannot exceed 10%"):
        billing.create_sale(pharmacist, cart, discount_percent=11.0, today=today)
        
    # Admin can do 100%
    sale2 = billing.create_sale(admin, cart, discount_percent=100.0, today=today)
    assert sale2.discount_percent == 100.0
