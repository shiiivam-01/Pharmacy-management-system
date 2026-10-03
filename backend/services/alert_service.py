"""
Alert service for dashboard notifications.
"""
import sqlite3
from typing import List, Dict, Any
from datetime import date
from backend.models import Session
from backend.config import EXPIRY_WARNING_DAYS

class AlertService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_low_stock_medicines(self, actor: Session, today: date = None) -> List[Dict[str, Any]]:
        if today is None:
            today = date.today()
        today_str = today.isoformat()
        
        cursor = self.conn.execute(
            """
            SELECT m.id, m.name, m.form, m.strength, m.reorder_level,
                   COALESCE(SUM(b.quantity), 0) as available_stock
            FROM medicines m
            LEFT JOIN batches b ON m.id = b.medicine_id AND b.expiry_date >= ? AND b.quantity > 0
            WHERE m.is_active = 1
            GROUP BY m.id
            HAVING available_stock <= m.reorder_level
            ORDER BY available_stock ASC
            """,
            (today_str,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_expiring_soon_batches(self, actor: Session, today: date = None) -> List[Dict[str, Any]]:
        if today is None:
            today = date.today()
        today_str = today.isoformat()
        
        cursor = self.conn.execute(
            f"""
            SELECT b.id as batch_id, b.batch_no, b.expiry_date, b.quantity,
                   m.id as medicine_id, m.name, m.form, m.strength
            FROM batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.quantity > 0 
              AND b.expiry_date >= ? 
              AND b.expiry_date <= date(?, '+{EXPIRY_WARNING_DAYS} days')
            ORDER BY b.expiry_date ASC
            """,
            (today_str, today_str)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_expired_batches(self, actor: Session, today: date = None) -> List[Dict[str, Any]]:
        if today is None:
            today = date.today()
        today_str = today.isoformat()
        
        cursor = self.conn.execute(
            """
            SELECT b.id as batch_id, b.batch_no, b.expiry_date, b.quantity,
                   m.id as medicine_id, m.name, m.form, m.strength
            FROM batches b
            JOIN medicines m ON b.medicine_id = m.id
            WHERE b.quantity > 0 
              AND b.expiry_date < ?
            ORDER BY b.expiry_date ASC
            """,
            (today_str,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_dashboard_summary(self, actor: Session, today: date = None) -> Dict[str, int]:
        low_stock = len(self.get_low_stock_medicines(actor, today))
        expiring_soon = len(self.get_expiring_soon_batches(actor, today))
        expired = len(self.get_expired_batches(actor, today))
        
        return {
            "low_stock_count": low_stock,
            "expiring_soon_count": expiring_soon,
            "expired_count": expired
        }
