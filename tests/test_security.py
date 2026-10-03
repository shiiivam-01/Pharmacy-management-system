import pytest
from pms.security import hash_password, verify_password, require, PERMISSIONS
from pms.exceptions import AuthorizationError

class DummySession:
    def __init__(self, role):
        self.role = role

def test_password_hashing():
    # Use low iterations for tests
    password = "MySecretPassword123"
    hash_str = hash_password(password, iterations=1000)
    
    assert hash_str.startswith("pbkdf2_sha256$1000$")
    assert verify_password(password, hash_str) is True
    assert verify_password("WrongPassword", hash_str) is False
    
    # Different salt for same password produces different hash
    hash_str2 = hash_password(password, iterations=1000)
    assert hash_str != hash_str2

def test_require_permission_granted():
    actor = DummySession(role="ADMIN")
    # Should not raise exception
    require(actor, "medicine.deactivate")

def test_require_permission_denied():
    actor = DummySession(role="PHARMACIST")
    with pytest.raises(AuthorizationError):
        require(actor, "medicine.deactivate")

def test_require_unknown_permission():
    actor = DummySession(role="ADMIN")
    with pytest.raises(AuthorizationError):
        require(actor, "some.fake.permission")
