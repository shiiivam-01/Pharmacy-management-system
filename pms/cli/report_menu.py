"""
Reports menu for the CLI.
"""
import sqlite3
from pms.cli import console
from pms.models import Session
from pms.services.report_service import ReportService
from pms.money import to_decimal
from pms.exceptions import PMSError

def show_menu(conn: sqlite3.Connection, actor: Session):
    report_service = ReportService(conn)
    
    while True:
        print("\n--- Reports ---")
        print("1. Daily Sales Summary")
        print("2. Low Stock Report")
        print("3. Expiry Report")
        if actor.role == "ADMIN":
            print("4. Stock Valuation")
        print("0. Back to main menu")
        
        choice = console.ask_text("Enter choice", required=True)
        if choice == "0":
            break
            
        try:
            if choice == "1":
                _daily_sales(report_service, actor)
            elif choice == "2":
                _low_stock(report_service, actor)
            elif choice == "3":
                _expiry_report(report_service, actor)
            elif choice == "4" and actor.role == "ADMIN":
                _stock_valuation(report_service, actor)
            else:
                print("Invalid choice.")
        except PMSError as e:
            print(f"Error: {e}")

def _daily_sales(report_service: ReportService, actor: Session):
    print("\n[Daily Sales Summary]")
    date_str = console.ask_text("Enter Date (YYYY-MM-DD) or leave blank for today")
    
    if date_str:
        try:
            from datetime import date
            date.fromisoformat(date_str)
        except ValueError:
            print("Invalid date format.")
            return
    else:
        date_str = None
        
    summary = report_service.get_daily_sales_summary(actor, date_str)
    
    print(f"\n--- Sales Summary for {summary['date']} ---")
    if summary['total_count'] == 0:
        print("No completed sales found.")
        return
        
    print(f"Total Sales: {summary['total_count']}")
    print(f"Subtotal:    {to_decimal(summary['total_subtotal'])}")
    print(f"Discounts:   {to_decimal(summary['total_discount'])}")
    print(f"Tax:         {to_decimal(summary['total_tax'])}")
    print(f"Revenue:     {to_decimal(summary['total_revenue'])}")
    
    print("\nBy Payment Method:")
    for pm, data in summary['by_method'].items():
        print(f"  {pm}: {data['count']} sales, {to_decimal(data['total'])}")

def _low_stock(report_service: ReportService, actor: Session):
    print("\n[Low Stock Report]")
    items = report_service.get_low_stock_report(actor)
    
    if not items:
        print("All medicines have sufficient stock.")
        return
        
    headers = ["Medicine", "Available", "Reorder Level"]
    rows = []
    for item in items:
        name = f"{item['name']} {item['form']} {item['strength']}".strip()
        rows.append([name, item['available'], item['reorder_level']])
        
    console.print_table(headers, rows)

def _expiry_report(report_service: ReportService, actor: Session):
    print("\n[Expiry Report]")
    from pms.config import EXPIRY_WARNING_DAYS
    days = console.ask_int(f"Days ahead [{EXPIRY_WARNING_DAYS}]", required=False) or EXPIRY_WARNING_DAYS
    
    items = report_service.get_expiry_report(actor, days)
    if not items:
        print(f"No batches expiring within {days} days.")
        return
        
    headers = ["Medicine", "Batch", "Qty", "Expiry Date"]
    rows = []
    for item in items:
        name = f"{item['name']} {item['form']} {item['strength']}".strip()
        rows.append([name, item['batch_no'], item['quantity'], item['expiry_date']])
        
    console.print_table(headers, rows)

def _stock_valuation(report_service: ReportService, actor: Session):
    print("\n[Stock Valuation]")
    val = report_service.get_stock_valuation(actor)
    
    print(f"\nDate: {val['date']}")
    print(f"Total Active Stock Value: {to_decimal(val['total_value'])}")
    
    if not val['items']:
        print("No stock found.")
        return
        
    if console.confirm("View detailed list?"):
        headers = ["Medicine", "Batch", "Qty", "Price", "Value"]
        rows = []
        for item in val['items']:
            rows.append([
                item['medicine'],
                item['batch_no'],
                item['quantity'],
                to_decimal(item['purchase_price']),
                to_decimal(item['value'])
            ])
        console.print_table(headers, rows)
