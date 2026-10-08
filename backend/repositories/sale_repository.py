"""
Sale repository.
"""
import sqlite3
from typing import List, Optional
from backend.models import Sale, SaleItem

class SaleRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_sale(self, store_id: int, bill_no: str, employee_id: int, customer_name: Optional[str],
                 prescription_note: Optional[str], subtotal_minor: int,
                 discount_percent: float, discount_minor: int, tax_minor: int,
                 total_minor: int, payment_method: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO sales (
                store_id, bill_no, employee_id, customer_name, prescription_note,
                subtotal_minor, discount_percent, discount_minor, tax_minor,
                total_minor, payment_method, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
            """,
            (store_id, bill_no, employee_id, customer_name, prescription_note,
             subtotal_minor, discount_percent, discount_minor, tax_minor,
             total_minor, payment_method)
        )
        return cursor.lastrowid

    def add_sale_item(self, store_id: int, sale_id: int, medicine_id: int, batch_id: int,
                      quantity: int, unit_price_minor: int, tax_percent: float,
                      line_total_minor: int) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO sale_items (
                store_id, sale_id, medicine_id, batch_id, quantity,
                unit_price_minor, tax_percent, line_total_minor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (store_id, sale_id, medicine_id, batch_id, quantity,
             unit_price_minor, tax_percent, line_total_minor)
        )
        return cursor.lastrowid

    def count_sales_today(self, store_id: int, today_str: str) -> int:
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM sales WHERE store_id = ? AND date(created_at) = ?",
            (store_id, today_str)
        )
        return cursor.fetchone()[0]

    def get_sale_by_bill_no(self, store_id: int, bill_no: str) -> Optional[Sale]:
        cursor = self.conn.execute("SELECT * FROM sales WHERE store_id = ? AND bill_no = ?", (store_id, bill_no))
        row = cursor.fetchone()
        return Sale(**dict(row)) if row else None
        
    def get_sale_items(self, store_id: int, sale_id: int) -> List[SaleItem]:
        cursor = self.conn.execute("SELECT * FROM sale_items WHERE store_id = ? AND sale_id = ?", (store_id, sale_id))
        return [SaleItem(**dict(row)) for row in cursor.fetchall()]

    def set_sale_status(self, store_id: int, sale_id: int, status: str, void_reason: str, voided_by: int):
        self.conn.execute(
            """
            UPDATE sales SET status = ?, void_reason = ?, voided_by = ?, voided_at = datetime('now', 'localtime')
            WHERE store_id = ? AND id = ?
            """,
            (status, void_reason, voided_by, store_id, sale_id)
        )

    def list_sales(self, store_id: int, employee_id: Optional[int] = None, date_str: Optional[str] = None) -> List[Sale]:
        sql = "SELECT * FROM sales WHERE store_id = ?"
        params = [store_id]
        
        if employee_id is not None:
            sql += " AND employee_id = ?"
            params.append(employee_id)
            
        if date_str:
            sql += " AND date(created_at) = ?"
            params.append(date_str)
            
        sql += " ORDER BY created_at DESC"
        
        cursor = self.conn.execute(sql, tuple(params))
        return [Sale(**dict(row)) for row in cursor.fetchall()]
