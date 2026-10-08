"""
Authentication service.
"""
import sqlite3
from backend.models import Session
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.store_repository import StoreRepository
from backend.security import hash_password, verify_password
from backend.exceptions import AuthenticationError, PMSError, ValidationError

class AuthService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = EmployeeRepository(conn)
        self.store_repo = StoreRepository(conn)

    def register_store(self, store_name: str, owner_name: str, location: str, email: str, password: str):
        """Creates a new store and the first Admin account."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
            
        if self.repo.get_by_username(email):
            raise ValidationError("Email (username) already registered.")

        # BEGIN IMMEDIATE ensures safe transaction for both store and employee
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            store = self.store_repo.add(store_name, owner_name, location)
            password_hash = hash_password(password)
            self.repo.add(store.id, owner_name, None, "ADMIN", email, password_hash)
            self.conn.execute("COMMIT")
            return store
        except Exception as e:
            self.conn.execute("ROLLBACK")
            raise e

    def register_employee(self, store_uid: str, full_name: str, email: str, password: str):
        """Registers a new Pharmacist by joining an existing store."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
            
        if self.repo.get_by_username(email):
            raise ValidationError("Email (username) already registered.")

        store = self.store_repo.get_by_uid(store_uid)
        if not store:
            raise ValidationError("Invalid Store UID. Store not found.")

        self.conn.execute("BEGIN IMMEDIATE")
        try:
            password_hash = hash_password(password)
            self.repo.add(store.id, full_name, None, "PHARMACIST", email, password_hash)
            self.conn.execute("COMMIT")
            return store
        except Exception as e:
            self.conn.execute("ROLLBACK")
            raise e

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
            from backend.config import LOCKOUT_ATTEMPTS, LOCKOUT_MINUTES
            from datetime import timedelta
            
            new_attempts = user.failed_attempts + 1
            lock_until = None
            if new_attempts >= LOCKOUT_ATTEMPTS:
                lock_until = (now + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
                
            self.repo.record_failed_login(user.id, lock_until)
            raise AuthenticationError("Invalid username or password")
            
        self.repo.reset_failed_logins(user.id)
        
        store = self.store_repo.get(user.store_id)
        return Session(
            employee_id=user.id,
            store_id=user.store_id,
            store_name=store.name,
            username=user.username,
            role=user.role,
            full_name=user.full_name
        )

    def change_password(self, actor: Session, current_password: str, new_password: str):
        user = self.repo.get(actor.store_id, actor.employee_id)
        if not user:
            raise ValidationError("User not found.")
            
        if not verify_password(current_password, user.password_hash):
            raise ValidationError("Current password is incorrect.")
            
        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long.")
            
        if verify_password(new_password, user.password_hash):
            raise ValidationError("New password must be different from the old one.")
            
        password_hash = hash_password(new_password)
        self.conn.execute("UPDATE employees SET password_hash = ? WHERE store_id = ? AND id = ?", (password_hash, actor.store_id, actor.employee_id))
        self.conn.execute("INSERT INTO audit_log (store_id, employee_id, action, entity, entity_id) VALUES (?, ?, ?, ?, ?)",
                          (actor.store_id, actor.employee_id, "CHANGE_PASSWORD", "Employee", actor.employee_id))
