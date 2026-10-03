"""
Authentication service.
"""
import sqlite3
from pms.models import Session
from pms.repositories.employee_repository import EmployeeRepository
from pms.security import hash_password, verify_password
from pms.exceptions import AuthenticationError, PMSError, ValidationError

class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = EmployeeRepository(conn)

    def is_bootstrap_needed(self) -> bool:
        return self.repo.count() == 0

    def bootstrap(self, full_name: str, username: str, password: str) -> None:
        """Creates the first Admin account."""
        if not self.is_bootstrap_needed():
            raise PMSError("System is already bootstrapped.")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
            
        password_hash = hash_password(password)
        self.repo.add(full_name, None, "ADMIN", username, password_hash)
        
    def login(self, username: str, password: str, now=None) -> Session:
        """
        Authenticates a user and returns a Session.
        Raises AuthenticationError on failure or lockout.
        """
        if now is None:
            from datetime import datetime
            now = datetime.now()
            
        user = self.repo.get_by_username(username)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid username or password")
            
        if user.locked_until:
            from datetime import datetime
            try:
                locked_until_dt = datetime.fromisoformat(user.locked_until)
                if now < locked_until_dt:
                    raise AuthenticationError("Account is locked due to too many failed attempts.")
            except ValueError:
                pass
            
        if not verify_password(password, user.password_hash):
            from pms.config import LOCKOUT_ATTEMPTS, LOCKOUT_MINUTES
            from datetime import timedelta
            
            new_attempts = user.failed_attempts + 1
            lock_until = None
            if new_attempts >= LOCKOUT_ATTEMPTS:
                lock_until = (now + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
                
            self.repo.record_failed_login(user.id, lock_until)
            raise AuthenticationError("Invalid username or password")
            
        self.repo.reset_failed_logins(user.id)
        
        return Session(
            employee_id=user.id,
            username=user.username,
            role=user.role,
            full_name=user.full_name
        )

    def change_password(self, actor: Session, current_password: str, new_password: str):
        user = self.repo.get(actor.employee_id)
        if not user:
            raise ValidationError("User not found.")
            
        if not verify_password(current_password, user.password_hash):
            raise ValidationError("Current password is incorrect.")
            
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long.")
            
        if verify_password(new_password, user.password_hash):
            raise ValidationError("New password must be different from the old one.")
            
        password_hash = hash_password(new_password)
        self.conn.execute("UPDATE employees SET password_hash = ? WHERE id = ?", (password_hash, actor.employee_id))
        self.conn.execute("INSERT INTO audit_log (employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?)",
                          (actor.employee_id, "CHANGE_PASSWORD", "Employee", actor.employee_id))
