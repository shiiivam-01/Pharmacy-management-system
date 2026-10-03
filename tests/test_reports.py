import pytest
from datetime import date
from decimal import Decimal
from backend.services.report_service import ReportService
from backend.services.medicine_service import MedicineService
from backend.services.inventory_service import InventoryService
from backend.services.billing_service import BillingService

@pytest.fixture
def test_data(db, admin, pharmacist, today):
    med_service = MedicineService(db)
    inv_service = InventoryService(db)
    billing = BillingService(db)
    
    med1 = med_service.add_medicine(
        admin, name="Paracetamol", form="Tablet", strength="500mg",
        unit_price=Decimal("2.00"), tax_percent=0.0, reorder_level=50,
        requires_prescription=False
    )
    inv_service.receive_stock(
        admin, med1.id, "B1", 100, Decimal("1.00"), "2027-01-01", today=today
    )
    
    med2 = med_service.add_medicine(
        admin, name="Aspirin", form="Tablet", strength="200mg",
        unit_price=Decimal("3.00"), tax_percent=0.0, reorder_level=100,
        requires_prescription=False
    )
    inv_service.receive_stock(
        admin, med2.id, "B2", 50, Decimal("1.50"), "2026-10-15", today=today # Expiring soon
    )
    
    # Create some sales
    cart1 = billing.add_to_cart(admin, [], med1.id, 10, today)
    s1 = billing.create_sale(admin, cart1, payment_method="CASH", today=today)
    
    cart2 = billing.add_to_cart(pharmacist, [], med2.id, 5, today)
    s2 = billing.create_sale(pharmacist, cart2, payment_method="CARD", today=today)
    
    return med1, med2

def test_daily_sales_summary(db, admin, pharmacist, today, test_data):
    rs = ReportService(db)
    
    # Admin sees both sales (10*2 = 20 CASH, 5*3 = 15 CARD)
    admin_summary = rs.get_daily_sales_summary(admin, today.isoformat())
    assert admin_summary["total_count"] == 2
    assert admin_summary["total_revenue"] == 3500
    assert admin_summary["by_method"]["CASH"]["total"] == 2000
    assert admin_summary["by_method"]["CARD"]["total"] == 1500
    
    # Pharmacist sees only their sale (CARD)
    pharm_summary = rs.get_daily_sales_summary(pharmacist, today.isoformat())
    assert pharm_summary["total_count"] == 1
    assert pharm_summary["total_revenue"] == 1500
    assert "CASH" not in pharm_summary["by_method"]

def test_stock_valuation(db, admin, today, test_data):
    rs = ReportService(db)
    # Remaining: B1 has 90 left, B2 has 45 left
    # Values: 90 * 1.00 = 90, 45 * 1.50 = 67.5 => total 157.50 (15750 minor)
    val = rs.get_stock_valuation(admin, today)
    assert val["total_value"] == 15750

def test_low_stock_report(db, admin, today, test_data):
    rs = ReportService(db)
    # Med1: 90 available, reorder 50 -> OK
    # Med2: 45 available, reorder 100 -> LOW
    low_stock = rs.get_low_stock_report(admin, today)
    assert len(low_stock) == 1
    assert low_stock[0]["name"] == "Aspirin"
    assert low_stock[0]["available"] == 45

def test_expiry_report(db, admin, today, test_data):
    rs = ReportService(db)
    
    # Within 30 days. B2 expires 2026-10-15. Today is 2026-10-03 (12 days)
    expiring = rs.get_expiry_report(admin, 30, today)
    assert len(expiring) == 1
    assert expiring[0]["batch_no"] == "B2"
    
    # Within 10 days, shouldn't show up
    expiring_10 = rs.get_expiry_report(admin, 10, today)
    assert len(expiring_10) == 0

def test_range_sales(db, admin, pharmacist, today, test_data):
    rs = ReportService(db)
    # Range covers today
    summary = rs.get_range_sales_summary(admin, today.isoformat(), today.isoformat())
    assert summary["count"] == 2
    assert summary["total"] == 3500

def test_top_sellers(db, admin, today, test_data):
    rs = ReportService(db)
    top = rs.get_top_sellers(admin, today.isoformat(), today.isoformat())
    assert len(top) == 2
    assert top[0]["name"] == "Paracetamol" # 10 sold
    assert top[0]["total_qty"] == 10
    assert top[1]["name"] == "Aspirin" # 5 sold
    assert top[1]["total_qty"] == 5

def test_sales_by_employee(db, admin, pharmacist, today, test_data):
    rs = ReportService(db)
    sales = rs.get_sales_by_employee(admin, today.isoformat(), today.isoformat())
    assert len(sales) >= 2 # Might include other users created by fixtures, but at least admin and pharmacist
    
    admin_sales = next(s for s in sales if s["username"] == "admin")
    assert admin_sales["bills_count"] == 1
    assert admin_sales["net_total"] == 2000
    
    pharm_sales = next(s for s in sales if s["username"] == "pharmacist")
    assert pharm_sales["bills_count"] == 1
    assert pharm_sales["net_total"] == 1500
