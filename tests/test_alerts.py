import pytest
from datetime import date, timedelta
from decimal import Decimal
from backend.services.medicine_service import MedicineService
from backend.services.inventory_service import InventoryService
from backend.services.alert_service import AlertService
from backend.config import EXPIRY_WARNING_DAYS

def test_alerts(db, admin, today):
    med_service = MedicineService(db)
    inv_service = InventoryService(db)
    alert = AlertService(db)
    
    # 1. Low stock at reorder level
    m1 = med_service.add_medicine(
        admin, "Med1", form="Tablet", strength="10mg", unit_price=Decimal("1.0"),
        tax_percent=0.0, reorder_level=10, requires_prescription=False
    )
    inv_service.receive_stock(admin, m1.id, "B1", 10, Decimal("0.5"), "2099-01-01", today=today)
    
    # 2. Low stock below reorder level
    m2 = med_service.add_medicine(
        admin, "Med2", form="Tablet", strength="10mg", unit_price=Decimal("1.0"),
        tax_percent=0.0, reorder_level=20, requires_prescription=False
    )
    inv_service.receive_stock(admin, m2.id, "B2", 5, Decimal("0.5"), "2099-01-01", today=today)
    
    # 3. Normal stock
    m3 = med_service.add_medicine(
        admin, "Med3", form="Tablet", strength="10mg", unit_price=Decimal("1.0"),
        tax_percent=0.0, reorder_level=5, requires_prescription=False
    )
    inv_service.receive_stock(admin, m3.id, "B3", 50, Decimal("0.5"), "2099-01-01", today=today)
    
    # 4. Expiring exactly on N, N+1, and today
    m4 = med_service.add_medicine(
        admin, "Med4", form="Tablet", strength="10mg", unit_price=Decimal("1.0"),
        tax_percent=0.0, reorder_level=0, requires_prescription=False
    )
    day_n = (today + timedelta(days=EXPIRY_WARNING_DAYS)).isoformat()
    day_n1 = (today + timedelta(days=EXPIRY_WARNING_DAYS + 1)).isoformat()
    day_today = today.isoformat()
    day_past = (today - timedelta(days=1)).isoformat()
    
    inv_service.receive_stock(admin, m4.id, "B4_N", 10, Decimal("0.5"), day_n, today=today)
    inv_service.receive_stock(admin, m4.id, "B4_N1", 10, Decimal("0.5"), day_n1, today=today)
    inv_service.receive_stock(admin, m4.id, "B4_Today", 10, Decimal("0.5"), day_today, today=today)
    day_past_yesterday = (today - timedelta(days=2)).isoformat()
    inv_service.receive_stock(admin, m4.id, "B4_Past", 10, Decimal("0.5"), day_past, today=(today - timedelta(days=2)))
    
    # Check low stock (M1 is exactly at 10, M2 is below at 5)
    low = alert.get_low_stock_medicines(admin, today)
    low_ids = [m["id"] for m in low]
    assert m1.id in low_ids
    assert m2.id in low_ids
    assert m3.id not in low_ids
    
    # Check expiring soon (B4_N, B4_Today)
    soon = alert.get_expiring_soon_batches(admin, today)
    soon_batches = [b["batch_no"] for b in soon]
    assert "B4_N" in soon_batches
    assert "B4_Today" in soon_batches
    assert "B4_N1" not in soon_batches
    assert "B4_Past" not in soon_batches # Already expired
    
    # Check expired (B4_Past)
    expired = alert.get_expired_batches(admin, today)
    expired_batches = [b["batch_no"] for b in expired]
    assert "B4_Past" in expired_batches
    assert "B4_Today" not in expired_batches
    
    # Dashboard summary
    summary = alert.get_dashboard_summary(admin, today)
    assert summary["low_stock_count"] == 2
    assert summary["expiring_soon_count"] == 2
    assert summary["expired_count"] == 1
