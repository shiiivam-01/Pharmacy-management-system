"""
Billing menu and bill rendering.
"""
import sqlite3
import os
from decimal import Decimal
from typing import List
from frontend.cli import console
from backend.models import Session, CartLine, Sale
from backend.database import transaction
from backend.services.billing_service import BillingService
from backend.services.medicine_service import MedicineService
from backend.money import to_decimal
from backend.exceptions import PMSError

def show_menu(conn: sqlite3.Connection, actor: Session):
    billing = BillingService(conn)
    med_service = MedicineService(conn)
    
    while True:
        print("\n--- Billing ---")
        print("1. New Sale")
        print("2. Sales History / Reprint Bill")
        if actor.role == "ADMIN":
            print("3. Void Sale")
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        try:
            if choice == "1":
                _new_sale(conn, billing, med_service, actor)
            elif choice == "2":
                _sales_history(billing, actor)
            elif choice == "3" and actor.role == "ADMIN":
                _void_sale(conn, billing, actor)
            else:
                print("Invalid choice.")
        except PMSError as e:
            print(f"Error: {e}")

def _new_sale(conn: sqlite3.Connection, billing: BillingService, med_service: MedicineService, actor: Session):
    print("\n[New Sale]")
    cart: List[CartLine] = []
    
    while True:
        action = console.ask_choice("Action (Add item, Finish, Cancel) [A/F/C]", ["A", "F", "C"])
        if action == "C":
            print("Sale cancelled.")
            return
        if action == "F":
            if not cart:
                print("Cart is empty. Please add items or cancel.")
                continue
            break
            
        if action == "A":
            query = console.ask_text("Search medicine (name/generic)")
            if not query:
                continue
            meds = med_service.search_medicines(actor, query, active_only=True)
            if not meds:
                print("No active medicines found.")
                continue
                
            for m in meds:
                print(f"ID: {m.id} | {m.name} {m.form} {m.strength} | Price: {to_decimal(m.unit_price_minor)} | Stock: {m.available_stock}")
                
            med_id = console.ask_int("Enter Medicine ID to add (or 0 to cancel)", required=True, allow_zero=True)
            if med_id == 0:
                continue
                
            qty = console.ask_int("Quantity", required=True)
            if qty <= 0:
                print("Quantity must be positive.")
                continue
                
            try:
                cart = billing.add_to_cart(actor, cart, med_id, qty)
                print("Added to cart.")
            except PMSError as e:
                print(f"Error: {e}")
                
    # Finish sale
    totals = billing.calculate_totals(cart, 0.0)
    print("\n--- Cart Preview ---")
    for item in cart:
        print(f"{item.medicine_name} | Qty: {item.quantity} | Total: {to_decimal(item.quantity * item.unit_price_minor)}")
    print(f"Subtotal: {to_decimal(totals['subtotal'])}")
    
    customer = console.ask_text("Customer Name (optional)", required=False)
    rx = console.ask_text("Prescription Note (optional)", required=False)
    discount = float(console.ask_decimal("Discount Percent [0.0]", required=False) or 0.0)
    
    pmt = console.ask_choice("Payment Method (CASH/CARD/UPI) [CASH]", ["CASH", "CARD", "UPI", ""])
    if not pmt: pmt = "CASH"
    
    # Re-calculate totals with discount
    try:
        totals = billing.calculate_totals(cart, discount)
    except PMSError as e:
        print(f"Error: {e}")
        return
        
    print(f"\nFINAL TOTAL: {to_decimal(totals['total'])}")
    
    requires_rx = any(item.requires_prescription for item in cart)
    if requires_rx:
        print("\nWARNING: This sale contains prescription medicines!")
        if not console.confirm("Has a valid prescription been verified?"):
            print("Sale cancelled (Prescription required).")
            return
            
    if not console.confirm("Confirm sale?"):
        print("Sale cancelled.")
        return
        
    try:
        with transaction(conn):
            sale = billing.create_sale(actor, cart, customer, rx, discount, pmt)
    except PMSError as e:
        print(f"Error creating sale: {e}")
        return
        
    _render_and_save_bill(billing, sale, cart)
    print("Sale completed.")

