"""
Inventory service for batches and stock adjustments.
"""
import sqlite3
from datetime import date
from decimal import Decimal
from typing import List
from pms.models import Batch, Session
from pms.repositories.batch_repository import BatchRepository
from pms.repositories.medicine_repository import MedicineRepository
from pms.security import require
from pms.exceptions import ValidationError, DuplicateError, NotFoundError
from pms.money import to_minor
import pms.validators as v

class InventoryService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.batch_repo = BatchRepository(conn)
        self.med_repo = MedicineRepository(conn)

    def _write_audit(self, actor: Session, action: str, entity_id: int, details: str = None):
        self.conn.execute(
            "INSERT INTO audit_log (employee_id, action, entity, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (actor.employee_id, action, "Batch", entity_id, details)
        )

    def receive_stock(self, actor: Session, medicine_id: int, batch_no: str,
                      quantity: int, purchase_price: Decimal, expiry_date: str,
                      supplier_id: int = None, today: date = None) -> Batch:
        require(actor, "inventory.receive")
        
        if today is None:
            today = date.today()
            
        med = self.med_repo.get(medicine_id)
        if not med:
            raise NotFoundError(f"Medicine {medicine_id} not found.")
            
        batch_no = v.validate_non_empty_text(batch_no, "Batch Number")
        qty = v.validate_positive_int(quantity, "Quantity")
        pp_minor = to_minor(purchase_price)
        if pp_minor < 0:
            raise ValidationError("Purchase price cannot be negative.")
            
        exp_date_obj = v.validate_date(expiry_date, "Expiry Date")
        if exp_date_obj < today:
            raise ValidationError("Cannot receive an expired batch.")
            
        try:
            batch_id = self.batch_repo.add(
                medicine_id, supplier_id, batch_no, qty, pp_minor,
                expiry_date, actor.employee_id
            )
            self._write_audit(actor, "RECEIVE_STOCK", batch_id, f"Qty: {qty}")
            return self.batch_repo.get(batch_id)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                raise DuplicateError(f"Batch '{batch_no}' already exists for this medicine.")
            raise

    def list_batches(self, actor: Session, medicine_id: int, available_only: bool = False, today: date = None) -> List[Batch]:
        require(actor, "medicine.view")
        
        if today is None:
            today = date.today()
            
        batches = self.batch_repo.list_by_medicine(medicine_id, active_only=available_only, today_str=today.isoformat())
        
        for b in batches:
            b_exp = date.fromisoformat(b.expiry_date)
            b.days_to_expiry = (b_exp - today).days
            
        return batches
