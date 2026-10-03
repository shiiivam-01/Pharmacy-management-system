# Pharmacy Management System - Flow Captures (Screenshots)

Since this is a console application, the following text blocks represent what the user sees in the terminal during main workflows.

## 1. Login Dashboard (Admin)
```text
=== Pharmacy Management System ===
1. Login
2. Exit
Enter choice: 1
Username: admin
Password: 

--- Dashboard ---
Welcome, System Admin (ADMIN)

Alerts:
  [!] 2 medicines are low on stock!
  [!] 1 batches expire within 30 days!
  [!] 0 expired batches have stock!

1. Billing
2. Inventory & Medicines
3. Suppliers
4. Reports
5. Employees
6. Audit Log
7. Change Password
0. Logout
Enter choice:
```

## 2. Receive Stock
```text
--- Inventory ---
1. Receive Stock
2. Stock Adjustments
3. Write-off Expired Stock
0. Back to main menu
Enter choice: 1

[Receive Stock]
Enter Medicine ID: 5
Medicine: Paracetamol Tablet 500mg (Available: 100)
Batch Number: BATCH-2024-X
Quantity: 500
Purchase Price (per unit): 1.50
Expiry Date (YYYY-MM-DD): 2027-12-31

Confirm receive stock? [Y/N]: Y
Stock received successfully.
```

## 3. Billing (New Sale)
```text
[New Sale]
Action (Add item, Finish, Cancel) [A/F/C]: A
Search medicine (name/generic): para
ID: 5 | Paracetamol Tablet 500mg | Price: 2.00 | Stock: 600
Enter Medicine ID to add (or 0 to cancel): 5
Quantity: 10
Added to cart.

Action (Add item, Finish, Cancel) [A/F/C]: F

--- Cart Preview ---
Paracetamol Tablet 500mg | Qty: 10 | Total: 20.00
Subtotal: 20.00
Customer Name (optional): John Doe
Prescription Note (optional): 
Discount Percent [0.0]: 0
Payment Method (CASH/CARD/UPI) [CASH]: CARD

FINAL TOTAL: 20.00
Confirm sale? [Y/N]: Y

========================================
             PHARMACY INC               
========================================
Bill No : PMS-20261003-0001
Date    : 2026-10-03 21:00:00
Cashier : Emp 1
----------------------------------------
Item                 Qty    Price  Total
----------------------------------------
Paracetamol Tablet 5 10     2.00   20.00
----------------------------------------
Subtotal:                    20.00
Discount (0.0%):              0.00
Tax:                          0.00
========================================
TOTAL:                       20.00
========================================

Bill saved to bills\PMS-20261003-0001.txt
Sale completed.
```

## 4. Reports (Daily Sales)
```text
--- Reports ---
1. Daily Sales Summary
2. Low Stock Report
3. Expiry Report
4. Stock Valuation
5. Range Sales Summary
6. Top 10 Sellers
7. Sales by Employee
0. Back to main menu
Enter choice: 1

[Daily Sales Summary]
Enter Date (YYYY-MM-DD) or leave blank for today: 

--- Sales Summary for 2026-10-03 ---
Total Sales: 4
Subtotal:    125.00
Discounts:   5.00
Tax:         0.00
Revenue:     120.00

By Payment Method:
  CASH: 2 sales, 60.00
  CARD: 1 sales, 20.00
  UPI: 1 sales, 40.00
Export to CSV? [Y/N]: Y
Exported to reports\daily_sales_2026-10-03.csv
```
