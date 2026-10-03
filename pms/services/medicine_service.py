"""
Medicine service.
"""
import sqlite3
from typing import List, Optional
from pms.models import Medicine, Session
from pms.repositories.medicine_repository import MedicineRepository
from pms.security import require
from pms.exceptions import NotFoundError, DuplicateError, ValidationError
import pms.validators as v
from decimal import Decimal
from pms.money import to_minor

class MedicineService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = MedicineRepository(conn)

    def _write_audit(self, actor: Session, action: str, entity_id: int):
        self.conn.execute(
            "INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
            (actor.employee_id, action, "Medicine", entity_id)
        )

    def _calculate_available_stock(self, medicine_id: int, today: date = None) -> int:
        if today is None:
            from datetime import date
            today = date.today()
        cursor = self.conn.execute(
            """
            SELECT sum(quantity) FROM batches 
            WHERE medicine_id = ? AND expiry_date >= ?
            """,
            (medicine_id, today.isoformat())
        )
        val = cursor.fetchone()[0]
        return val if val else 0

    def list_medicines(self, actor: Session, active_only: bool = False, today: date = None) -> List[Medicine]:
        require(actor, "medicine.view")
        meds = self.repo.list_all(active_only)
        for m in meds:
            m.available_stock = self._calculate_available_stock(m.id, today)
        return meds

    def search_medicines(self, actor: Session, query: str, active_only: bool = False, today: date = None) -> List[Medicine]:
        require(actor, "medicine.view")
        query = query.strip()
        if not query:
            return self.list_medicines(actor, active_only, today)
            
        meds = self.repo.search(query, active_only)
        for m in meds:
            m.available_stock = self._calculate_available_stock(m.id, today)
        return meds

    def get_medicine(self, actor: Session, medicine_id: int, today: date = None) -> Medicine:
        require(actor, "medicine.view")
        med = self.repo.get(medicine_id)
        if not med:
            raise NotFoundError(f"Medicine ID {medicine_id} not found.")
        med.available_stock = self._calculate_available_stock(med.id, today)
        return med

    def add_medicine(self, actor: Session, name: str, form: str, strength: str,
                     unit_price: Decimal, tax_percent: float, reorder_level: int,
                     requires_prescription: bool, generic_name: Optional[str] = None,
                     category: Optional[str] = None, manufacturer: Optional[str] = None,
                     supplier_id: Optional[int] = None) -> Medicine:
        require(actor, "medicine.write")
        
        name = v.validate_non_empty_text(name, "Name")
        form = v.validate_non_empty_text(form, "Form")
        strength = strength.strip()
        unit_price_minor = to_minor(unit_price)
        if unit_price_minor <= 0:
            raise ValidationError("Unit price must be positive.")
        if tax_percent < 0 or tax_percent > 100:
            raise ValidationError("Tax percent must be between 0 and 100.")
            
        try:
            med_id = self.repo.add(
                name, generic_name, form, strength, category, manufacturer,
                supplier_id, unit_price_minor, float(tax_percent), reorder_level,
                1 if requires_prescription else 0
            )
            self._write_audit(actor, "CREATE_MEDICINE", med_id)
            return self.get_medicine(actor, med_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise DuplicateError(f"Medicine '{name}' ({form} - {strength}) already exists.")
            if "FOREIGN KEY" in str(e):
                raise ValidationError("Invalid supplier ID.")
            raise

    def update_medicine(self, actor: Session, medicine_id: int, name: str, form: str,
                        strength: str, unit_price: Decimal, tax_percent: float,
                        reorder_level: int, requires_prescription: bool,
                        generic_name: Optional[str] = None, category: Optional[str] = None,
                        manufacturer: Optional[str] = None, supplier_id: Optional[int] = None) -> Medicine:
        require(actor, "medicine.write")
        self.get_medicine(actor, medicine_id) # check exists
        
        name = v.validate_non_empty_text(name, "Name")
        form = v.validate_non_empty_text(form, "Form")
        strength = strength.strip()
        unit_price_minor = to_minor(unit_price)
        if unit_price_minor <= 0:
            raise ValidationError("Unit price must be positive.")
        if tax_percent < 0 or tax_percent > 100:
            raise ValidationError("Tax percent must be between 0 and 100.")
            
        try:
            self.repo.update(
                medicine_id, name, generic_name, form, strength, category,
                manufacturer, supplier_id, unit_price_minor, float(tax_percent),
                reorder_level, 1 if requires_prescription else 0
            )
            self._write_audit(actor, "UPDATE_MEDICINE", medicine_id)
            return self.get_medicine(actor, medicine_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise DuplicateError(f"Medicine '{name}' ({form} - {strength}) already exists.")
            if "FOREIGN KEY" in str(e):
                raise ValidationError("Invalid supplier ID.")
            raise

    def deactivate_medicine(self, actor: Session, medicine_id: int) -> None:
        require(actor, "medicine.deactivate")
        self.get_medicine(actor, medicine_id)
        self.repo.set_active(medicine_id, 0)
        self._write_audit(actor, "DEACTIVATE_MEDICINE", medicine_id)
