"""
Security utilities and permission definitions for the Pharmacy Management System.
"""
import os
import hashlib
import hmac
from backend import config
from backend.exceptions import AuthorizationError

PERMISSIONS = {
    "medicine.view":        {"ADMIN", "PHARMACIST"},
    "medicine.write":       {"ADMIN"},
    "medicine.deactivate":  {"ADMIN"},
    "supplier.view":        {"ADMIN", "PHARMACIST"},
    "supplier.write":       {"ADMIN"},
    "inventory.receive":    {"ADMIN", "PHARMACIST"},
    "inventory.adjust":     {"ADMIN"},
    "sale.create":          {"ADMIN", "PHARMACIST"},
    "sale.view_all":        {"ADMIN"},
    "sale.void":            {"ADMIN"},
    "discount.unlimited":   {"ADMIN"},
    "report.admin":         {"ADMIN"},
    "employee.manage":      {"ADMIN"},
    "audit.view":           {"ADMIN"},
}

def hash_password(password: str, iterations: int = None) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256.
    Returns format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    if iterations is None:
        iterations = config.PBKDF2_ITERATIONS
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt.hex()}${hash_bytes.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a password against a stored hash using constant-time comparison.
    """
    try:
        algorithm, iterations_str, salt_hex, hash_hex = stored_hash.split('$')
        if algorithm != 'pbkdf2_sha256':
            return False
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations
        )
        return hmac.compare_digest(expected_hash, computed_hash)
    except (ValueError, AttributeError):
        return False

def require(actor, permission: str) -> None:
    """
    Checks if the actor's role has the required permission.
    Raises AuthorizationError if not.
    """
    if permission not in PERMISSIONS:
        raise AuthorizationError(f"Unknown permission: {permission}")
        
    allowed_roles = PERMISSIONS[permission]
    
    if getattr(actor, 'role', None) not in allowed_roles:
        raise AuthorizationError(f"Role '{getattr(actor, 'role', None)}' does not have permission '{permission}'")
