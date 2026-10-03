import pytest
from decimal import Decimal
from pms.services.medicine_service import MedicineService
from pms.exceptions import DuplicateError, NotFoundError, AuthorizationError, ValidationError

def test_add_medicine(db, admin):
    service = MedicineService(db)
    med = service.add_medicine(
        admin, name="Paracetamol", form="Tablet", strength="500mg",
        unit_price=Decimal("1.50"), tax_percent=10.0, reorder_level=50,
        requires_prescription=False
    )
    assert med.id is not None
    assert med.name == "Paracetamol"
    assert med.unit_price_minor == 150
    assert med.tax_percent == 10.0

def test_add_medicine_duplicate(db, admin):
    service = MedicineService(db)
    service.add_medicine(
        admin, name="Paracetamol", form="Tablet", strength="500mg",
        unit_price=Decimal("1.50"), tax_percent=10.0, reorder_level=50,
        requires_prescription=False
    )
    with pytest.raises(DuplicateError):
        service.add_medicine(
            admin, name="Paracetamol", form="Tablet", strength="500mg",
            unit_price=Decimal("2.00"), tax_percent=10.0, reorder_level=50,
            requires_prescription=False
        )

def test_pharmacist_cannot_add_medicine(db, pharmacist):
    service = MedicineService(db)
    with pytest.raises(AuthorizationError):
        service.add_medicine(
            pharmacist, name="Paracetamol", form="Tablet", strength="500mg",
            unit_price=Decimal("1.50"), tax_percent=10.0, reorder_level=50,
            requires_prescription=False
        )

def test_search_medicines(db, admin, pharmacist):
    service = MedicineService(db)
    m1 = service.add_medicine(
        admin, name="Aspirin", form="Tablet", strength="100mg",
        unit_price=Decimal("1.00"), tax_percent=0.0, reorder_level=10,
        requires_prescription=False, generic_name="Acetylsalicylic acid"
    )
    m2 = service.add_medicine(
        admin, name="Ibuprofen", form="Capsule", strength="200mg",
        unit_price=Decimal("2.00"), tax_percent=0.0, reorder_level=10,
        requires_prescription=False
    )
    service.deactivate_medicine(admin, m2.id)

    # Admin search
    res = service.search_medicines(admin, "ibu", active_only=False)
    assert len(res) == 1
    assert res[0].name == "Ibuprofen"
    
    # Search by generic name
    res2 = service.search_medicines(admin, "acetyl", active_only=False)
    assert len(res2) == 1
    assert res2[0].name == "Aspirin"
    
    # Pharmacist search (active only)
    res3 = service.search_medicines(pharmacist, "ibu", active_only=True)
    assert len(res3) == 0

def test_update_medicine(db, admin):
    service = MedicineService(db)
    med = service.add_medicine(
        admin, name="Aspirin", form="Tablet", strength="100mg",
        unit_price=Decimal("1.00"), tax_percent=0.0, reorder_level=10,
        requires_prescription=False
    )
    updated = service.update_medicine(
        admin, med.id, name="Aspirin Plus", form="Tablet", strength="100mg",
        unit_price=Decimal("1.50"), tax_percent=5.0, reorder_level=15,
        requires_prescription=True
    )
    assert updated.name == "Aspirin Plus"
    assert updated.unit_price_minor == 150
    assert updated.requires_prescription == 1
