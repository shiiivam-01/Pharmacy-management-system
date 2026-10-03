"""
Pytest configuration and shared fixtures for the Pharmacy Management System.
"""
import pytest
from datetime import date
from backend import config
from backend.database import connect, init_schema
from backend.models import Session

# Lower PBKDF2 iterations for fast testing
config.PBKDF2_ITERATIONS = 1000

@pytest.fixture
def db():
    """Provides an initialized in-memory database connection."""
    conn = connect(":memory:")
    init_schema(conn)
    conn.execute("INSERT INTO employees (id, full_name, role, username, password_hash) VALUES (1, 'Test Admin', 'ADMIN', 'admin', 'dummy_hash')")
    conn.execute("INSERT INTO employees (id, full_name, role, username, password_hash) VALUES (2, 'Test Pharmacist', 'PHARMACIST', 'pharmacist', 'dummy_hash')")
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def admin():
    """Provides a dummy Admin session."""
    return Session(employee_id=1, username="admin", role="ADMIN", full_name="Test Admin")

@pytest.fixture
def pharmacist():
    """Provides a dummy Pharmacist session."""
    return Session(employee_id=2, username="pharmacist", role="PHARMACIST", full_name="Test Pharmacist")

@pytest.fixture
def today():
    """Provides a fixed date for tests."""
    return date(2026, 10, 3)

@pytest.fixture
def sample_medicine():
    """Placeholder for sample medicine fixture"""
    pass

@pytest.fixture
def sample_batches():
    """Placeholder for sample batches fixture"""
    pass
