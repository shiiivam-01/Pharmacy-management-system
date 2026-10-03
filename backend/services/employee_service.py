"""
Employee service for managing employees.
"""
import sqlite3
from typing import List, Optional
from backend.models import Session, Employee
from backend.repositories.employee_repository import EmployeeRepository
from backend.security import require, hash_password
from backend.exceptions import ValidationError
import backend.validators as v

class EmployeeService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = EmployeeRepository(conn)

    def _validate_password(self, password: str):
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

    def add_employee(self, actor: Session, full_name: str, phone: Optional[str],
                     role: str, username: str, password: str) -> Employee:
        require(actor, "employee.manage")
        
        full_name = v.validate_non_empty_text(full_name, "Full Name")
        username = v.validate_non_empty_text(username, "Username")
        role = v.validate_non_empty_text(role, "Role").upper()
        if role not in ("ADMIN", "PHARMACIST"):
            raise ValidationError("Role must be ADMIN or PHARMACIST.")
            
        self._validate_password(password)
        
        existing = self.repo.get_by_username(username)
        if existing:
            raise ValidationError(f"Username '{username}' is already taken.")
            
        password_hash = hash_password(password)
        
        emp_id = self.repo.add(full_name, phone, role, username, password_hash)
        self.conn.execute("INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
                          (actor.employee_id, "ADD_EMPLOYEE", "Employee", emp_id))
        return self.repo.get(emp_id)

    def list_employees(self, actor: Session) -> List[Employee]:
        require(actor, "employee.manage")
        cursor = self.conn.execute("SELECT * FROM employees ORDER BY full_name")
        return [Employee(**dict(row)) for row in cursor.fetchall()]

    def update_employee(self, actor: Session, employee_id: int, full_name: str, phone: Optional[str], role: str) -> Employee:
        require(actor, "employee.manage")
        emp = self.repo.get(employee_id)
        if not emp:
            raise ValidationError("Employee not found.")
            
        full_name = v.validate_non_empty_text(full_name, "Full Name")
        role = v.validate_non_empty_text(role, "Role").upper()
        if role not in ("ADMIN", "PHARMACIST"):
            raise ValidationError("Role must be ADMIN or PHARMACIST.")
            
        if emp.role == "ADMIN" and role != "ADMIN" and emp.is_active:
            if self.repo.count_active_admins() <= 1:
                raise ValidationError("Cannot change the role of the last active Admin.")
                
        self.conn.execute(
            "UPDATE employees SET full_name = ?, phone = ?, role = ? WHERE id = ?",
            (full_name, phone, role, employee_id)
        )
        self.conn.execute("INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
                          (actor.employee_id, "UPDATE_EMPLOYEE", "Employee", employee_id))
        return self.repo.get(employee_id)

    def deactivate_employee(self, actor: Session, employee_id: int):
        require(actor, "employee.manage")
        if actor.employee_id == employee_id:
            raise ValidationError("You cannot deactivate yourself.")
            
        emp = self.repo.get(employee_id)
        if not emp:
            raise ValidationError("Employee not found.")
            
        if emp.role == "ADMIN" and self.repo.count_active_admins() <= 1:
            raise ValidationError("Cannot deactivate the last active Admin.")
            
        self.conn.execute("UPDATE employees SET is_active = 0 WHERE id = ?", (employee_id,))
        self.conn.execute("INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
                          (actor.employee_id, "DEACTIVATE_EMPLOYEE", "Employee", employee_id))

    def reset_password(self, actor: Session, employee_id: int, new_password: str):
        require(actor, "employee.manage")
        emp = self.repo.get(employee_id)
        if not emp:
            raise ValidationError("Employee not found.")
            
        self._validate_password(new_password)
        password_hash = hash_password(new_password)
        
        self.conn.execute(
            "UPDATE employees SET password_hash = ?, failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (password_hash, employee_id)
        )
        self.conn.execute("INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
                          (actor.employee_id, "RESET_PASSWORD", "Employee", employee_id))
