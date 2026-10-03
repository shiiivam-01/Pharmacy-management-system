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
        
    def login(self, username: str, password: str) -> Session:
        """
        Authenticates a user and returns a Session.
        Raises AuthenticationError on failure.
        """
        user = self.repo.get_by_username(username)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid username or password")
            
        if not verify_password(password, user.password_hash):
            self.repo.record_failed_login(user.id)
            raise AuthenticationError("Invalid username or password")
            
        self.repo.reset_failed_logins(user.id)
        
        return Session(
            employee_id=user.id,
            username=user.username,
            role=user.role,
            full_name=user.full_name
        )
