"""
Test that the basic db fixture works as expected.
"""
def test_db_fixture(db):
    # Verify the database has the employees table created
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees';")
    assert cursor.fetchone() is not None
