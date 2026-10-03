import sqlite3
from contextlib import contextmanager
from pathlib import Path
from backend import config

def connect(db_path: str = None) -> sqlite3.Connection:
    """Creates a connection to the SQLite database with enforced settings."""
    if db_path is None:
        db_path = str(config.DB_PATH)
    
    # Connect
    conn = sqlite3.connect(db_path)
    # Enable foreign keys and use Row factory
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_schema(conn: sqlite3.Connection) -> None:
    """Initializes the database schema if not already present."""
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)

@contextmanager
def transaction(conn: sqlite3.Connection):
    """
    Context manager for atomic database transactions.
    Rolls back on error and re-raises.
    """
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
