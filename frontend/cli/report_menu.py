"""
Reports menu for the CLI.
"""
import sqlite3
from frontend.cli import console
from backend.models import Session
from backend.services.report_service import ReportService
from backend.money import to_decimal
from backend.exceptions import PMSError
import csv
import os

def _export_csv(filename: str, headers: list, rows: list):
    os.makedirs("reports", exist_ok=True)
    filepath = os.path.join("reports", filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Exported to {filepath}")

def show_menu(conn: sqlite3.Connection, actor: Session):
    report_service = ReportService(conn)
    
    while True:
        print("\n--- Reports ---")
        print("1. Daily Sales Summary")
        print("2. Low Stock Report")
        print("3. Expiry Report")
        if actor.role == "ADMIN":
            print("4. Stock Valuation")
            print("5. Range Sales Summary")
            print("6. Top 10 Sellers")
            print("7. Sales by Employee")
        print("8. Visual Sales Chart (Weekly/Monthly)")
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
            elif choice == "5" and actor.role == "ADMIN":
                _range_sales(report_service, actor)
            elif choice == "6" and actor.role == "ADMIN":
                _top_sellers(report_service, actor)
            elif choice == "7" and actor.role == "ADMIN":
                _sales_by_employee(report_service, actor)
            elif choice == "8":
                _visual_sales_chart(report_service, actor)
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
    csv_rows = []
    for pm, data in summary['by_method'].items():
        print(f"  {pm}: {data['count']} sales, {to_decimal(data['total'])}")
        csv_rows.append([pm, data['count'], to_decimal(data['total'])])
        
    if console.confirm("Export to CSV?"):
        _export_csv(f"daily_sales_{summary['date']}.csv", ["Payment Method", "Sales Count", "Revenue"], csv_rows)

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
    
    if console.confirm("Export to CSV?"):
        _export_csv("low_stock_report.csv", headers, rows)

def _expiry_report(report_service: ReportService, actor: Session):
    print("\n[Expiry Report]")
    from backend.config import EXPIRY_WARNING_DAYS
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
    
    if console.confirm("Export to CSV?"):
        _export_csv(f"expiry_report_{days}days.csv", headers, rows)

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
        
        if console.confirm("Export to CSV?"):
            _export_csv(f"stock_valuation_{val['date']}.csv", headers, rows)

def _range_sales(report_service: ReportService, actor: Session):
    print("\n[Range Sales Summary]")
    start = console.ask_date("Start Date", required=True)
    end = console.ask_date("End Date", required=True)
    
    summary = report_service.get_range_sales_summary(actor, start.isoformat(), end.isoformat())
    print(f"\nSales from {summary['start_date']} to {summary['end_date']}")
    print(f"Count: {summary['count']}")
    print(f"Revenue: {to_decimal(summary['total'])}")
    
    if console.confirm("Export to CSV?"):
        _export_csv(f"range_sales_{summary['start_date']}_{summary['end_date']}.csv", 
                    ["Start", "End", "Count", "Revenue"],
                    [[summary['start_date'], summary['end_date'], summary['count'], to_decimal(summary['total'])]])

def _top_sellers(report_service: ReportService, actor: Session):
    print("\n[Top 10 Sellers]")
    start = console.ask_date("Start Date", required=True)
    end = console.ask_date("End Date", required=True)
    
    items = report_service.get_top_sellers(actor, start.isoformat(), end.isoformat())
    if not items:
        print("No sales in this range.")
        return
        
    headers = ["Medicine", "Qty Sold", "Revenue"]
    rows = []
    for item in items:
        name = f"{item['name']} {item['form']} {item['strength']}".strip()
        rows.append([name, item['total_qty'], to_decimal(item['total_revenue'])])
        
    console.print_table(headers, rows)
    
    if console.confirm("Export to CSV?"):
        _export_csv(f"top_sellers_{start.isoformat()}_{end.isoformat()}.csv", headers, rows)

def _sales_by_employee(report_service: ReportService, actor: Session):
    print("\n[Sales by Employee]")
    start = console.ask_date("Start Date", required=True)
    end = console.ask_date("End Date", required=True)
    
    items = report_service.get_sales_by_employee(actor, start.isoformat(), end.isoformat())
    
    headers = ["Employee ID", "Username", "Name", "Bills Count", "Net Total"]
    rows = []
    for item in items:
        rows.append([item['id'], item['username'], item['full_name'], item['bills_count'], to_decimal(item['net_total'] or 0)])
        
    console.print_table(headers, rows)
    
    if console.confirm("Export to CSV?"):
        _export_csv(f"sales_by_employee_{start.isoformat()}_{end.isoformat()}.csv", headers, rows)

def _visual_sales_chart(report_service: ReportService, actor: Session):
    print("\n[Visual Sales Chart]")
    days = console.ask_int("Enter number of days (e.g., 7 for weekly, 30 for monthly)", required=True)
    if days <= 0 or days > 365:
        print("Please enter a valid number of days (1-365).")
        return
        
    chart_data = report_service.get_sales_chart_data(actor, days)
    
    # Calculate max for scaling the chart
    max_total = max((item['total'] for item in chart_data), default=0)
    
    print(f"\n--- Sales Chart (Last {days} Days) ---")
    if max_total == 0:
        print("No sales data available for this period.")
        return
        
    MAX_BAR_LENGTH = 50
    for item in chart_data:
        date_str = item['date'][-5:] # Show only MM-DD for cleaner chart
        total = item['total']
        
        # Calculate bar length (proportional to max_total)
        bar_len = int((total / max_total) * MAX_BAR_LENGTH) if max_total > 0 else 0
        bar = '█' * bar_len
        
        # Print date, bar, and exact value
        from backend.money import to_decimal
        print(f"{date_str} | {bar:<{MAX_BAR_LENGTH}} | {to_decimal(total)}")
        
    print("-" * (MAX_BAR_LENGTH + 20))
    from backend.money import to_decimal
    print(f"Total over {days} days: {to_decimal(sum(item['total'] for item in chart_data))}")
