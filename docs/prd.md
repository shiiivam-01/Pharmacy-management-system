# Product Requirements Document: Pharmacy Management System (PMS)

| | |
|---|---|
| **Version** | 1.0 |
| **Status** | Draft for implementation |
| **Date** | 2026-10-03 |
| **Owner** | [Your Name] |
| **Related** | [README](../README.md), [architecture](architecture.md), [implementation plan](implementation-plan.md) |

---

## Table of Contents

1. [Purpose and background](#1-purpose-and-background)
2. [Problem statement](#2-problem-statement)
3. [Goals and non-goals](#3-goals-and-non-goals)
4. [Users and personas](#4-users-and-personas)
5. [User stories](#5-user-stories)
6. [Roles and permissions](#6-roles-and-permissions)
7. [Business rules](#7-business-rules)
8. [Functional requirements](#8-functional-requirements)
9. [Non-functional requirements](#9-non-functional-requirements)
10. [Data requirements](#10-data-requirements)
11. [Report specifications](#11-report-specifications)
12. [Assumptions, constraints and dependencies](#12-assumptions-constraints-and-dependencies)
13. [Risks and mitigations](#13-risks-and-mitigations)
14. [Success metrics](#14-success-metrics)
15. [Scope: release plan and exclusions](#15-scope-release-plan-and-exclusions)
16. [Open questions](#16-open-questions)
17. [Glossary](#17-glossary)

---

## 1. Purpose and background

PMS is a console application that digitises the daily work of a small pharmacy: keeping track of medicines and their expiry dates, receiving stock from suppliers, billing customers, warning staff about low or expiring stock, and giving the owner simple reports.

It is built as a software engineering semester project. The requirements here define *what* the system must do; [architecture.md](architecture.md) defines *how*.

## 2. Problem statement

Pharmacies that rely on paper registers or loose spreadsheets suffer from:

1. **Inaccurate stock.** Counts drift, causing stock-outs or overstock.
2. **Expired medicines on the shelf.** This is a safety and legal risk. Expiry dates are per delivery (batch), which makes them hard to track manually.
3. **Billing errors.** Manual arithmetic on tax and discounts causes revenue loss and disputes.
4. **Scattered records.** Supplier details, staff and sales history live in different places or are lost.
5. **No accountability.** Nobody can tell who changed what.

PMS addresses these with batch-level stock tracking, automatic FEFO billing, alerts, role-based access and an audit trail.

## 3. Goals and non-goals

### Goals

| ID | Goal |
|---|---|
| G1 | Always-accurate stock, tracked per batch with expiry dates |
| G2 | Never sell an expired medicine |
| G3 | Fast, correct billing with automatic stock deduction |
| G4 | Early warnings for low stock and expiring stock |
| G5 | Controlled access: Admin and Pharmacist roles |
| G6 | Simple reports for daily decisions |
| G7 | A clean, layered, well-tested codebase the author can fully explain |

### Non-goals (v1)

Returns and refunds, purchase orders, customer accounts, barcode scanning, GUI or web front end, network or multi-user concurrency, online payments, regulatory compliance features (controlled-substance register, e-prescriptions, insurance claims), multi-branch operation. See [section 15](#15-scope-release-plan-and-exclusions).

## 4. Users and personas

### Persona 1: Meera, Admin (pharmacy owner)

- **Goals:** control costs, avoid expired stock, know daily takings, manage staff.
- **Frustrations:** finds out about expiry too late; cannot check what happened when money does not match.
- **Uses PMS to:** manage employees and suppliers, review reports and the audit log, adjust or write off stock, void mistaken bills.

### Persona 2: Asha, Pharmacist (counter staff)

- **Goals:** serve customers quickly, find medicines fast, avoid billing mistakes.
- **Frustrations:** searching registers, doing arithmetic under pressure, uncertainty about which stock to sell first.
- **Uses PMS to:** search medicines, receive deliveries, create bills, check alerts.

## 5. User stories

Priority levels: **P0** foundation, **P1** core MVP, **P2** important, **P3** hardening, **P4** future. A project is demo-ready after P1; it is complete after P2; P3 makes it robust.

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| US-01 | owner | create the first Admin account when I start the app | the system is secured from day one | P0 |
| US-02 | employee | log in with my own username and password | actions are tied to me | P0 |
| US-03 | pharmacist | search medicines by name, generic name or category | I find items in seconds | P1 |
| US-04 | pharmacist | add and update medicines | the catalogue stays current | P1 |
| US-05 | admin | add and update suppliers | I know who supplies what | P1 |
| US-06 | pharmacist | record a delivery as a batch with expiry date | stock and expiry are accurate | P1 |
| US-07 | pharmacist | build a cart and confirm a sale | the customer gets a correct bill | P1 |
| US-08 | pharmacist | have the system pick the earliest-expiring stock | old stock is sold first and expired stock is never sold | P1 |
| US-09 | pharmacist | get a printed bill and a saved copy | I can hand it over and reprint it later | P1 |
| US-10 | admin | restrict what pharmacists can do | mistakes and misuse are limited | P1 |
| US-11 | pharmacist | see low-stock and expiring-soon alerts when I log in | I reorder and act in time | P2 |
| US-12 | admin | add, deactivate and reset passwords for employees | staff access matches reality | P2 |
| US-13 | admin | adjust stock with a reason and write off expired batches | the system matches the shelf | P2 |
| US-14 | owner | see a daily sales summary and a stock valuation | I know takings and capital tied up | P2 |
| US-15 | pharmacist | look up and reprint an old bill | I can help a customer who lost theirs | P2 |
| US-16 | admin | void a wrong bill and restore its stock | errors can be corrected cleanly | P3 |
| US-17 | admin | view an audit log | I can trace who did what | P3 |
| US-18 | owner | export reports to CSV | I can open them in a spreadsheet | P3 |
| US-19 | any user | be protected from password guessing | accounts are safer | P3 |

## 6. Roles and permissions

Authorization is enforced in the **service layer** (not just by hiding menus).

| Action | Admin | Pharmacist |
|---|:---:|:---:|
| Log in, log out, change own password | Yes | Yes |
| View and search medicines | Yes | Yes |
| Add and update medicines | Yes | Yes |
| Deactivate and reactivate medicines | Yes | No |
| View suppliers | Yes | Yes |
| Add, update, deactivate suppliers | Yes | No |
| Receive stock (create batch) | Yes | Yes |
| View batches | Yes | Yes |
| Adjust stock, write off expired batches | Yes | No |
| Create a sale | Yes | Yes |
| Discount above the pharmacist cap (default 10 percent) | Yes | No |
| View sales history | All sales | Own sales only |
| Reprint a bill | Any bill | Own bills only |
| Void a sale | Yes | No |
| View alerts | Yes | Yes |
| Reports: daily sales | All | Own sales only |
| Reports: low-stock list, expiry list | Yes | Yes |
| Reports: stock valuation, range sales, top sellers, sales by employee | Yes | No |
| Manage employees (add, update, deactivate, reset password) | Yes | No |
| View audit log | Yes | No |

## 7. Business rules

| ID | Rule |
|---|---|
| BR-01 | A batch is **expired** when `expiry_date < today`. Expired batches are never sold. |
| BR-02 | Stock is sold **FEFO**: from the batch with the earliest expiry date first (ties broken by lowest batch id), spanning batches when one is not enough. |
| BR-03 | Stock quantity of a batch can never be negative. |
| BR-04 | **Available stock** of a medicine = sum of `quantity` over its non-expired batches. |
| BR-05 | Unit price must be greater than 0. Tax percent must be between 0 and 100. Reorder level must be 0 or more. |
| BR-06 | A medicine is unique by (name, form, strength), compared case-insensitively. |
| BR-07 | A batch number is unique per medicine. A received batch must have quantity > 0 and an expiry date in the future. |
| BR-08 | Records referenced by history (medicines, suppliers, employees, batches, sales) are **deactivated, never deleted**. |
| BR-09 | Money is stored as integer minor units (for example paise) and computed with `Decimal`. |
| BR-10 | Prices are **tax-exclusive**. Per sale line: `line_base = quantity x unit_price`; `discount = round(line_base x discount%)`; `tax = round((line_base - discount) x tax%)`. Rounding is half-up to the minor unit, per line. Totals are the sums of the lines. |
| BR-11 | Prices and tax % are copied onto each sale line at the time of sale. Later price changes never alter past bills. |
| BR-12 | Bill numbers have the format `PMS-YYYYMMDD-NNNN`, are unique and increase through the day. Voided bills keep their number. |
| BR-13 | A sale either fully succeeds (sale, lines, stock reduction) or changes nothing. |
| BR-14 | A voided sale restores each line's quantity to the batch it was taken from. A voided sale is excluded from sales reports. |
| BR-15 | Passwords are at least 8 characters and stored only as salted PBKDF2 hashes. |
| BR-16 | The last active Admin cannot be deactivated, and nobody can deactivate their own account. |
| BR-17 | Inactive medicines and suppliers cannot be chosen for new sales, deliveries or medicines. Existing history is untouched. |
| BR-18 | Low stock means available stock is at or below the medicine's reorder level. Expiring soon means a non-empty batch expires within `EXPIRY_WARNING_DAYS` (default 30) days from today. |

## 8. Functional requirements

Each requirement has a priority and acceptance criteria.

### 8.1 Authentication and access (AUTH)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-AUTH-01 | On first run with no employees, the app asks the user to create the first Admin. | P0 | With an empty database the setup screen appears; after creation login works; the setup screen never appears again. |
| FR-AUTH-02 | Employees log in with username and password. Passwords are stored only as salted PBKDF2 hashes. | P0 | Correct credentials open a session. Wrong credentials show one generic message ("Invalid username or password"). The database holds no plain-text passwords. Inactive accounts cannot log in. |
| FR-AUTH-03 | Every service operation checks the acting employee's role against the permission table. | P1 | A Pharmacist calling an Admin-only operation gets an authorization error and nothing changes. Menus hide actions the role cannot use. |
| FR-AUTH-04 | Users can change their own password and log out. | P2 | Requires the current password. New password has 8+ characters and differs from the old one. Logout returns to the login screen. |
| FR-AUTH-05 | Five consecutive failed logins lock the account for 5 minutes. | P3 | The fifth failure sets the lock. A login attempt during the lock is refused and shows the remaining time. A successful login resets the counter. |

### 8.2 Medicines (MED)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-MED-01 | Add a medicine. | P1 | Required: name, form, unit price. Optional: generic name, strength, category, manufacturer, preferred supplier, tax %, reorder level (default 10), prescription flag. A duplicate (name, form, strength) is rejected with a clear message. |
| FR-MED-02 | List and view medicines. | P1 | List shows id, name, strength, form, price, available stock. Detail view shows all fields and the medicine's batches. |
| FR-MED-03 | Update a medicine. | P1 | Any field can be edited with the same validation as add. Past sales are unaffected (BR-11). |
| FR-MED-04 | Deactivate a medicine (Admin). | P1 | An inactive medicine does not appear in billing search and cannot be sold. History is kept. |
| FR-MED-05 | Search by name, generic name or category. | P1 | Partial, case-insensitive matching. Results return in under 1 second with 10,000 medicines. |
| FR-MED-06 | Filter by category or supplier; reactivate a medicine (Admin). | P2 | Filters can be combined with search. A reactivated medicine is sellable again. |

### 8.3 Suppliers (SUP)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-SUP-01 | Add and update suppliers (Admin). | P1 | Name is required and unique. Phone and email are validated when given. |
| FR-SUP-02 | List and view suppliers (both roles). | P1 | List shows name, contact, phone and the number of medicines linked. |
| FR-SUP-03 | Deactivate a supplier (Admin). | P1 | An inactive supplier cannot be chosen for new deliveries or medicines. Existing links stay. |

### 8.4 Inventory (INV)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-INV-01 | Receive stock by creating a batch. | P1 | Required: medicine, batch number, quantity > 0, expiry date in the future, purchase price >= 0. Supplier is optional and defaults to the medicine's preferred supplier. Available stock rises by the quantity. Duplicate batch number for the same medicine is rejected. |
| FR-INV-02 | View batches per medicine. | P1 | Ordered by expiry date. Shows quantity remaining, expiry date and days to expiry; expired batches are marked. |
| FR-INV-03 | Available stock excludes expired batches everywhere it is displayed or checked. | P1 | A medicine with only expired batches shows 0 available and cannot be sold. |
| FR-INV-04 | Adjust stock (Admin). | P2 | Reasons: DAMAGED, LOST, CORRECTION. A reason is mandatory. The batch quantity cannot go below 0. Each adjustment is recorded in `stock_adjustments`. |
| FR-INV-05 | Write off expired batches (Admin). | P2 | Sets the batch quantity to 0 and records an EXPIRED_WRITE_OFF adjustment holding the removed quantity. |

### 8.5 Billing (BILL)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-BILL-01 | Build a cart. | P1 | Search and select medicines, enter quantities. The same medicine merges into one line. Items can be removed before confirming. |
| FR-BILL-02 | Allocate stock by FEFO (BR-02). | P1 | With batches expiring on days 10 and 20, selling more than the first batch holds takes the remainder from the second. Expired batches are never used. |
| FR-BILL-03 | Reject insufficient stock. | P1 | Message shows the available quantity. The cart stays unchanged. |
| FR-BILL-04 | Compute totals (BR-10). | P1 | Subtotal, discount, tax and total match hand calculation for test cases, to the minor unit. |
| FR-BILL-05 | Confirm a sale atomically (BR-13). | P1 | Sale, lines and stock reduction are saved together. A simulated failure midway leaves stock unchanged. |
| FR-BILL-06 | Produce the bill. | P1 | The bill prints to the console and is saved as `bills/<bill_no>.txt`. Bill numbers follow BR-12. |
| FR-BILL-07 | Apply a discount. | P2 | Percent from 0 to 100. A Pharmacist is capped at `MAX_PHARMACIST_DISCOUNT_PCT` (default 10). |
| FR-BILL-08 | Sales history and reprint. | P2 | Filter by date or bill number. Pharmacists see only their own sales; Admin sees all. A reprint is identical to the original. |
| FR-BILL-09 | Void a sale (Admin). | P3 | A reason is mandatory. Status becomes VOIDED. Stock is restored to the same batches and logged as SALE_VOID adjustments. |
| FR-BILL-10 | Prescription flag. | P3 | Selling a flagged medicine requires explicit confirmation. An optional prescription note is saved on the sale. |

### 8.6 Alerts (ALR)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-ALR-01 | Low-stock alert (BR-18). | P2 | Lists active medicines at or below their reorder level with available and reorder quantities. |
| FR-ALR-02 | Expiring-soon alert (BR-18). | P2 | Lists non-empty batches expiring within `EXPIRY_WARNING_DAYS`, soonest first. |
| FR-ALR-03 | Expired-with-stock alert. | P2 | Lists batches with expiry before today and quantity above 0. |
| FR-ALR-04 | Login dashboard. | P2 | After login, shows the three alert counts, with drill-down lists on request. |

### 8.7 Reports (RPT)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-RPT-01 | Daily sales summary. | P2 | For a chosen date (default today): number of bills, items sold, gross, discounts, tax, net, split by payment method. Voided sales excluded. Pharmacists see own sales only. |
| FR-RPT-02 | Stock valuation (Admin). | P2 | Sum over non-expired batches of quantity x purchase price, and of quantity x selling price. |
| FR-RPT-03 | Low-stock and expiry lists. | P2 | Same data as FR-ALR-01 to 03, formatted for printing. |
| FR-RPT-04 | Range sales and top 10 sellers (Admin). | P3 | Totals for a date range; ten medicines with the highest quantity sold. |
| FR-RPT-05 | Sales by employee (Admin). | P3 | Bills and net total per employee for a date range. |
| FR-RPT-06 | CSV export of any report. | P3 | A CSV file is written to `reports/` with a header row and the same figures as the screen. |

### 8.8 Employees (EMP)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-EMP-01 | Add an employee (Admin). | P2 | Name, phone, role, unique username and initial password. Password rules from BR-15. |
| FR-EMP-02 | Update, deactivate, reset password (Admin). | P2 | BR-16 is enforced. A deactivated employee cannot log in; their past sales remain. |
| FR-EMP-03 | List employees (Admin). | P2 | Shows name, username, role, active flag. |

### 8.9 Audit (AUD)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-AUD-01 | Record security-relevant and money-relevant actions. | P3 | Login success and failure, create/update/deactivate of any record, stock receive and adjust, sale create and void, password change. Each entry has who, when, what, and the record id. |
| FR-AUD-02 | Admin can view and filter the audit log. | P3 | Filter by employee, action and date range. |

### 8.10 System (SYS)

| ID | Requirement | Priority | Acceptance criteria |
|---|---|:---:|---|
| FR-SYS-01 | Central configuration. | P0 | Shop name and address, paths, thresholds, currency symbol and discount cap are defined in one config module. |
| FR-SYS-02 | Logging and friendly errors. | P0 | A rotating log file records unexpected errors with tracebacks. Users see a short message, never a traceback. |
| FR-SYS-03 | Automatic database setup. | P0 | The database file and schema are created on first run. Schema version is stored in `PRAGMA user_version`. |
| FR-SYS-04 | Demo data script. | P3 | One command loads sample suppliers, medicines, batches (including near-expiry and expired ones) and two employees. |
| FR-SYS-05 | Database backup command. | P3 | One command copies the database to `backups/` with a timestamped name. |

## 9. Non-functional requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Usability | Numbered menus, clear prompts, input re-prompted on error, confirmation before any destructive or irreversible action, consistent table output. |
| NFR-02 | Performance | Search, billing and alert queries complete in under 1 second with 10,000 medicines, 50,000 batches and 100,000 sales (indexes defined in the schema). |
| NFR-03 | Reliability | Foreign keys are enforced on every connection. Multi-step writes use a single transaction. No partial saves. |
| NFR-04 | Security | PBKDF2-HMAC-SHA256 with a random salt and at least 600,000 iterations. All SQL is parameterised. Passwords never appear in logs or the audit log. Authorization checked in services. |
| NFR-05 | Data integrity | Database `CHECK`, `UNIQUE` and `FOREIGN KEY` constraints back up the application rules. |
| NFR-06 | Maintainability | Strict layering (CLI, service, repository). Type hints on all functions. No business logic in the CLI or SQL in services. |
| NFR-07 | Testability | At least 80 percent line coverage on `pms/services`. Tests run against an in-memory database. |
| NFR-08 | Portability | Runs on Windows, macOS and Linux with Python 3.10+ and no third-party runtime dependencies. |
| NFR-09 | Observability | Rotating log files (for example 1 MB x 5). Errors include context such as employee id and operation name. |
| NFR-10 | Documentation | README, PRD, architecture, implementation plan and code docstrings stay in sync with behaviour. |

## 10. Data requirements

| Entity | Key attributes | Notes |
|---|---|---|
| Employee | name, phone, role, username, password hash, active, failed attempts, locked until | Soft-deleted via `is_active` |
| Supplier | name, contact person, phone, email, address, active | Name unique |
| Medicine | name, generic name, form, strength, category, manufacturer, preferred supplier, unit price, tax %, reorder level, prescription flag, active | Unique (name, form, strength) |
| Batch | medicine, supplier, batch number, quantity, initial quantity, purchase price, expiry date, received on, received by | Unique (medicine, batch number) |
| Sale | bill number, employee, customer name, prescription note, subtotal, discount %, discount, tax, total, payment method, status, void details, timestamp | Status COMPLETED or VOIDED |
| Sale item | sale, medicine, batch, quantity, unit price, tax %, line total | Price copied at sale time |
| Stock adjustment | batch, employee, delta, reason, note, timestamp | Reasons: DAMAGED, LOST, EXPIRED_WRITE_OFF, CORRECTION, SALE_VOID |
| Audit entry | employee, action, entity, entity id, details, timestamp | Append-only |

Column-level definitions are in [architecture.md](architecture.md#5-data-architecture).

## 11. Report specifications

**Daily sales summary**

| Field | Definition |
|---|---|
| Bills | Count of COMPLETED sales on the date |
| Items sold | Sum of line quantities |
| Gross | Sum of sale subtotals |
| Discounts | Sum of discount amounts |
| Tax | Sum of tax amounts |
| Net | Sum of sale totals |
| By payment method | Net total and bill count for CASH, CARD, ONLINE |

**Stock valuation:** per medicine and overall, `sum(quantity x purchase price)` and `sum(quantity x selling price)` over non-expired batches.

**Low-stock list:** medicine, available, reorder level, preferred supplier.

**Expiry report:** medicine, batch number, quantity, expiry date, days left (negative when expired), status (EXPIRED or EXPIRING).

**Top sellers:** medicine, quantity sold, net revenue, for a date range, descending by quantity.

**Sales by employee:** employee, bills, net total, for a date range.

## 12. Assumptions, constraints and dependencies

**Assumptions**

- A1: Implementation is **Python 3.10+ with SQLite**. If the language changes, update the architecture document first.
- A2: One shop, one machine, one user at a time.
- A3: The shop uses a single currency; prices are tax-exclusive.
- A4: The system clock of the machine is correct (expiry and bill numbers depend on it).

**Constraints**

- Solo student project; estimated effort 55 to 70 hours.
- No third-party runtime dependencies. `pytest` is for development only.
- Must be demonstrable offline.

**Dependencies:** Python runtime, SQLite (bundled with Python), a terminal.

## 13. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|:---:|:---:|---|
| Scope creep | High | High | Work strictly by priority; do not start P3 before P2 is done; P4 is out of scope |
| Stock inconsistencies from bugs in billing | Medium | High | Transactions, database constraints, tests for FEFO, rollback and void |
| Date and rounding mistakes | Medium | Medium | Dates as ISO text, money as integer minor units, dedicated helper modules with tests |
| Running out of time | Medium | High | Cut line: P0 + P1 + alerts + daily sales report is still a complete demo |
| Code the author cannot explain | Medium | High | Keep code simple, avoid clever abstractions, write docstrings, rehearse the viva questions in the plan |
| AI-generated code drifting from the design | Medium | Medium | `AGENTS.md` rules, one task at a time, tests required for every task |

## 14. Success metrics

| Metric | Target |
|---|---|
| All P0, P1, P2 acceptance criteria pass | 100 percent |
| Automated tests passing | 100 percent, with at least 80 percent coverage on services |
| Time to create a 3-item bill | Under 60 seconds |
| Expired medicines sold in tests | 0 |
| Stock mismatches after a sequence of receive, sell, void in tests | 0 |
| Viva: author can explain each layer, FEFO and the transaction flow | Yes |

## 15. Scope: release plan and exclusions

| Release | Content |
|---|---|
| **MVP (after P1)** | Login, medicines, suppliers, batches, billing with FEFO, bills, role checks |
| **v1.0 (after P2)** | Plus alerts, reports, employees, stock control, sales history, discounts |
| **v1.1 (after P3)** | Plus void sale, audit log, lockout, CSV export, demo data, backups, prescription flag |
| **Future (P4)** | Returns, purchase orders, barcode scanning, customer accounts, GUI or web front end, REST API, multi-branch |

## 16. Open questions

| # | Question | Default used until answered |
|---|---|---|
| Q1 | Which language will be used? | Python 3.10+ with SQLite |
| Q2 | Does the course require a specific document format (SRS, UML diagrams)? | This PRD acts as the SRS; add UML diagrams from the architecture document if required |
| Q3 | Should prices include tax? | Tax-exclusive; set tax % to 0 for tax-inclusive prices |
| Q4 | Is a printed hardcopy bill needed, or is a text file enough? | Console output plus text file |

## 17. Glossary

| Term | Meaning |
|---|---|
| **Batch** | One delivery lot of a medicine, with its own batch number, quantity and expiry date |
| **FEFO** | First Expired, First Out: sell the batch that expires soonest first |
| **Reorder level** | Stock quantity at or below which a medicine is considered low |
| **Minor units** | The smallest currency unit (paise, cents), used to store money as integers |
| **Soft delete** | Marking a record inactive instead of removing it |
| **Actor** | The logged-in employee performing an operation |
| **Write-off** | Removing stock from the system because it is expired or unusable |
| **Void** | Cancelling a completed sale and restoring its stock |
