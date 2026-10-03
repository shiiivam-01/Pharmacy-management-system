from pms.cli import console, supplier_menu, medicine_menu, inventory_menu, billing_menu
from pms.logger import get_logger
from pms.database import connect, transaction
from pms.services.auth_service import AuthService
from pms.services.alert_service import AlertService
from pms.models import Session
from pms.exceptions import PMSError

logger = get_logger(__name__)

def _show_dashboard(conn, session: Session):
    alert_service = AlertService(conn)
    summary = alert_service.get_dashboard_summary(session)
    
    print("\n--- Dashboard ---")
    print(f"1. Low Stock: {summary['low_stock_count']}")
    print(f"2. Expiring Soon: {summary['expiring_soon_count']}")
    print(f"3. Expired: {summary['expired_count']}")
    
    while True:
        choice = console.ask_text("Enter number to view list (or 0 to continue to menu)", required=False)
        if choice == "0" or choice == "":
            break
        elif choice == "1":
            low = alert_service.get_low_stock_medicines(session)
            if not low:
                print("No low stock medicines.")
            else:
                headers = ["Med ID", "Name", "Form", "Strength", "Reorder Level", "Available"]
                rows = [[m["id"], m["name"], m["form"], m["strength"], m["reorder_level"], m["available_stock"]] for m in low]
                console.print_table(headers, rows)
        elif choice == "2":
            soon = alert_service.get_expiring_soon_batches(session)
            if not soon:
                print("No batches expiring soon.")
            else:
                headers = ["Batch No", "Med Name", "Qty", "Expiry Date"]
                rows = [[b["batch_no"], b["name"], b["quantity"], b["expiry_date"]] for b in soon]
                console.print_table(headers, rows)
        elif choice == "3":
            expired = alert_service.get_expired_batches(session)
            if not expired:
                print("No expired batches.")
            else:
                headers = ["Batch No", "Med Name", "Qty", "Expiry Date"]
                rows = [[b["batch_no"], b["name"], b["quantity"], b["expiry_date"]] for b in expired]
                console.print_table(headers, rows)

def role_menu(conn, session: Session):
    while True:
        print(f"\n--- Main Menu ({session.role}) ---")
        print("1. Suppliers")
        print("2. Medicines")
        print("3. Inventory")
        print("4. Billing")
        if session.role == "ADMIN":
            print("5. Audit Log")
        print("0. Logout")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
        elif choice == "1":
            supplier_menu.show_menu(conn, session)
        elif choice == "2":
            medicine_menu.show_menu(conn, session)
        elif choice == "3":
            inventory_menu.show_menu(conn, session)
        elif choice == "4":
            billing_menu.show_menu(conn, session)
        elif choice == "5" and session.role == "ADMIN":
            from pms.cli import audit_menu
            audit_menu.show_menu(conn, session)
        else:
            print("Invalid choice.")

def run():
    logger.info("Application starting.")
    try:
        from pms.database import init_schema
        conn = connect()
        init_schema(conn)
        auth = AuthService(conn)
        
        # Bootstrap logic
        if auth.is_bootstrap_needed():
            print("\nWelcome! No users found. Let's create the first Admin.")
            name = console.ask_text("Full Name")
            user = console.ask_text("Username")
            pw = console.ask_text("Password")
            try:
                with transaction(conn):
                    auth.bootstrap(name, user, pw)
                print("Admin created successfully.")
            except PMSError as e:
                print(f"Failed: {e}")
                return

        # Login logic
        while True:
            print("\n--- Login (0 to exit) ---")
            user = console.ask_text("Username", required=True)
            if user == "0":
                break
            pw = console.ask_text("Password", required=True)
            try:
                with transaction(conn):
                    session = auth.login(user, pw)
                print(f"Welcome, {session.full_name} ({session.role})")
                
                # Show Dashboard
                _show_dashboard(conn, session)
                
                # Enter main menu
                role_menu(conn, session)
                
            except PMSError as e:
                print(str(e))
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\nSomething went wrong: {e}")
    finally:
        logger.info("Application stopped.")

