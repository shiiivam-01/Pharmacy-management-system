import pytest
from pms.services.auth_service import AuthService
from pms.exceptions import AuthenticationError, PMSError, ValidationError
from pms.models import Session

def test_bootstrap_and_login(db):
    db.execute("DELETE FROM employees")
    db.commit()
    service = AuthService(db)
    
    assert service.is_bootstrap_needed() is True
    
    # Needs valid password length
    with pytest.raises(ValidationError):
        service.bootstrap("Admin", "admin", "short")
        
    service.bootstrap("Admin", "admin", "password123")
    assert service.is_bootstrap_needed() is False
    
    # Cannot bootstrap twice
    with pytest.raises(PMSError):
        service.bootstrap("Admin2", "admin2", "password123")
        
    # Login success
    session = service.login("admin", "password123")
    assert session.username == "admin"
    assert session.role == "ADMIN"
    
    # Login failure
    with pytest.raises(AuthenticationError):
        service.login("admin", "wrongpassword")
        
    # User not found
    with pytest.raises(AuthenticationError):
        service.login("unknown", "password")

def test_change_password(db, admin):
    service = AuthService(db)
    
    # We need a user with a valid password hash, because the fixture has dummy_hash
    from pms.security import hash_password
    pw_hash = hash_password("oldpassword")
    db.execute("INSERT INTO employees (full_name, role, username, password_hash) VALUES ('Real', 'ADMIN', 'real_admin', ?)", (pw_hash,))
    real_admin_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    real_session = Session(employee_id=real_admin_id, username="real_admin", role="ADMIN", full_name="Real")
    
    # Wrong current password
    with pytest.raises(ValidationError, match="Current password is incorrect"):
        service.change_password(real_session, "wrongpw", "newpassword123")
        
    # Short new password
    with pytest.raises(ValidationError, match="at least 8 characters"):
        service.change_password(real_session, "oldpassword", "short")
        
    # Same as old
    with pytest.raises(ValidationError, match="must be different"):
        service.change_password(real_session, "oldpassword", "oldpassword")
        
    # Success
    service.change_password(real_session, "oldpassword", "newpassword123")
    
    # Verify login with new password
    session = service.login("real_admin", "newpassword123")
    assert session.username == "real_admin"
    
    # Old password no longer works
    with pytest.raises(AuthenticationError):
        service.login("real_admin", "oldpassword")
