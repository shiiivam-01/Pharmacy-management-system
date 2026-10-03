import pytest
import sqlite3
from backend.database import connect, init_schema, transaction

def test_database_connection_and_schema():
    # Use in-memory for testing
    conn = connect(":memory:")
    
    # Foreign keys should be ON
    cursor = conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1
    
    init_schema(conn)
    
    # Check user_version is 1
    cursor = conn.execute("PRAGMA user_version;")
    assert cursor.fetchone()[0] == 1
    
    # Check if a table exists
    cursor = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='employees';")
    assert cursor.fetchone()[0] == 1

def test_transaction_commit():
    conn = connect(":memory:")
    init_schema(conn)
    
    with transaction(conn):
        conn.execute(
            "INSERT INTO employees (full_name, role, username, password_hash) VALUES (?, ?, ?, ?)",
            ("Test User", "ADMIN", "test_admin", "hash")
        )
    
    # The insert should be committed
    cursor = conn.execute("SELECT count(*) FROM employees;")
    assert cursor.fetchone()[0] == 1

def test_transaction_rollback():
    conn = connect(":memory:")
    init_schema(conn)
    
    with pytest.raises(ValueError):
        with transaction(conn):
            conn.execute(
                "INSERT INTO employees (full_name, role, username, password_hash) VALUES (?, ?, ?, ?)",
                ("Test User 2", "ADMIN", "test_admin2", "hash")
            )
            raise ValueError("Something went wrong")
    
    # The insert should be rolled back
    cursor = conn.execute("SELECT count(*) FROM employees;")
    assert cursor.fetchone()[0] == 0
