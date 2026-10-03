import pytest
from pms.services.auth_service import AuthService
from pms.exceptions import AuthenticationError, PMSError, ValidationError

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
