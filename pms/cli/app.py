from pms.cli import console, supplier_menu, medicine_menu, inventory_menu, billing_menu
from pms.logger import get_logger
from pms.database import connect, transaction
from pms.services.auth_service import AuthService
from pms.models import Session
from pms.exceptions import PMSError

logger = get_logger(__name__)

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

