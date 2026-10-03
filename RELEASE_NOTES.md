# Pharmacy Management System - Release Notes

## v1.0 Release
**Date:** 2026-10-03

We are excited to announce the full v1.0 release of the Pharmacy Management System! This release brings together everything required to run a full pharmacy's operations locally from a command-line interface, safely and securely.

### What's Included:
- **Comprehensive Stock & Inventory Management:** 
  - Manage Medicines and Suppliers. 
  - Receive deliveries mapped to specific batches and expiry dates.
  - Automatically write-off expired stock and perform manual stock adjustments with mandatory reasons.
- **Advanced Billing (FEFO):**
  - Search medicines, add items to cart, and generate professional text-based bills.
  - The system automatically allocates stock using First-Expired, First-Out (FEFO), skipping expired batches and ensuring no stock goes to waste.
  - Apply role-based discounts (Admin has unlimited discount capability, Pharmacist is capped at 10%).
  - Flag prescription-only medicines for mandatory pharmacist verification.
- **Robust Staff & Security Management:**
  - Segregated `ADMIN` and `PHARMACIST` roles with fine-grained access control enforced at the service level.
  - Secure PBKDF2-HMAC-SHA256 password hashing and a 5-attempt login lockout policy to prevent brute-forcing.
- **Reporting & Auditing:**
  - View real-time alerts for low stock and upcoming expirations right on your dashboard.
  - Generate comprehensive reports: Daily Sales, Range Sales, Top Sellers, Sales by Employee, and Stock Valuation.
  - Export all reports directly to CSV for spreadsheet software.
  - Admins can view a tamper-proof Audit Log of every action (sales, logins, stock updates) in the system.
- **Developer & Testing Tools:**
  - Over 89% code coverage with `pytest` utilizing an injected in-memory database to prevent test contamination.
  - `seed_demo.py` script provided to auto-populate the database for quick demonstration.
  - `backup_db.py` script to safely backup data using native SQLite locking mechanisms.

**Documentation Updates:**
- Included ER Diagram (`er_diagram.mmd`), Test Cases (`test_cases.md`), Screenshots (`screenshots.md`), and a `user_manual.md`.
- Fully documented architecture, database schemas, and implementation plans.

Thank you to everyone who contributed to building and testing the system!
