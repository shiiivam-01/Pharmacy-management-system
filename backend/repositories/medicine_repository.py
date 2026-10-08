"""
Medicine repository.
"""
import sqlite3
from typing import List, Optional
from backend.models import Medicine

class MedicineRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Medicine:
        return Medicine(**dict(row))

    def add(self, store_id: int, name: str, generic_name: Optional[str], form: str, strength: str,
            category: Optional[str], manufacturer: Optional[str], supplier_id: Optional[int],
            unit_price_minor: int, tax_percent: float, reorder_level: int,
            requires_prescription: int, description: Optional[str] = None) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO medicines (
                store_id, name, generic_name, form, strength, category, manufacturer,
                supplier_id, unit_price_minor, tax_percent, reorder_level,
                requires_prescription, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (store_id, name, generic_name, form, strength, category, manufacturer,
             supplier_id, unit_price_minor, tax_percent, reorder_level,
             requires_prescription, description)
        )
        return cursor.lastrowid

    def get(self, store_id: int, medicine_id: int) -> Optional[Medicine]:
        cursor = self.conn.execute("SELECT * FROM medicines WHERE store_id = ? AND id = ?", (store_id, medicine_id))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def search(self, store_id: int, query: str, active_only: bool = False, category: Optional[str] = None) -> List[Medicine]:
        sql = "SELECT * FROM medicines WHERE store_id = ? AND (name LIKE ? OR generic_name LIKE ?)"
        like_query = f"%{query}%"
        params = [store_id, like_query, like_query]
        
        if active_only:
            sql += " AND is_active = 1"
        if category:
            sql += " AND category = ?"
            params.append(category)
            
        sql += " ORDER BY name COLLATE NOCASE, form, strength"
        
        cursor = self.conn.execute(sql, tuple(params))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def list_all(self, store_id: int, active_only: bool = False, category: Optional[str] = None) -> List[Medicine]:
        sql = "SELECT * FROM medicines WHERE store_id = ?"
        params = [store_id]
        
        if active_only:
            sql += " AND is_active = 1"
        if category:
            sql += " AND category = ?"
            params.append(category)
            
        sql += " ORDER BY name COLLATE NOCASE, form, strength"
        
        cursor = self.conn.execute(sql, tuple(params))
        return [self.row_to_model(row) for row in cursor.fetchall()]

    def update(self, store_id: int, medicine_id: int, name: str, generic_name: Optional[str], form: str,
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
            WHERE store_id = ? AND id = ?
            """,
            (name, generic_name, form, strength, category, manufacturer,
             supplier_id, unit_price_minor, tax_percent, reorder_level,
             requires_prescription, store_id, medicine_id)
        )

    def set_active(self, store_id: int, medicine_id: int, is_active: int):
        self.conn.execute(
            "UPDATE medicines SET is_active = ?, updated_at = datetime('now', 'localtime') WHERE store_id = ? AND id = ?",
            (is_active, store_id, medicine_id)
        )
