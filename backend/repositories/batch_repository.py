"""
Batch repository.
"""
import sqlite3
from typing import List, Optional
from datetime import date
from backend.models import Batch

class BatchRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Batch:
        return Batch(**dict(row))

    def add(self, store_id: int, medicine_id: int, supplier_id: Optional[int], batch_no: str,
            quantity: int, purchase_price_minor: int, expiry_date: str,
            received_by: Optional[int]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO batches (
                store_id, medicine_id, supplier_id, batch_no, quantity, initial_quantity,
                purchase_price_minor, expiry_date, received_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (store_id, medicine_id, supplier_id, batch_no, quantity, quantity,
             purchase_price_minor, expiry_date, received_by)
        )
        return cursor.lastrowid

    def get(self, store_id: int, batch_id: int) -> Optional[Batch]:
        cursor = self.conn.execute("SELECT * FROM batches WHERE store_id = ? AND id = ?", (store_id, batch_id))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def list_by_medicine(self, store_id: int, medicine_id: int, active_only: bool = False, today_str: str = None) -> List[Batch]:
        if today_str is None:
            today_str = date.today().isoformat()
            
        sql = "SELECT * FROM batches WHERE store_id = ? AND medicine_id = ?"
        params = [store_id, medicine_id]
        
        if active_only:
            sql += " AND quantity > 0 AND expiry_date >= ?"
            params.append(today_str)
            
        sql += " ORDER BY expiry_date, id"
        
        cursor = self.conn.execute(sql, tuple(params))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update_quantity(self, store_id: int, batch_id: int, new_quantity: int):
        self.conn.execute(
            "UPDATE batches SET quantity = ? WHERE store_id = ? AND id = ?",
            (new_quantity, store_id, batch_id)
        )
