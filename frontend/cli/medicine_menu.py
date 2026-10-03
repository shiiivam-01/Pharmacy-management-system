"""
Medicine menu for the CLI.
"""
import sqlite3
from decimal import Decimal
from frontend.cli import console
from backend.models import Session
from backend.database import transaction
from backend.services.medicine_service import MedicineService
from backend.money import to_decimal
from backend.exceptions import PMSError

def show_menu(conn: sqlite3.Connection, actor: Session):
    service = MedicineService(conn)
    
    while True:
        print("\n--- Medicines ---")
        if actor.role == "ADMIN":
            print("1. Add medicine")
            print("2. List/Search medicines")
            print("3. View medicine details")
            print("4. Update medicine")
            print("5. Deactivate medicine")
            print("6. Reactivate medicine")
        else:
            print("1. List/Search medicines")
            print("2. View medicine details")
            
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        try:
            if choice == "1" and actor.role == "ADMIN":
                _add_medicine(conn, service, actor)
            elif choice == "2" and actor.role == "ADMIN" or choice == "1" and actor.role != "ADMIN":
                _list_search_medicines(service, actor)
            elif choice == "3" and actor.role == "ADMIN" or choice == "2" and actor.role != "ADMIN":
                _view_medicine(service, actor)
            elif choice == "4" and actor.role == "ADMIN":
                _update_medicine(conn, service, actor)
            elif choice == "5" and actor.role == "ADMIN":
                _deactivate_medicine(conn, service, actor)
            elif choice == "6" and actor.role == "ADMIN":
                _reactivate_medicine(conn, service, actor)
            else:
                print("Invalid choice.")
        except PMSError as e:
            print(f"Error: {e}")

def _add_medicine(conn: sqlite3.Connection, service: MedicineService, actor: Session):
    print("\n[Add Medicine]")
    name = console.ask_text("Name", required=True)
    form = console.ask_text("Form (e.g. tablet, syrup)", required=True)
    strength = console.ask_text("Strength (e.g. 500mg)", required=False) or ""
    generic = console.ask_text("Generic Name", required=False)
    cat = console.ask_text("Category", required=False)
    mfg = console.ask_text("Manufacturer", required=False)
    
    sup_id = console.ask_int("Supplier ID", required=False)
    
    price = console.ask_decimal("Unit Price (excl. tax)", required=True)
    tax = console.ask_decimal("Tax Percent", required=True)
    
    reorder = console.ask_int("Reorder Level", required=True, allow_zero=True)
    rx = console.confirm("Requires Prescription?")
    
    with transaction(conn):
        med = service.add_medicine(
            actor, name=name, form=form, strength=strength, unit_price=price,
            tax_percent=float(tax), reorder_level=reorder, requires_prescription=rx,
            generic_name=generic, category=cat, manufacturer=mfg, supplier_id=sup_id
        )
    print(f"Medicine '{med.name}' added successfully (ID: {med.id}).")

def _list_search_medicines(service: MedicineService, actor: Session):
    print("\n[List/Search Medicines]")
    query = console.ask_text("Enter search query (leave blank for all)", required=False)
    
    category = console.ask_text("Filter by Category (leave blank for any)", required=False)
    sup_id_str = console.ask_text("Filter by Supplier ID (leave blank for any)", required=False)
    supplier_id = int(sup_id_str) if sup_id_str.isdigit() else None
    
    active_only = actor.role != "ADMIN"
    
    meds = service.search_medicines(
        actor, query, active_only=active_only, category=category, supplier_id=supplier_id
    )
    if not meds:
        print("No medicines found.")
        return
        
    headers = ["ID", "Name", "Form", "Strength", "Stock", "Price", "Rx", "Active"]
    rows = []
    for m in meds:
        rows.append([
            m.id, m.name, m.form, m.strength, m.available_stock,
            to_decimal(m.unit_price_minor), "Yes" if m.requires_prescription else "No",
            "Yes" if m.is_active else "No"
        ])
    console.print_table(headers, rows)