def _render_and_save_bill(billing: BillingService, sale: Sale, cart: List[CartLine] = None):
    # Fetch items if cart not provided (e.g. for past bills)
    items_to_render = []
    if cart:
        for c in cart:
            items_to_render.append((c.medicine_name, c.quantity, c.unit_price_minor, c.quantity * c.unit_price_minor))
    else:
        sale_items = billing.sale_repo.get_sale_items(sale.id)
        # We need medicine names. Let's fetch them, or just use IDs if lazy.
        # Actually, for past bills we should look up medicine names via med_repo.
        for si in sale_items:
            med = billing.med_repo.get(si.medicine_id)
            med_name = f"{med.name} {med.form} {med.strength}".strip() if med else f"Med {si.medicine_id}"
            items_to_render.append((med_name, si.quantity, si.unit_price_minor, si.line_total_minor))

    lines = []
    lines.append("========================================")
    lines.append("             PHARMACY INC               ")
    lines.append("========================================")
    lines.append(f"Bill No : {sale.bill_no}")
    lines.append(f"Date    : {sale.created_at}")
    # Cashier name would require Employee lookup. Let's just use Employee ID or "Cashier".
    lines.append(f"Cashier : Emp {sale.employee_id}")
    if sale.status == "VOIDED":
        lines.append(f"STATUS  : VOIDED ({sale.void_reason})")
    lines.append("----------------------------------------")
    lines.append(f"{'Item'.ljust(20)} {'Qty'.ljust(6)} {'Price'.ljust(6)} {'Total'}")
    lines.append("----------------------------------------")
    
    for name, qty, price, total in items_to_render:
        name_trunc = (name[:18] + "..") if len(name) > 20 else name.ljust(20)
        qty_str = str(qty).ljust(6)
        price_str = str(to_decimal(price)).ljust(6)
        total_str = str(to_decimal(total))
        lines.append(f"{name_trunc} {qty_str} {price_str} {total_str}")
        
    lines.append("----------------------------------------")
    lines.append(f"Subtotal: {' ' * 19}{to_decimal(sale.subtotal_minor)}")
    lines.append(f"Discount ({sale.discount_percent}%): {' ' * (20 - len(str(sale.discount_percent)))}{to_decimal(sale.discount_minor)}")
    lines.append(f"Tax: {' ' * 24}{to_decimal(sale.tax_minor)}")
    lines.append("========================================")
    lines.append(f"TOTAL: {' ' * 22}{to_decimal(sale.total_minor)}")
    lines.append("========================================")
    
    bill_text = "\n".join(lines)
    print(f"\n{bill_text}\n")
    
    os.makedirs("bills", exist_ok=True)
    filename = os.path.join("bills", f"{sale.bill_no}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bill_text)
    print(f"Bill saved to {filename}")

def _sales_history(billing: BillingService, actor: Session):
    print("\n[Sales History]")
    search = console.ask_text("Enter Bill Number or Date (YYYY-MM-DD) or leave blank for all")
    
    if search and search.startswith("PMS-"):
        try:
            sale, _ = billing.get_sale_details(actor, search)
            _render_and_save_bill(billing, sale)
        except PMSError as e:
            print(f"Error: {e}")
        return
        
    date_filter = search if search else None
    if date_filter:
        try:
            from datetime import date
            date.fromisoformat(date_filter)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    try:
        sales = billing.get_sales_history(actor, date_filter)
        if not sales:
            print("No sales found.")
            return
            
        print("\nSales History:")
        headers = ["ID", "Bill No", "Date", "Status", "Total"]
        rows = [[s.id, s.bill_no, s.created_at[:10], s.status, to_decimal(s.total_minor)] for s in sales]
        console.print_table(headers, rows)
        
        bill_no = console.ask_text("Enter Bill Number to reprint (or leave blank to go back)")
        if bill_no:
            sale, _ = billing.get_sale_details(actor, bill_no)
            _render_and_save_bill(billing, sale)
    except PMSError as e:
        print(f"Error: {e}")

def _void_sale(conn: sqlite3.Connection, billing: BillingService, actor: Session):
    bill_no = console.ask_text("Enter Bill Number to void", required=True)
    reason = console.ask_text("Reason for voiding", required=True)
    
    if console.confirm(f"Are you sure you want to void {bill_no}?"):
        try:
            with transaction(conn):
                billing.void_sale(actor, bill_no, reason)
            print("Sale voided successfully.")
        except PMSError as e:
            print(f"Error: {e}")
