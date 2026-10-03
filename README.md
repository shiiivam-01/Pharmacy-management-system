# Pharmacy Management System (PMS)

> A menu-driven Python application that lets a pharmacy manage medicine stock, expiry dates, suppliers, staff, billing, alerts and reports in one place.

**Status:** In development. Progress is tracked in [docs/implementation-plan.md](docs/implementation-plan.md). The setup commands below apply once Priority 0 (foundation) is complete.

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [The problem it solves](#2-the-problem-it-solves)
3. [Roles and responsibilities](#3-roles-and-responsibilities)
4. [How the system works](#4-how-the-system-works)
5. [Features](#5-features)
6. [Menus by role](#6-menus-by-role)
7. [Business rules](#7-business-rules)
8. [Sample bill](#8-sample-bill)
9. [Tech stack](#9-tech-stack)
10. [Architecture at a glance](#10-architecture-at-a-glance)
11. [Project structure](#11-project-structure)
12. [Data model](#12-data-model)
13. [Getting started](#13-getting-started)
14. [Testing](#14-testing)
15. [Documentation](#15-documentation)
16. [Roadmap](#16-roadmap)
17. [Limitations](#17-limitations)
18. [Acknowledgements, license and author](#18-acknowledgements-license-and-author)

---

## 1. Purpose

A pharmacy sells hundreds of different medicines. Each one has a price, a quantity on the shelf and, most importantly, an **expiry date**. PMS keeps all of this accurate and organised so that staff can:

- always know what is in stock and what is running low,
- never sell an expired medicine,
- bill customers quickly and correctly,
- keep records of suppliers, staff and sales,
- see simple reports that help the owner make decisions.

**In one line:** PMS keeps a pharmacy's stock, sales and records accurate, safe and easy to find.

## 2. The problem it solves

When a pharmacy runs on paper or scattered spreadsheets, the same problems keep appearing:

| Problem | Consequence | How PMS handles it |
|---|---|---|
| Stock counts drift from reality | Customers are turned away, or money is tied up in overstock | Every sale reduces stock automatically; every delivery adds a batch |
| Expired medicines stay on the shelf | Safety and legal risk | Expiry is tracked per batch; expired batches can never be sold; alerts warn early |
| Manual billing errors | Lost revenue, unhappy customers | Totals, tax and discounts are calculated by the system |
| Records are lost or scattered | No history, no accountability | One database, with an audit trail of important actions |
| Everyone can do everything | Mistakes and misuse | Role-based access: Admin and Pharmacist |

## 3. Roles and responsibilities

PMS has two roles. Each employee has their own login.

| | **Admin** | **Pharmacist** |
|---|---|---|
| Typical person | Owner or manager | Counter staff, dispensing pharmacist |
| Main job | Controls the system, people and money-sensitive actions | Serves customers, receives deliveries, keeps shelves stocked |
| Can do | Everything a Pharmacist can, plus: manage employees and suppliers, deactivate medicines, adjust stock, write off expired stock, give discounts above the pharmacist limit, void sales, view all reports and the audit log | Search and add/update medicines, receive stock, create bills, reprint bills, view alerts, view own sales and basic reports, change own password |
| Cannot do | Nothing is blocked | Manage employees, edit suppliers, deactivate medicines, adjust or write off stock, void sales, view other staff's sales or the audit log |

The exact permission table is in [docs/prd.md](docs/prd.md#6-roles-and-permissions).

## 4. How the system works

### A typical day

1. **Open the app and log in.** On the very first run the app asks you to create the first Admin account.
2. **Check the dashboard.** After login, PMS shows three alert counts: low stock, expiring soon, and expired with stock remaining.
3. **Receive a delivery.** For each medicine delivered, the pharmacist records a *batch*: batch number, quantity, expiry date, purchase price and supplier.
4. **Serve customers.** The pharmacist searches a medicine, adds it to a cart, repeats for other items, chooses discount and payment method, previews the bill and confirms.
5. **PMS does the rest.** It picks stock from the batch that expires first (FEFO: First Expired, First Out), skips expired batches, reduces stock, saves the sale and prints the bill.
6. **Review.** At closing time, the owner opens the daily sales summary, stock valuation and expiry reports.

### What happens inside a sale

```
Cart confirmed
   -> permission check (is this employee allowed?)
   -> validation (active medicine, positive quantity, enough non-expired stock)
   -> start a database transaction
   -> allocate stock from earliest-expiry batches (FEFO)
   -> save sale + sale items, reduce batch quantities
   -> commit (or roll back everything if anything fails)
   -> print bill and save it to bills/
```

A sale is **all-or-nothing**: it is never half-saved.

## 5. Features

Priorities (P0 to P4) match the implementation plan.

| Module | What it does | Priority |
|---|---|---|
| **Foundation** | Configuration, logging, database setup, first-run Admin creation, secure login | P0 |
| **Medicines** | Add, view, update, search, deactivate; category, strength, form, price, tax %, reorder level | P1 |
| **Suppliers** | Add, view, update, deactivate; link suppliers to medicines and deliveries | P1 |
| **Inventory** | Receive stock as batches, view batches by expiry, available stock excludes expired | P1 |
| **Billing** | Cart, FEFO allocation, tax and totals, atomic save, bill printout, bill file | P1 |
| **Access control** | Role checks enforced in the service layer; menus hide forbidden actions | P1 |
| **Alerts** | Low stock, expiring soon, expired with stock; dashboard at login | P2 |
| **Reports** | Daily sales, stock valuation, low-stock and expiry lists | P2 |
| **Employees** | Add, update, deactivate, reset password; change own password | P2 |
| **Stock control** | Adjust stock with a reason; write off expired batches | P2 |
| **Sales history** | Filter by date or bill number; reprint bills; discounts with a pharmacist cap | P2 |
| **Hardening** | Void sale, audit log, login lockout, CSV export, demo data, backups, prescription flag | P3 |
| **Future** | Returns, purchase orders, barcode scanning, GUI or web front end, multi-branch | P4 |

## 6. Menus by role

**Admin**

```
Main menu
 1. Medicines      (add, list, view, update, search, deactivate, reactivate)
 2. Inventory      (receive stock, view batches, adjust stock, write off expired)
 3. Billing        (new sale, sales history, reprint bill, void sale)
 4. Suppliers      (add, list, update, deactivate)
 5. Employees      (add, list, update, deactivate, reset password)
 6. Alerts         (low stock, expiring soon, expired)
 7. Reports        (daily sales, range sales, top sellers, stock valuation, sales by employee)
 8. Audit log
 9. My account     (change password)
 0. Logout
```

**Pharmacist**

```
Main menu
 1. Medicines      (add, list, view, update, search)
 2. Inventory      (receive stock, view batches)
 3. Billing        (new sale, my sales history, reprint bill)
 4. Suppliers      (list only)
 5. Alerts         (low stock, expiring soon, expired)
 6. Reports        (my daily sales, low-stock list, expiry list)
 7. My account     (change password)
 0. Logout
```

## 7. Business rules

- An **expired batch is never sold.** A batch is expired when its expiry date is before today.
- Stock is sold **FEFO**: earliest expiry first, spanning several batches when needed.
- **Stock can never go negative.**
- Expiry belongs to the **batch**, not the medicine. One medicine can have many batches.
- Money is stored as **whole minor units** (for example paise or cents) to avoid rounding errors.
- Prices are **tax-exclusive** in v1: tax is added on top using each medicine's tax %. Set tax % to 0 if your prices already include tax.
- Records that have history are **deactivated, never deleted**.
- Bill numbers are unique and sequential per day: `PMS-YYYYMMDD-0001`.
- Passwords are at least 8 characters and stored only as salted hashes.

Full list: [docs/prd.md](docs/prd.md#7-business-rules).

## 8. Sample bill

```
==========================================
              CITY PHARMACY
==========================================
Bill No  : PMS-20261003-0001
Date     : 2026-10-03 14:32
Served by: asha (PHARMACIST)
Customer : Walk-in
------------------------------------------
Item                  Qty   Price    Total
Paracetamol 500mg       2   20.00    40.00
Amoxicillin 250mg       1   85.00    85.00
------------------------------------------
Subtotal                            125.00
Discount (0%)                         0.00
Tax                                   6.25
------------------------------------------
TOTAL                               131.25
Payment  : CASH
==========================================
        Thank you. Get well soon.
```

## 9. Tech stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Application language |
| SQLite (`sqlite3`, standard library) | Database, a single file with real SQL, transactions and constraints |
| `hashlib` (PBKDF2-HMAC-SHA256) | Password hashing, no external dependency |
| `decimal` | Exact money calculations |
| `logging` | Rotating log file |
| `pytest` | Automated tests (the only dependency) |
| Git | Version control |

> The stack is an assumption made while the language was still undecided. If you switch language, update [docs/architecture.md](docs/architecture.md) first.

## 10. Architecture at a glance

```
+--------------------------------------------------+
| CLI layer        menus, prompts, printing        |
+--------------------------------------------------+
| Service layer    business rules, permissions,    |
|                  transactions                    |
+--------------------------------------------------+
| Repository layer SQL only, one class per table   |
+--------------------------------------------------+
| SQLite database  schema, constraints, data       |
+--------------------------------------------------+
```

Each layer only talks to the one directly below it. Details and workflow diagrams are in [docs/architecture.md](docs/architecture.md).

## 11. Project structure

```
pharmacy-management-system/
├── main.py                  # entry point
├── requirements.txt
├── README.md
├── AGENTS.md                # instructions for AI coding agents
├── docs/
│   ├── prd.md
│   ├── architecture.md
│   └── implementation-plan.md
├── pms/
│   ├── config.py  logger.py  exceptions.py  money.py  validators.py
│   ├── security.py          # password hashing + permission matrix
│   ├── database.py          # connection, schema init, transaction()
│   ├── schema.sql
│   ├── models.py
│   ├── repositories/        # SQL only
│   ├── services/            # business logic
│   └── cli/                 # menus and console helpers
├── scripts/                 # seed_demo.py, backup_db.py
├── tests/
├── data/  bills/  reports/  logs/  backups/   # created at runtime, not committed
```

## 12. Data model

| Table | Purpose |
|---|---|
| `employees` | Staff accounts: name, role, username, password hash, active flag |
| `suppliers` | Supplier contact details |
| `medicines` | Catalogue: name, form, strength, price, tax %, reorder level |
| `batches` | Each delivery of a medicine: batch no, quantity, expiry date, purchase price |
| `sales` | One row per bill: totals, payment method, status, who sold it |
| `sale_items` | Lines of a bill, each pointing at the batch it was taken from |
| `stock_adjustments` | Every manual or system stock change with a reason |
| `audit_log` | Who did what and when |

Full column definitions and the ER diagram are in [docs/architecture.md](docs/architecture.md#5-data-architecture).

## 13. Getting started

**Requirements:** Python 3.10 or newer.

```bash
# 1. Get the project
git clone <your-repository-url>
cd pharmacy-management-system

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies (pytest only)
python -m pip install -r requirements.txt

# 4. Run
python main.py
```

On first run, PMS creates `data/pharmacy.db`, applies the schema and asks you to create the first Admin account.

Optional, after the matching tasks are done:

```bash
python scripts/seed_demo.py    # load sample medicines, batches and staff
python scripts/backup_db.py    # copy the database to backups/ with a timestamp
```

**Configuration** lives in `pms/config.py`: shop name and address (printed on bills), expiry warning days (default 30), pharmacist discount cap (default 10 percent), currency symbol, and folder paths.

## 14. Testing

```bash
python -m pytest
```

Tests use an in-memory SQLite database, so they never touch real data. The most important scenarios are FEFO across several batches, expired stock excluded, sale rollback on failure, void restoring stock, permission denial, and password hashing.

## 15. Documentation

| Document | What it contains |
|---|---|
| [docs/prd.md](docs/prd.md) | Product requirements: users, user stories, requirements with acceptance criteria, business rules, permissions |
| [docs/architecture.md](docs/architecture.md) | Layers, modules, database design, workflow diagrams, error handling, security, testing |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Priority-wise task list with estimates, dependencies, milestones and progress |
| [AGENTS.md](AGENTS.md) | Rules and commands for AI coding agents working in this repository |

## 16. Roadmap

| Priority | Theme | Goal |
|---|---|---|
| P0 | Foundation | Project skeleton, database, login |
| P1 | Core MVP | Medicines, suppliers, batches, billing: a pharmacy can receive stock and sell it |
| P2 | Important | Alerts, reports, employee management, stock control, sales history |
| P3 | Hardening | Void sale, audit log, lockout, CSV export, demo data, backups, higher test coverage |
| P4 | Future | Returns, purchase orders, barcode, GUI or web front end |

## 17. Limitations

- Single machine, single user at a time. There is no network or multi-user concurrency.
- Console interface only in v1.
- No returns or refunds, purchase orders, customer accounts or online payments in v1.
- This is an **educational project**. It is not certified for real pharmacy operations and does not implement regulatory requirements such as controlled-substance registers or e-prescriptions.

## 18. Acknowledgements, license and author

- The feature scope was informed by publicly available pharmacy management projects, for example [abdulrehmandev/pharmacy-management-cli](https://github.com/abdulrehmandev/pharmacy-management-cli). PMS is an independent implementation. *(Keep this line accurate: edit it if you used any other source.)*
- **License:** MIT *(change this if your course requires something else)*.
- **Author:** [Your Name], [Your College / Course], [Year].