def _view_medicine(service: MedicineService, actor: Session):
    print("\n[View Medicine]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    med = service.get_medicine(actor, med_id)
    
    print(f"\n--- {med.name} (ID: {med.id}) ---")
    print(f"Generic Name: {med.generic_name or '-'}")
    print(f"Form: {med.form} | Strength: {med.strength}")
    print(f"Category: {med.category or '-'}")
    print(f"Manufacturer: {med.manufacturer or '-'}")
    print(f"Supplier ID: {med.supplier_id or '-'}")
    print(f"Unit Price: {to_decimal(med.unit_price_minor)} | Tax: {med.tax_percent}%")
    print(f"Available Stock: {med.available_stock}")
    print(f"Reorder Level: {med.reorder_level}")
    print(f"Requires Prescription: {'Yes' if med.requires_prescription else 'No'}")
    print(f"Active: {'Yes' if med.is_active else 'No'}")

def _update_medicine(conn: sqlite3.Connection, service: MedicineService, actor: Session):
    print("\n[Update Medicine]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    med = service.get_medicine(actor, med_id)
    
    print(f"Updating '{med.name}'. Leave fields blank to keep current values.")
    
    name = console.ask_text(f"Name [{med.name}]", required=False) or med.name
    form = console.ask_text(f"Form [{med.form}]", required=False) or med.form
    strength = console.ask_text(f"Strength [{med.strength}]", required=False) or med.strength
    generic = console.ask_text(f"Generic [{med.generic_name or '-'}]", required=False) or med.generic_name
    cat = console.ask_text(f"Category [{med.category or '-'}]", required=False) or med.category
    mfg = console.ask_text(f"Manufacturer [{med.manufacturer or '-'}]", required=False) or med.manufacturer
    
    sup_id_str = console.ask_text(f"Supplier ID [{med.supplier_id or '-'}]", required=False)
    sup_id = int(sup_id_str) if sup_id_str.isdigit() else med.supplier_id
    
    price_val = console.ask_text(f"Unit Price [{to_decimal(med.unit_price_minor)}]", required=False)
    price = Decimal(price_val) if price_val else to_decimal(med.unit_price_minor)
    
    tax_val = console.ask_text(f"Tax % [{med.tax_percent}]", required=False)
    tax = float(tax_val) if tax_val else med.tax_percent
    
    reorder_val = console.ask_text(f"Reorder Level [{med.reorder_level}]", required=False)
    reorder = int(reorder_val) if reorder_val and reorder_val.isdigit() else med.reorder_level
    
    rx_str = console.ask_choice(f"Requires Rx? (Y/N) [{'Y' if med.requires_prescription else 'N'}]", ["Y", "N", ""])
    if rx_str == "":
        rx = bool(med.requires_prescription)
    else:
        rx = rx_str == "Y"
        
    with transaction(conn):
        service.update_medicine(
            actor, med_id, name=name, form=form, strength=strength,
            unit_price=price, tax_percent=tax, reorder_level=reorder,
            requires_prescription=rx, generic_name=generic, category=cat,
            manufacturer=mfg, supplier_id=sup_id
        )
    print("Medicine updated successfully.")

def _deactivate_medicine(conn: sqlite3.Connection, service: MedicineService, actor: Session):
    print("\n[Deactivate Medicine]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    med = service.get_medicine(actor, med_id)
    
    if not med.is_active:
        print("Medicine is already inactive.")
        return
        
    if console.confirm(f"Are you sure you want to deactivate '{med.name}'?"):
        with transaction(conn):
            service.deactivate_medicine(actor, med_id)
        print("Medicine deactivated.")

def _reactivate_medicine(conn: sqlite3.Connection, service: MedicineService, actor: Session):
    print("\n[Reactivate Medicine]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    med = service.get_medicine(actor, med_id)
    
    if med.is_active:
        print("Medicine is already active.")
        return
        
    if console.confirm(f"Are you sure you want to reactivate '{med.name}'?"):
        with transaction(conn):
            service.reactivate_medicine(actor, med_id)
        print("Medicine reactivated.")
