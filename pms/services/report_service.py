"""
Reporting service for the Pharmacy Management System.
"""
import sqlite3
from typing import Dict, List, Any
from datetime import date
from pms.models import Session
from pms.security import require

class ReportService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_daily_sales_summary(self, actor: Session, date_str: str = None) -> Dict[str, Any]:
        require(actor, "medicine.view")
        if not date_str:
            date_str = date.today().isoformat()
            
        sql = """
            SELECT payment_method, COUNT(*) as count, SUM(subtotal_minor) as subtotal, 
                   SUM(discount_minor) as discount, SUM(tax_minor) as tax, SUM(total_minor) as total
            FROM sales
            WHERE date(created_at) = ? AND status != 'VOIDED'
        """
        params = [date_str]
        
        if actor.role == "PHARMACIST":
            sql += " AND employee_id = ?"
            params.append(actor.employee_id)
            
        sql += " GROUP BY payment_method"
        
        cursor = self.conn.execute(sql, tuple(params))
        rows = cursor.fetchall()
        
        result = {
            "date": date_str,
            "total_count": 0,
            "total_subtotal": 0,
            "total_discount": 0,
            "total_tax": 0,
            "total_revenue": 0,
            "by_method": {}
        }
        
        for row in rows:
            pm = row["payment_method"]
            count = row["count"]
            sub = row["subtotal"]
            disc = row["discount"]
            tax = row["tax"]
            tot = row["total"]
            
            result["by_method"][pm] = {
                "count": count,
                "total": tot
            }
            
            result["total_count"] += count
            result["total_subtotal"] += sub
            result["total_discount"] += disc
            result["total_tax"] += tax
            result["total_revenue"] += tot
            
        return result

    def get_stock_valuation(self, actor: Session, today: date = None) -> Dict[str, Any]:
        require(actor, "inventory.adjust") # Admin only
        if not today:
            today = date.today()
            
        sql = """
            SELECT m.name, m.form, m.strength, b.batch_no, b.quantity, b.purchase_price_minor
            FROM batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.quantity > 0 AND b.expiry_date >= ?
        """
        cursor = self.conn.execute(sql, (today.isoformat(),))
        
        total_value = 0
        items = []
        for row in cursor.fetchall():
            val = row["quantity"] * row["purchase_price_minor"]
            total_value += val
            items.append({
                "medicine": f"{row['name']} {row['form']} {row['strength']}".strip(),
                "batch_no": row["batch_no"],
                "quantity": row["quantity"],
                "purchase_price": row["purchase_price_minor"],
                "value": val
            })
            
        return {
            "date": today.isoformat(),
            "total_value": total_value,
            "items": items
        }

    def get_low_stock_report(self, actor: Session, today: date = None) -> List[Dict[str, Any]]:
        require(actor, "medicine.view")
        if not today:
            today = date.today()
            
        sql = """
            SELECT m.id, m.name, m.form, m.strength, m.reorder_level,
                   IFNULL(SUM(b.quantity), 0) as available
            FROM medicines m
            LEFT JOIN batches b ON m.id = b.medicine_id AND b.quantity > 0 AND b.expiry_date >= ?
            WHERE m.is_active = 1
            GROUP BY m.id
            HAVING available <= m.reorder_level
            ORDER BY available ASC
        """
        cursor = self.conn.execute(sql, (today.isoformat(),))
        return [dict(r) for r in cursor.fetchall()]

    def get_expiry_report(self, actor: Session, days_ahead: int, today: date = None) -> List[Dict[str, Any]]:
        require(actor, "medicine.view")
        if not today:
            today = date.today()
            
        from datetime import timedelta
        cutoff_date = today + timedelta(days=days_ahead)
        
        sql = """
            SELECT m.name, m.form, m.strength, b.batch_no, b.quantity, b.expiry_date
            FROM batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.quantity > 0 AND b.expiry_date >= ? AND b.expiry_date <= ?
            ORDER BY b.expiry_date ASC
        """
        cursor = self.conn.execute(sql, (today.isoformat(), cutoff_date.isoformat()))
        return [dict(r) for r in cursor.fetchall()]

    def get_range_sales_summary(self, actor: Session, start_date: str, end_date: str) -> Dict[str, Any]:
        require(actor, "audit.view") # Admin only (reusing audit.view as proxy for high-level admin)
        
        sql = """
            SELECT COUNT(*) as count, SUM(subtotal_minor) as subtotal, 
                   SUM(discount_minor) as discount, SUM(tax_minor) as tax, SUM(total_minor) as total
            FROM sales
            WHERE date(created_at) >= ? AND date(created_at) <= ? AND status != 'VOIDED'
        """
        cursor = self.conn.execute(sql, (start_date, end_date))
        row = cursor.fetchone()
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": row["count"] or 0,
            "subtotal": row["subtotal"] or 0,
            "discount": row["discount"] or 0,
            "tax": row["tax"] or 0,
            "total": row["total"] or 0
        }

    def get_top_sellers(self, actor: Session, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        require(actor, "audit.view") # Admin only
        
        sql = """
            SELECT m.name, m.form, m.strength, SUM(si.quantity) as total_qty, SUM(si.line_total_minor) as total_revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN medicines m ON si.medicine_id = m.id
            WHERE date(s.created_at) >= ? AND date(s.created_at) <= ? AND s.status != 'VOIDED'
            GROUP BY m.id
            ORDER BY total_qty DESC
            LIMIT 10
        """
        cursor = self.conn.execute(sql, (start_date, end_date))
        return [dict(r) for r in cursor.fetchall()]

    def get_sales_by_employee(self, actor: Session, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        require(actor, "audit.view") # Admin only
        
        sql = """
            SELECT e.id, e.username, e.full_name, COUNT(s.id) as bills_count, SUM(s.total_minor) as net_total
            FROM employees e
            LEFT JOIN sales s ON e.id = s.employee_id AND date(s.created_at) >= ? AND date(s.created_at) <= ? AND s.status != 'VOIDED'
            GROUP BY e.id
            ORDER BY net_total DESC
        """
        cursor = self.conn.execute(sql, (start_date, end_date))
        return [dict(r) for r in cursor.fetchall()]

