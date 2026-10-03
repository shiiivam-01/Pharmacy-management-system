"""
Inventory menu for the CLI.
"""
import sqlite3
from frontend.cli import console
from backend.models import Session
from backend.database import transaction
from backend.services.inventory_service import InventoryService
from backend.services.medicine_service import MedicineService
from backend.exceptions import PMSError

def show_menu(conn: sqlite3.Connection, actor: Session):
    inv_service = InventoryService(conn)
    med_service = MedicineService(conn)
    
    while True:
        print("\n--- Inventory ---")
        print("1. Receive Stock (New Batch)")
        print("2. View Batches for Medicine")
        if actor.role == "ADMIN":
            print("3. Adjust Stock")
            print("4. Write-off Expired Batch")
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        try:
            if choice == "1":
                _receive_stock(conn, inv_service, med_service, actor)
            elif choice == "2":
                _view_batches(inv_service, med_service, actor)
            elif choice == "3" and actor.role == "ADMIN":
                _adjust_stock(conn, actor, inv_service)
            elif choice == "4" and actor.role == "ADMIN":
                _write_off_expired(conn, actor, inv_service)
            else:
                print("Invalid choice.")
        except PMSError as e:
            print(f"Error: {e}")

def _receive_stock(conn: sqlite3.Connection, inv_service: InventoryService, med_service: MedicineService, actor: Session):
    print("\n[Receive Stock]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    
    med = med_service.get_medicine(actor, med_id)
    print(f"Receiving stock for: {med.name} ({med.form} {med.strength})")
    
    batch_no = console.ask_text("Batch Number", required=True)
    qty = console.ask_int("Quantity", required=True)
    price = console.ask_decimal("Purchase Price", required=True)
    expiry = console.ask_date("Expiry Date", required=True)
    
    sup_id = console.ask_int("Supplier ID", required=False)
    
    with transaction(conn):
        batch = inv_service.receive_stock(
            actor, med_id, batch_no, qty, price,
            expiry.isoformat() if expiry else None, sup_id
        )
    print(f"Batch '{batch.batch_no}' received successfully.")

def _view_batches(inv_service: InventoryService, med_service: MedicineService, actor: Session):
    print("\n[View Batches]")
    med_id = console.ask_int("Enter Medicine ID", required=True)
    med = med_service.get_medicine(actor, med_id)
    
    available_only = console.confirm("Show available batches only?")
    batches = inv_service.list_batches(actor, med_id, available_only=available_only)
    
    if not batches:
        print("No batches found.")
        return
        
    print(f"\nBatches for {med.name}:")
    headers = ["ID", "Batch No", "Qty", "Expiry", "Days to Expiry"]
    rows = []
    for b in batches:
        rows.append([b.id, b.batch_no, b.quantity, b.expiry_date, b.days_to_expiry])
    console.print_table(headers, rows)

def _adjust_stock(conn: sqlite3.Connection, actor: Session, inv_service: InventoryService):
    print("\n[Adjust Stock]")
    batch_id = console.ask_int("Batch ID to adjust", required=True)
    new_qty = console.ask_int("New Quantity", required=True)
    reason = console.ask_choice("Reason", ["DAMAGED", "LOST", "CORRECTION"])
    note = console.ask_text("Note", required=False)
    
    with transaction(conn):
        batch = inv_service.adjust_stock(actor, batch_id, new_qty, reason, note)
    print(f"Success! Batch '{batch.batch_no}' quantity adjusted to {batch.quantity}.")

def _write_off_expired(conn: sqlite3.Connection, actor: Session, inv_service: InventoryService):
    print("\n[Write-off Expired Batch]")
    batch_id = console.ask_int("Batch ID to write-off", required=True)
    if not console.confirm(f"Are you sure you want to write-off batch {batch_id}?"):
        return
        
    with transaction(conn):
        batch = inv_service.write_off_expired(actor, batch_id)
    print(f"Success! Batch '{batch.batch_no}' written off.")
