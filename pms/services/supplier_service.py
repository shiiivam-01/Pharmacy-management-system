"""
Supplier service.
"""
import sqlite3
from typing import List, Optional
from pms.models import Supplier, Session
from pms.repositories.supplier_repository import SupplierRepository
from pms.security import require
from pms.exceptions import NotFoundError, DuplicateError
import pms.validators as v

class SupplierService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = SupplierRepository(conn)

    def _write_audit(self, actor: Session, action: str, entity_id: int):
        self.conn.execute(
            "INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
            (actor.employee_id, action, "Supplier", entity_id)
        )

    def list_suppliers(self, actor: Session, active_only: bool = False) -> List[Supplier]:
        require(actor, "supplier.view")
        suppliers = self.repo.list_all(active_only)
        for supplier in suppliers:
            supplier.medicine_count = self.repo.count_medicines(supplier.id)
        return suppliers

    def get_supplier(self, actor: Session, supplier_id: int) -> Supplier:
        require(actor, "supplier.view")
        supplier = self.repo.get(supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier ID {supplier_id} not found.")
        return supplier

    def add_supplier(self, actor: Session, name: str, contact_person: Optional[str] = None, 
                     phone: Optional[str] = None, email: Optional[str] = None, address: Optional[str] = None) -> Supplier:
        require(actor, "supplier.write")
        
        name = v.validate_non_empty_text(name, "Supplier name")
        phone = v.validate_phone(phone) if phone else None
        email = v.validate_email(email) if email else None
        
        try:
            supplier_id = self.repo.add(name, contact_person, phone, email, address)
            self._write_audit(actor, "CREATE_SUPPLIER", supplier_id)
            return self.get_supplier(actor, supplier_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise DuplicateError(f"Supplier with name '{name}' already exists.")
            raise

    def update_supplier(self, actor: Session, supplier_id: int, name: str, 
                        contact_person: Optional[str] = None, phone: Optional[str] = None, 
                        email: Optional[str] = None, address: Optional[str] = None) -> Supplier:
        require(actor, "supplier.write")
        
        # Ensure exists
        self.get_supplier(actor, supplier_id)
        
        name = v.validate_non_empty_text(name, "Supplier name")
        phone = v.validate_phone(phone) if phone else None
        email = v.validate_email(email) if email else None
        
        try:
            self.repo.update(supplier_id, name, contact_person, phone, email, address)
            self._write_audit(actor, "UPDATE_SUPPLIER", supplier_id)
            return self.get_supplier(actor, supplier_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise DuplicateError(f"Supplier with name '{name}' already exists.")
            raise

    def deactivate_supplier(self, actor: Session, supplier_id: int) -> None:
        require(actor, "supplier.write")
        self.get_supplier(actor, supplier_id) # ensure exists
        self.repo.set_active(supplier_id, 0)
        self._write_audit(actor, "DEACTIVATE_SUPPLIER", supplier_id)
