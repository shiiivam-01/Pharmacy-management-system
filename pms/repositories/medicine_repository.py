"""
Medicine repository.
"""
import sqlite3
from typing import List, Optional
from pms.models import Medicine

class MedicineRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Medicine:
        return Medicine(**dict(row))

    def add(self, name: str, generic_name: Optional[str], form: str, strength: str,
            category: Optional[str], manufacturer: Optional[str], supplier_id: Optional[int],
            unit_price_minor: int, tax_percent: float, reorder_level: int,
            requires_prescription: int) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO medicines (
                name, generic_name, form, strength, category, manufacturer,
                supplier_id, unit_price_minor, tax_percent, reorder_level,
                requires_prescription
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, generic_name, form, strength, category, manufacturer,
             supplier_id, unit_price_minor, tax_percent, reorder_level,
             requires_prescription)
        )
        return cursor.lastrowid

    def get(self, medicine_id: int) -> Optional[Medicine]:
        cursor = self.conn.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def search(self, query: str, active_only: bool = False) -> List[Medicine]:
        sql = "SELECT * FROM medicines WHERE (name LIKE ? OR generic_name LIKE ?)"
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY name COLLATE NOCASE, form, strength"
        
        like_query = f"%{query}%"
        cursor = self.conn.execute(sql, (like_query, like_query))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def list_all(self, active_only: bool = False) -> List[Medicine]:
        sql = "SELECT * FROM medicines"
        if active_only:
            sql += " WHERE is_active = 1"
        sql += " ORDER BY name COLLATE NOCASE, form, strength"
        
        cursor = self.conn.execute(sql)
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update(self, medicine_id: int, name: str, generic_name: Optional[str], form: str,
               strength: str, category: Optional[str], manufacturer: Optional[str],
               supplier_id: Optional[int], unit_price_minor: int, tax_percent: float,
               reorder_level: int, requires_prescription: int):
        self.conn.execute(
            """
            UPDATE medicines SET
                name = ?, generic_name = ?, form = ?, strength = ?,
                category = ?, manufacturer = ?, supplier_id = ?,
                unit_price_minor = ?, tax_percent = ?, reorder_level = ?,
                requires_prescription = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (name, generic_name, form, strength, category, manufacturer,
             supplier_id, unit_price_minor, tax_percent, reorder_level,
             requires_prescription, medicine_id)
        )

    def set_active(self, medicine_id: int, is_active: int):
        self.conn.execute(
            "UPDATE medicines SET is_active = ?, updated_at = datetime('now', 'localtime') WHERE id = ?",
            (is_active, medicine_id)
        )
