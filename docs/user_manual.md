# Pharmacy Management System - User Manual

Welcome to the Pharmacy Management System (PMS). The system is a menu-driven terminal application. All actions are performed by selecting numbers from a menu or typing text when prompted.

## Logging In
When you start the application (`python main.py`), you will be prompted to log in. 
- Enter your **Username** and **Password**. 
- If this is the very first time the application is run, it will ask you to create the initial **System Admin** account.

---

## 1. Role: Pharmacist

The Pharmacist role is designed for daily counter operations.

### What you can do:
- **View Alerts:** Your dashboard will warn you about low stock or expiring medicines.
- **Search & View Medicines:** You can look up active medicines to check their prices and stock availability.
- **Process Sales (Billing):**
  - Select `Billing -> New Sale`.
  - Search for medicines and add them to your cart.
  - Apply up to a **10% discount** per bill.
  - The system automatically allocates stock from the batches that expire soonest (FEFO).
  - Bills are saved to the `bills/` folder and printed to the screen.
- **View Own Sales History:** You can reprint bills for sales *you* processed today or on past dates.
- **View Daily Sales:** You can check your own total revenue and sales count for the day.
- **Change Password:** You can update your own login password at any time.

### What you CANNOT do:
- You cannot add or edit medicines, suppliers, or employees.
- You cannot receive new stock or adjust/void existing stock.
- You cannot void a completed sale.
- You cannot view reports for the entire pharmacy or other employees.

---

## 2. Role: Admin

The Admin role has full control over the system, including back-office management and auditing.

### What you can do:
Everything a Pharmacist can do, **PLUS**:
- **Manage Employees:** Add new Pharmacists or Admins, deactivate old accounts, and reset passwords if an employee forgets theirs.
- **Manage Suppliers & Medicines:** Add new suppliers and medicines to the catalog, update prices/taxes, or deactivate discontinued products.
- **Manage Inventory:**
  - Receive stock (assigning it to specific batches with expiry dates).
  - Perform manual stock adjustments (with a mandatory reason).
  - Write off expired stock automatically.
- **Void Sales:** Cancel a completed sale if there was a mistake. The stock is automatically returned to the shelves.
- **Apply Unlimited Discounts:** Apply any discount percent (up to 100%) during a sale.
- **Advanced Reports:**
  - View **All Sales** (not just your own).
  - View **Stock Valuation** (calculate the capital tied up in inventory).
  - View **Range Sales Summary** and **Top 10 Sellers**.
  - View **Sales by Employee** to track performance.
- **Audit Logs:** View a complete, tamper-proof history of every action taken in the system, filterable by user, action, or date.
- **Export Data:** Export any report directly to a CSV file.

## Need Help?
Follow the prompt hints. 
- `[Y/N]` means you can type `Y` for Yes or `N` for No.
- Dates must always be typed in `YYYY-MM-DD` format (e.g., `2026-10-15`).
- If you make a mistake, look for a `0` option to cancel or go back to the previous menu.
