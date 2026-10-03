import sqlite3
from frontend.cli import console
from backend.models import Session
from backend.services.employee_service import EmployeeService
from backend.exceptions import PMSError
from backend.database import transaction

def show_menu(conn: sqlite3.Connection, actor: Session):
    emp_service = EmployeeService(conn)
    
    while True:
        print("\n--- Employee Management ---")
        print("1. Add Employee")
        print("2. List Employees")
        print("3. Update Employee")
        print("4. Deactivate Employee")
        print("5. Reset Password")
        print("0. Back")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
        elif choice == "1":
            _add_employee(conn, actor, emp_service)
        elif choice == "2":
            _list_employees(actor, emp_service)
        elif choice == "3":
            _update_employee(conn, actor, emp_service)
        elif choice == "4":
            _deactivate_employee(conn, actor, emp_service)
        elif choice == "5":
            _reset_password(conn, actor, emp_service)
        else:
            print("Invalid choice.")

def _add_employee(conn: sqlite3.Connection, actor: Session, service: EmployeeService):
    print("\n[Add Employee]")
    name = console.ask_text("Full Name", required=True)
    phone = console.ask_text("Phone", required=False)
    role = console.ask_choice("Role", ["ADMIN", "PHARMACIST"])
    user = console.ask_text("Username", required=True)
    pw = console.ask_text("Initial Password", required=True)
    
    try:
        with transaction(conn):
            emp = service.add_employee(actor, name, phone, role, user, pw)
        print(f"Success! Employee '{emp.full_name}' added with ID {emp.id}.")
    except PMSError as e:
        print(f"Failed: {e}")

def _list_employees(actor: Session, service: EmployeeService):
    print("\n[List Employees]")
    try:
        employees = service.list_employees(actor)
        if not employees:
            print("No employees found.")
            return
            
        headers = ["ID", "Name", "Role", "Username", "Active"]
        rows = [[e.id, e.full_name, e.role, e.username, "Yes" if e.is_active else "No"] for e in employees]
        console.print_table(headers, rows)
    except PMSError as e:
        print(f"Failed: {e}")

def _update_employee(conn: sqlite3.Connection, actor: Session, service: EmployeeService):
    print("\n[Update Employee]")
    emp_id = console.ask_int("Employee ID to update", required=True)
    name = console.ask_text("New Full Name", required=True)
    phone = console.ask_text("New Phone", required=False)
    role = console.ask_choice("New Role", ["ADMIN", "PHARMACIST"])
    
    try:
        with transaction(conn):
            emp = service.update_employee(actor, emp_id, name, phone, role)
        print(f"Success! Employee {emp.id} updated.")
    except PMSError as e:
        print(f"Failed: {e}")

def _deactivate_employee(conn: sqlite3.Connection, actor: Session, service: EmployeeService):
    print("\n[Deactivate Employee]")
    emp_id = console.ask_int("Employee ID to deactivate", required=True)
    if not console.confirm(f"Are you sure you want to deactivate employee {emp_id}?"):
        return
        
    try:
        with transaction(conn):
            service.deactivate_employee(actor, emp_id)
        print(f"Success! Employee {emp_id} deactivated.")
    except PMSError as e:
        print(f"Failed: {e}")

def _reset_password(conn: sqlite3.Connection, actor: Session, service: EmployeeService):
    print("\n[Reset Employee Password]")
    emp_id = console.ask_int("Employee ID", required=True)
    pw = console.ask_text("New Password", required=True)
    
    try:
        with transaction(conn):
            service.reset_password(actor, emp_id, pw)
        print(f"Success! Password for employee {emp_id} reset.")
    except PMSError as e:
        print(f"Failed: {e}")
