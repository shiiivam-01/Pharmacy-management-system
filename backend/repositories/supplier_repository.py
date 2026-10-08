"""
Supplier repository.
"""
import sqlite3
from typing import List, Optional
from backend.models import Supplier

class SupplierRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Supplier:
        return Supplier(**dict(row))

    def add(self, store_id: int, name: str, contact_person: str, phone: str, email: str, address: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO suppliers (store_id, name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (store_id, name, contact_person, phone, email, address)
        )
        return cursor.lastrowid

    def get(self, store_id: int, supplier_id: int) -> Optional[Supplier]:
        cursor = self.conn.execute("SELECT * FROM suppliers WHERE store_id = ? AND id = ?", (store_id, supplier_id))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def list_all(self, store_id: int, active_only: bool = False) -> List[Supplier]:
        query = "SELECT * FROM suppliers WHERE store_id = ?"
        params = [store_id]
        if active_only:
            query += " AND is_active = 1"
        query += " ORDER BY name COLLATE NOCASE"
        
        cursor = self.conn.execute(query, tuple(params))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update(self, store_id: int, supplier_id: int, name: str, contact_person: str, phone: str, email: str, address: str):
        self.conn.execute(
            """
            UPDATE suppliers 
            SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?
            WHERE store_id = ? AND id = ?
            """,
            (name, contact_person, phone, email, address, store_id, supplier_id)
        )

    def set_active(self, store_id: int, supplier_id: int, is_active: int):
        self.conn.execute(
            "UPDATE suppliers SET is_active = ? WHERE store_id = ? AND id = ?",
            (is_active, store_id, supplier_id)
        )

    def count_medicines(self, store_id: int, supplier_id: int) -> int:
        cursor = self.conn.execute(
            "SELECT count(*) FROM medicines WHERE store_id = ? AND supplier_id = ?",
            (store_id, supplier_id)
        )
        return cursor.fetchone()[0]
