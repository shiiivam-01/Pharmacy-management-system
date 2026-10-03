"""
Supplier repository.
"""
import sqlite3
from typing import List, Optional
from pms.models import Supplier

class SupplierRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Supplier:
        return Supplier(**dict(row))

    def add(self, name: str, contact_person: str, phone: str, email: str, address: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, contact_person, phone, email, address)
        )
        return cursor.lastrowid

    def get(self, supplier_id: int) -> Optional[Supplier]:
        cursor = self.conn.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def list_all(self, active_only: bool = False) -> List[Supplier]:
        query = "SELECT * FROM suppliers"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name COLLATE NOCASE"
        
        cursor = self.conn.execute(query)
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update(self, supplier_id: int, name: str, contact_person: str, phone: str, email: str, address: str):
        self.conn.execute(
            """
            UPDATE suppliers 
            SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
            """,
            (name, contact_person, phone, email, address, supplier_id)
        )

    def set_active(self, supplier_id: int, is_active: int):
        self.conn.execute(
            "UPDATE suppliers SET is_active = ? WHERE id = ?",
            (is_active, supplier_id)
        )

    def count_medicines(self, supplier_id: int) -> int:
        cursor = self.conn.execute(
            "SELECT count(*) FROM medicines WHERE supplier_id = ?",
            (supplier_id,)
        )
        return cursor.fetchone()[0]
