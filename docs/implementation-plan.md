# Implementation Plan: Pharmacy Management System (PMS)

| | |
|---|---|
| **Version** | 1.0 |
| **Date** | 2026-10-03 |
| **Related** | [README](../README.md), [PRD](prd.md), [architecture](architecture.md) |
| **Total estimate** | About 55 to 70 hours for P0 to P3 plus documentation |

Update the **Status** column as you work: `☐` not started, `🔄` in progress, `✅` done.

---

## Table of Contents

1. [How to use this plan](#1-how-to-use-this-plan)
2. [Priority levels](#2-priority-levels)
3. [Summary and schedule](#3-summary-and-schedule)
4. [P0: Foundation](#4-p0-foundation)
5. [P1: Core MVP](#5-p1-core-mvp)
6. [P2: Important](#6-p2-important)
7. [P3: Hardening and polish](#7-p3-hardening-and-polish)
8. [P4: Future ideas](#8-p4-future-ideas)
9. [Documentation and submission tasks](#9-documentation-and-submission-tasks)
10. [Definition of done](#10-definition-of-done)
11. [If time runs short](#11-if-time-runs-short)
12. [Viva preparation](#12-viva-preparation)

---

## 1. How to use this plan

1. Work **strictly in priority order**: finish all of P0, then P1, and so on. Do not start P3 while P2 has open tasks.
2. Inside a priority, follow the **Depends on** column.
3. For every task: write the code, write its tests, run `python -m pytest`, then commit with a clear message.
4. A task is done only when its **Done when** condition is true and it meets the [definition of done](#10-definition-of-done).
5. The **Covers** column links each task to requirement IDs in the [PRD](prd.md#8-functional-requirements).
6. Estimates assume a beginner working carefully. Treat them as a guide, not a promise.

## 2. Priority levels

| Priority | Name | Meaning | Outcome |
|---|---|---|---|
| **P0** | Foundation | Everything else depends on it | App starts, database exists, you can log in |
| **P1** | Core MVP | The pharmacy's main loop works | Receive stock, sell it with FEFO, print a bill |
| **P2** | Important | Makes it a complete, useful system | Alerts, reports, staff management, stock control |
| **P3** | Hardening | Robustness and polish | Void sale, audit, lockout, export, demo data, higher coverage |
| **P4** | Future | Not part of this project | Ideas only |

## 3. Summary and schedule

| Priority | Tasks | Estimate |
|---|---|---|
| P0 Foundation | T-001 to T-009 | 12 h |
| P1 Core MVP | T-101 to T-109 | 21.5 h |
| P2 Important | T-201 to T-209 | 14 h |
| P3 Hardening | T-301 to T-309 | 11 h |
| Documentation | D-01 to D-06 | 5 h |
| **Total** | | **63.5 h** |

**Suggested schedule (about 16 hours a week)**

| Week | Focus | Milestone at the end of the week |
|---|---|---|
| 1 | P0, then suppliers and medicines (T-101, T-102) | **M0:** you can log in; medicines and suppliers can be managed |
| 2 | Rest of P1 | **M1 (MVP):** receive stock, sell with FEFO, print and save a bill, permissions enforced |
| 3 | P2 | **M2 (v1.0):** alerts, reports, employees, stock control, sales history |
| 4 | P3 and documentation | **M3 (v1.1):** hardened, tested, documented, demo-ready |

## 4. P0: Foundation

| ID | Task | Est. | Depends on | Covers | Done when | Status |
|---|---|:---:|---|---|---|:---:|
| T-001 | Create the repository, folder structure from the README, `.gitignore`, `requirements.txt` (pytest), empty package files | 0.5 h | none | | `python main.py` runs without error (prints a placeholder); folders match the README tree; `data/`, `bills/`, `reports/`, `logs/`, `backups/` are ignored by Git | ✅ |
| T-002 | `config.py` and `logger.py` (rotating file log plus console) | 1 h | T-001 | FR-SYS-01, FR-SYS-02 | Settings are read from one module; a log line appears in `logs/pms.log`; log rotates at 1 MB | ✅ |
| T-003 | `exceptions.py`, `validators.py`, `money.py` with tests | 1.5 h | T-001 | NFR-06 | Exception hierarchy exists; validators reject bad input with `ValidationError`; money converts both ways with half-up rounding; tests pass | ✅ |
| T-004 | `schema.sql` and `database.py` (`connect`, `init_schema`, `transaction`) | 2 h | T-002 | FR-SYS-03, NFR-03 | First run creates the database; foreign keys are on; `transaction()` rolls back on error (tested); `user_version` is 1 | ✅ |
| T-005 | `security.py`: password hash and verify, `PERMISSIONS`, `require` | 1 h | T-003 | NFR-04, FR-AUTH-03 | Hash format as in the architecture; same password gives different hashes; verify works; `require` raises `AuthorizationError` for a disallowed role; tests pass | ✅ |
| T-006 | `models.py` dataclasses | 1 h | T-001 | | All models in the architecture exist with type hints | ✅ |
| T-007 | Test infrastructure: `conftest.py` with in-memory database and session fixtures | 1 h | T-004, T-006 | NFR-07 | A sample test using the `db` fixture passes; tests never touch `data/pharmacy.db` | ✅ |
| T-008 | `cli/console.py` helpers (`ask_text`, `ask_int`, `ask_decimal`, `ask_date`, `ask_choice`, `confirm`, `print_table`) and the `app.py` menu loop skeleton | 1.5 h | T-003 | NFR-01 | Helpers re-prompt on bad input; a table prints aligned; the skeleton shows a main menu and exits cleanly | ✅ |
| T-009 | `EmployeeRepository`, `AuthService` (bootstrap, login), login menu | 2.5 h | T-004, T-005, T-007, T-008 | FR-AUTH-01, FR-AUTH-02 | Empty database triggers Admin creation once; correct login opens a session; wrong login shows one generic message; inactive account cannot log in; tests pass | ✅ |

**Milestone check (M0 foundation):** run the app twice. The first run creates an Admin; the second run goes straight to login.

## 5. P1: Core MVP

| ID | Task | Est. | Depends on | Covers | Done when | Status |
|---|---|:---:|---|---|---|:---:|
| T-101 | Suppliers: `SupplierRepository`, `SupplierService`, `supplier_menu` (add, list, update, deactivate) | 2 h | T-009 | FR-SUP-01 to 03 | All four actions work from the menu; duplicate name rejected; inactive supplier hidden from selection; tests pass | ✅ |
| T-102 | Medicines: repository, service, menu (add, list, view, update, deactivate, search) | 4 h | T-101 | FR-MED-01 to 05 | Duplicate (name, form, strength) rejected; search is partial and case-insensitive; deactivated medicine does not appear in search for billing; tests pass | ✅ |
| T-103 | Inventory: `BatchRepository`, `InventoryService.receive_stock`, view batches, available stock | 3 h | T-102 | FR-INV-01 to 03 | Receiving a batch raises available stock; duplicate batch number and past expiry rejected; expired batches excluded from availability; tests pass | ✅ |
| T-104 | FEFO allocation function with thorough unit tests | 2 h | T-103 | FR-BILL-02, BR-02 | Tests cover single batch, spanning batches, expired skipped, tie on expiry, insufficient stock | ✅ |
| T-105 | Billing part 1: cart handling, totals and rounding in `BillingService` | 3 h | T-104 | FR-BILL-01, 03, 04 | Same medicine merges; totals match hand-calculated cases including a rounding edge case; insufficient stock rejected with available quantity | ✅ |
| T-106 | Billing part 2: atomic `create_sale`, bill numbering, sale repository | 3 h | T-105 | FR-BILL-05, 06, BR-12, BR-13 | Sale, items and stock change commit together; an injected failure rolls everything back (tested); bill numbers are unique and increasing | ✅ |
| T-107 | Bill rendering to console and `bills/<bill_no>.txt`; `billing_menu` new-sale flow | 1.5 h | T-106 | FR-BILL-06 | Bill matches the README sample layout; file exists after a sale; the whole flow works from the menu | ✅ |
| T-108 | Enforce roles in every service and filter menus by role | 1.5 h | T-107 | FR-AUTH-03 | Each Admin-only action raises `AuthorizationError` for a Pharmacist (tested); menus show only allowed items | ✅ |
| T-109 | Integration tests: receive, sell, check stock; sell across batches; deny pharmacist | 1.5 h | T-108 | | End-to-end tests pass using only service calls | ✅ |

**Milestone check (M1 MVP):** from a clean database, create a supplier and a medicine, receive two batches with different expiry dates, sell enough to span both, and confirm the bill, the saved file and the remaining stock are correct. Repeat with an expired batch present.

## 6. P2: Important

| ID | Task | Est. | Depends on | Covers | Done when | Status |
|---|---|:---:|---|---|---|:---:|
| T-201 | `AlertService` and login dashboard (low stock, expiring soon, expired with stock) | 2.5 h | T-109 | FR-ALR-01 to 04 | Boundary tests pass: exactly at reorder level, expiring on day N and N+1, expiring today; dashboard shows counts with drill-down | ✅ |
| T-202 | Employee management: service and menu (add, list, update, deactivate, reset password) | 2 h | T-109 | FR-EMP-01 to 03, BR-16 | Last active Admin and self cannot be deactivated (tested); deactivated user cannot log in | ✅ |
| T-203 | Change own password and logout | 0.5 h | T-202 | FR-AUTH-04 | Needs current password; new password rules enforced | ✅ |
| T-204 | Stock adjustment and expired write-off (Admin) | 2 h | T-109 | FR-INV-04, 05 | Reason mandatory; cannot go below 0; adjustment rows recorded; write-off zeroes the batch | ✅ |
| T-205 | Sales history, filter by date or bill number, reprint | 1.5 h | T-109 | FR-BILL-08 | Pharmacist sees only own sales; Admin sees all; reprint identical to original | ✅ |
| T-206 | Discounts with the pharmacist cap | 1 h | T-109 | FR-BILL-07 | Pharmacist above cap is rejected; Admin can go to 100 percent; totals still correct | ✅ |
| T-207 | Reports: daily sales summary, stock valuation, low-stock list, expiry report | 3 h | T-201 | FR-RPT-01 to 03 | Figures match hand calculation on test data; voided sales excluded; pharmacist sees own daily sales only | ✅ |
| T-208 | Filters by category and supplier; reactivate medicine | 1 h | T-102 | FR-MED-06 | Filters combine with search; reactivated medicine sellable | ✅ |
| T-209 | Pagination in long lists | 0.5 h | T-102 | NFR-01 | Lists show `PAGE_SIZE` rows with next and previous | ✅ |

**Milestone check (M2 v1.0):** log in as a Pharmacist and as an Admin and walk through every menu from the README. Nothing should crash, and every Admin-only item should be missing or refused for the Pharmacist.

## 7. P3: Hardening and polish

| ID | Task | Est. | Depends on | Covers | Done when | Status |
|---|---|:---:|---|---|---|:---:|
| T-301 | Void sale (Admin) | 2 h | T-205 | FR-BILL-09, BR-14 | Stock restored to the same batches; sale marked VOIDED; excluded from reports; cannot void twice; tests pass | ✅ |
| T-302 | Audit log: write entries from services and an Admin viewer with filters | 1.5 h | T-109 | FR-AUD-01, 02 | All actions listed in the architecture create entries; no passwords appear in entries | ✅ |
| T-303 | Login lockout | 1 h | T-009 | FR-AUTH-05 | Fifth failure locks for 5 minutes; success resets; tested with an injected clock | ✅ |
| T-304 | CSV export for reports; range sales, top sellers, sales by employee | 1 h | T-207 | FR-RPT-04 to 06 | CSV opens in a spreadsheet with a header row and the same figures as the screen | ✅ |
| T-305 | `scripts/seed_demo.py` | 1 h | T-109 | FR-SYS-04 | One command fills a clean database with realistic data including near-expiry and expired batches | ✅ |
| T-306 | `scripts/backup_db.py` | 0.5 h | T-004 | FR-SYS-05 | Timestamped copy appears in `backups/` | ✅ |
| T-307 | Prescription flag with confirmation | 1 h | T-109 | FR-BILL-10 | Flagged medicine requires confirmation; note saved on the sale | ✅ |
| T-308 | Raise coverage and add edge-case tests; fix the bugs found | 2 h | all P2 | NFR-07 | Coverage on `pms/services` is at least 80 percent; all must-have scenarios from the architecture are tested | ✅ |
| T-309 | Cleanup: type hints, docstrings, remove dead code, consistent naming, optional linter | 1 h | T-308 | NFR-06, NFR-10 | No unused code; every public function has a docstring and type hints | ✅ |

## 8. P4: Future ideas

Not part of this project. Pick one only after P3 is done and documented.

| Idea | Notes |
|---|---|
| Returns and refunds | New table referencing `sale_items`; stock restored via adjustments |
| Purchase orders to suppliers | Generate orders from the low-stock list; link batches to orders |
| Barcode scanning | Barcode column on medicines; scanner works as keyboard input |
| GUI (Tkinter) or web front end | Reuse the service layer unchanged |
| Customer accounts and loyalty | New table; link to sales |
| REST API | Thin layer over services |
| Multi-branch | Needs a client-server database and UTC timestamps |

## 9. Documentation and submission tasks

| ID | Task | Est. | When | Done when | Status |
|---|---|:---:|---|---|:---:|
| D-01 | Export the ER diagram and layer diagram as images for the report | 0.5 h | after P0 | Images saved in `docs/images/` | ☐ |
| D-02 | Test-case table: ID, scenario, input, expected result, actual result, pass or fail | 1.5 h | after P2 | Covers every P1 and P2 requirement | ☐ |
| D-03 | Screenshots of each main flow (login, receive stock, bill, alerts, reports) | 0.5 h | after P2 | Saved in `docs/images/` and linked from the README | ☐ |
| D-04 | Short user manual: how an Admin and a Pharmacist use the system | 1 h | after P2 | One page per role | ☐ |
| D-05 | Update README status, features and limitations to match what is built | 0.5 h | at the end | No statement in the README is untrue | ☐ |
| D-06 | Tag release `v1.0` in Git and write release notes | 1 h | at the end | Tag exists; notes list what is included | ☐ |

## 10. Definition of done

A task is **done** only when all of these are true:

- [ ] The behaviour matches the task's **Done when** column and the linked PRD acceptance criteria.
- [ ] Layering rules hold: no `print` or `input` in services, no SQL outside repositories, no business rules in the CLI.
- [ ] New code has type hints and a short docstring.
- [ ] Tests for the new behaviour exist and `python -m pytest` passes in full.
- [ ] If the schema changed, `schema.sql`, `architecture.md` and the tests were updated together.
- [ ] If behaviour changed, the README or PRD was updated.
- [ ] The change is committed with a clear message (for example `feat: allocate stock by FEFO`).
- [ ] The Status column in this file is updated.

## 11. If time runs short

Cut from the bottom up. Each level below is still a complete, demonstrable system.

| You finish | You can honestly say |
|---|---|
| P0 + P1 | "A working pharmacy system: stock by batch with expiry, FEFO billing, bills, roles." |
| P0 + P1 + T-201 + T-207 | "Plus alerts and a daily sales report." Best minimum for a demo. |
| P0 + P1 + P2 | "A complete system with alerts, reports, staff management and stock control." |
| P0 to P3 | "Hardened, audited, tested and documented." |

Never skip: tests for billing, rollback behaviour, and the README accuracy task (D-05).

## 12. Viva preparation

Be able to answer these in your own words, without looking at the code:

1. What problem does the system solve, and for whom?
2. Why is expiry stored on the batch and not on the medicine?
3. What is FEFO, and how does your code allocate across several batches?
4. What happens if the power fails halfway through a sale? (Transactions and rollback.)
5. Why are money amounts stored as integers?
6. Why do services, not menus, check permissions?
7. How are passwords stored, and why not in plain text?
8. Why soft delete instead of deleting rows?
9. What does each layer do, and why can't the CLI call SQL?
10. Which bug did you find through tests, and how did you fix it?
11. What would you change to add a web front end?
12. What are the system's limitations?

Practise by drawing the layer diagram and the sale workflow from memory.
