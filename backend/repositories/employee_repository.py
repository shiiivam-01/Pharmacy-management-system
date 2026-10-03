"""
Employee repository for database operations.
"""
import sqlite3
from typing import Optional
from backend.models import Employee

class EmployeeRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def row_to_model(self, row: sqlite3.Row) -> Employee:
        return Employee(**dict(row))

    def count(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM employees")
        return cursor.fetchone()[0]

    def count_active_admins(self) -> int:
        cursor = self.conn.execute("SELECT COUNT(*) FROM employees WHERE role = 'ADMIN' AND is_active = 1")
        return cursor.fetchone()[0]

    def get(self, employee_id: int) -> Optional[Employee]:
        cursor = self.conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None

    def add(self, full_name: str, phone: Optional[str], role: str, username: str, password_hash: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO employees (full_name, phone, role, username, password_hash)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, phone, role, username, password_hash)
        )
        return cursor.lastrowid

    def get_by_username(self, username: str) -> Optional[Employee]:
        cursor = self.conn.execute(
            "SELECT * FROM employees WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        return self.row_to_model(row) if row else None
        
    def record_failed_login(self, employee_id: int, lock_until: Optional[str] = None):
        self.conn.execute(
            """
            UPDATE employees 
            SET failed_attempts = failed_attempts + 1, locked_until = ? 
            WHERE id = ?
            """,
            (lock_until, employee_id)
        )

    def reset_failed_logins(self, employee_id: int):
        self.conn.execute(
            "UPDATE employees SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (employee_id,)
        )
