import pytest
from backend.services.supplier_service import SupplierService
from backend.exceptions import DuplicateError, NotFoundError, AuthorizationError

def test_add_supplier(db, admin):
    service = SupplierService(db)
    sup = service.add_supplier(admin, name="Med Corp", phone="12345")
    
    assert sup.id is not None
    assert sup.name == "Med Corp"
    assert sup.phone == "12345"
    assert sup.is_active == 1

def test_add_supplier_duplicate_name(db, admin):
    service = SupplierService(db)
    service.add_supplier(admin, name="Med Corp")
    with pytest.raises(DuplicateError):
        service.add_supplier(admin, name="Med Corp")

def test_pharmacist_cannot_add_supplier(db, pharmacist):
    service = SupplierService(db)
    with pytest.raises(AuthorizationError):
        service.add_supplier(pharmacist, name="New Supp")

def test_list_suppliers(db, admin, pharmacist):
    service = SupplierService(db)
    service.add_supplier(admin, name="Supp A")
    sup_b = service.add_supplier(admin, name="Supp B")
    service.deactivate_supplier(admin, sup_b.id)
    
    # Admin sees all
    all_sups = service.list_suppliers(admin, active_only=False)
    assert len(all_sups) == 2
    
    # Pharmacist typically sees active only (checked in menu/service layer)
    active_sups = service.list_suppliers(pharmacist, active_only=True)
    assert len(active_sups) == 1
    assert active_sups[0].name == "Supp A"

def test_update_supplier(db, admin):
    service = SupplierService(db)
    sup = service.add_supplier(admin, name="Med Corp")
    
    updated = service.update_supplier(admin, sup.id, name="Med Corp Inc", email="test@example.com")
    assert updated.name == "Med Corp Inc"
    assert updated.email == "test@example.com"

def test_update_supplier_not_found(db, admin):
    service = SupplierService(db)
    with pytest.raises(NotFoundError):
        service.update_supplier(admin, 999, name="Test")

def test_deactivate_supplier(db, admin):
    service = SupplierService(db)
    sup = service.add_supplier(admin, name="Med Corp")
    
    service.deactivate_supplier(admin, sup.id)
    retrieved = service.get_supplier(admin, sup.id)
    assert retrieved.is_active == 0
