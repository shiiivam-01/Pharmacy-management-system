"""
Store repository for multi-tenant database operations.
"""
import sqlite3
from typing import Optional
from backend.models import Store
import secrets
import string

class StoreRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Store:
        return Store(**dict(row))

    def get(self, store_id: int) -> Optional[Store]:
        cursor = self.conn.execute("SELECT * FROM stores WHERE id = ?", (store_id,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def get_by_uid(self, store_uid: str) -> Optional[Store]:
        cursor = self.conn.execute("SELECT * FROM stores WHERE store_uid = ?", (store_uid,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def _generate_uid(self) -> str:
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(6))

    def add(self, name: str, owner_name: str, location: Optional[str]) -> Store:
        while True:
            uid = self._generate_uid()
            # Check for collision
            if not self.get_by_uid(uid):
                break

        cursor = self.conn.execute(
            """
            INSERT INTO stores (store_uid, name, owner_name, location)
            VALUES (?, ?, ?, ?)
            """,
            (uid, name, owner_name, location)
        )
        return self.get(cursor.lastrowid)
