"""
Batch repository.
"""
import sqlite3
from typing import List, Optional
from datetime import date
from pms.models import Batch

class BatchRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Batch:
        return Batch(**dict(row))

    def add(self, medicine_id: int, supplier_id: Optional[int], batch_no: str,
            quantity: int, purchase_price_minor: int, expiry_date: str,
            received_by: Optional[int]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO batches (
                medicine_id, supplier_id, batch_no, quantity, initial_quantity,
                purchase_price_minor, expiry_date, received_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (medicine_id, supplier_id, batch_no, quantity, quantity,
             purchase_price_minor, expiry_date, received_by)
        )
        return cursor.lastrowid

    def get(self, batch_id: int) -> Optional[Batch]:
        cursor = self.conn.execute("SELECT * FROM batches WHERE id = ?", (batch_id,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def list_by_medicine(self, medicine_id: int, active_only: bool = False, today_str: str = None) -> List[Batch]:
        if today_str is None:
            today_str = date.today().isoformat()
            
        sql = "SELECT * FROM batches WHERE medicine_id = ?"
        params = [medicine_id]
        
        if active_only:
            sql += " AND quantity > 0 AND expiry_date >= ?"
            params.append(today_str)
            
        sql += " ORDER BY expiry_date, id"
        
        cursor = self.conn.execute(sql, tuple(params))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update_quantity(self, batch_id: int, new_quantity: int):
        self.conn.execute(
            "UPDATE batches SET quantity = ? WHERE id = ?",
            (new_quantity, batch_id)
        )
