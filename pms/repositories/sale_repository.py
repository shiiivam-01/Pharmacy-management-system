"""
Sale repository.
"""
import sqlite3
from typing import List, Optional
from pms.models import Sale, SaleItem

class SaleRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add_sale(self, bill_no: str, employee_id: int, customer_name: Optional[str],
                 prescription_note: Optional[str], subtotal_minor: int,
                 discount_percent: float, discount_minor: int, tax_minor: int,
                 total_minor: int, payment_method: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO sales (
                bill_no, employee_id, customer_name, prescription_note,
                subtotal_minor, discount_percent, discount_minor, tax_minor,
                total_minor, payment_method, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
            """,
            (bill_no, employee_id, customer_name, prescription_note,
             subtotal_minor, discount_percent, discount_minor, tax_minor,
             total_minor, payment_method)
        )
        return cursor.lastrowid

    def add_sale_item(self, sale_id: int, medicine_id: int, batch_id: int,
                      quantity: int, unit_price_minor: int, tax_percent: float,
                      line_total_minor: int) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO sale_items (
                sale_id, medicine_id, batch_id, quantity,
                unit_price_minor, tax_percent, line_total_minor
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (sale_id, medicine_id, batch_id, quantity,
             unit_price_minor, tax_percent, line_total_minor)
        )
        return cursor.lastrowid

    def count_sales_today(self, today_str: str) -> int:
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM sales WHERE date(created_at) = ?",
            (today_str,)
        )
        return cursor.fetchone()[0]

    def get_sale_by_bill_no(self, bill_no: str) -> Optional[Sale]:
        cursor = self.conn.execute("SELECT * FROM sales WHERE bill_no = ?", (bill_no,))
        row = cursor.fetchone()
        return Sale(**dict(row)) if row else None
        
    def get_sale_items(self, sale_id: int) -> List[SaleItem]:
        cursor = self.conn.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,))
        return [SaleItem(**dict(row)) for row in cursor.fetchall()]

    def set_sale_status(self, sale_id: int, status: str, void_reason: str, voided_by: int):
        self.conn.execute(
            """
            UPDATE sales SET status = ?, void_reason = ?, voided_by = ?, voided_at = datetime('now', 'localtime')
            WHERE id = ?
            """,
            (status, void_reason, voided_by, sale_id)
        )
