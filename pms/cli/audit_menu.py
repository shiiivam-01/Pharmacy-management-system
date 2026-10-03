"""
Audit log menu for Admin.
"""
import sqlite3
from pms.cli import console
from pms.models import Session
from pms.exceptions import PMSError
from pms.security import require

def show_menu(conn: sqlite3.Connection, actor: Session):
    require(actor, "audit.view") # Since this is admin only
    
    while True:
        print("\n--- Audit Log ---")
        print("1. View Recent Logs")
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        if choice == "1":
            _view_logs(conn)
        else:
            print("Invalid choice.")

def _view_logs(conn: sqlite3.Connection):
    limit = console.ask_int("Number of entries to view", required=False) or 20
    
    cursor = conn.execute(
        """
        SELECT a.id, e.username, a.action, a.entity, a.entity_id, a.details, a.created_at
        FROM audit_log a
        LEFT JOIN employees e ON a.employee_id = e.id
        ORDER BY a.id DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    if not rows:
        print("No audit logs found.")
        return
        
    headers = ["ID", "Time", "User", "Action", "Entity", "Entity ID", "Details"]
    table_rows = []
    for r in rows:
        table_rows.append([
            r["id"], r["created_at"], r["username"] or "-", r["action"],
            r["entity"] or "-", r["entity_id"] or "-", r["details"] or "-"
        ])
        
    console.print_table(headers, table_rows)
