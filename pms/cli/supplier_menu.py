"""
Supplier menu for the CLI.
"""
import sqlite3
from pms.cli import console
from pms.models import Session
from pms.database import transaction
from pms.services.supplier_service import SupplierService
from pms.exceptions import PMSError

def show_menu(conn: sqlite3.Connection, actor: Session):
    service = SupplierService(conn)
    
    while True:
        print("\n--- Suppliers ---")
        if actor.role == "ADMIN":
            print("1. Add supplier")
            print("2. List suppliers")
            print("3. Update supplier")
            print("4. Deactivate supplier")
        else:
            print("1. List suppliers")
            
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        try:
            if choice == "1" and actor.role == "ADMIN":
                _add_supplier(conn, service, actor)
            elif choice == "1" and actor.role != "ADMIN" or choice == "2" and actor.role == "ADMIN":
                _list_suppliers(service, actor)
            elif choice == "3" and actor.role == "ADMIN":
                _update_supplier(conn, service, actor)
            elif choice == "4" and actor.role == "ADMIN":
                _deactivate_supplier(conn, service, actor)
            else:
                print("Invalid choice.")
        except PMSError as e:
            print(f"Error: {e}")

def _add_supplier(conn: sqlite3.Connection, service: SupplierService, actor: Session):
    print("\n[Add Supplier]")
    name = console.ask_text("Name", required=True)
    contact = console.ask_text("Contact Person", required=False)
    phone = console.ask_text("Phone", required=False)
    email = console.ask_text("Email", required=False)
    address = console.ask_text("Address", required=False)
    
    with transaction(conn):
        sup = service.add_supplier(actor, name, contact, phone, email, address)
    print(f"Supplier '{sup.name}' added successfully (ID: {sup.id}).")

def _list_suppliers(service: SupplierService, actor: Session):
    print("\n[Supplier List]")
    active_only = actor.role != "ADMIN"
    suppliers = service.list_suppliers(actor, active_only=active_only)
    
    if not suppliers:
        print("No suppliers found.")
        return
        
    headers = ["ID", "Name", "Contact", "Phone", "Medicines Linked", "Active"]
    rows = []
    for s in suppliers:
        rows.append([
            s.id, s.name, s.contact_person or "-", s.phone or "-", s.medicine_count, "Yes" if s.is_active else "No"
        ])
    console.print_table(headers, rows)

def _update_supplier(conn: sqlite3.Connection, service: SupplierService, actor: Session):
    print("\n[Update Supplier]")
    sup_id = console.ask_int("Enter Supplier ID to update")
    if sup_id is None:
        return
        
    sup = service.get_supplier(actor, sup_id)
    print(f"Updating '{sup.name}'. Leave fields blank to keep current values.")
    
    name = console.ask_text(f"Name [{sup.name}]", required=False) or sup.name
    contact = console.ask_text(f"Contact Person [{sup.contact_person or '-'}]", required=False) or sup.contact_person
    phone = console.ask_text(f"Phone [{sup.phone or '-'}]", required=False) or sup.phone
    email = console.ask_text(f"Email [{sup.email or '-'}]", required=False) or sup.email
    address = console.ask_text(f"Address [{sup.address or '-'}]", required=False) or sup.address
    
    with transaction(conn):
        service.update_supplier(actor, sup_id, name, contact, phone, email, address)
    print("Supplier updated successfully.")

def _deactivate_supplier(conn: sqlite3.Connection, service: SupplierService, actor: Session):
    print("\n[Deactivate Supplier]")
    sup_id = console.ask_int("Enter Supplier ID to deactivate")
    if sup_id is None:
        return
        
    sup = service.get_supplier(actor, sup_id)
    if not sup.is_active:
        print("Supplier is already inactive.")
        return
        
    if console.confirm(f"Are you sure you want to deactivate '{sup.name}'?"):
        with transaction(conn):
            service.deactivate_supplier(actor, sup_id)
        print("Supplier deactivated.")
