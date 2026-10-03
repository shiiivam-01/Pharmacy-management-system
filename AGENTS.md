# AGENTS.md

Instructions for AI coding agents (Antigravity, Claude Code, Copilot, Cursor and similar) working in this repository. Humans can read it too.

## 1. Project in one paragraph

**Pharmacy Management System (PMS)** is a menu-driven Python 3.10+ console application with a SQLite database. It manages medicines, **batches with expiry dates**, suppliers, employees, billing with **FEFO** stock allocation, alerts and reports. Two roles exist: **ADMIN** and **PHARMACIST**. It is a student learning project, built from scratch.

## 2. Read these first, in this order

1. `docs/prd.md`: what to build, requirement IDs, business rules (BR-xx), permissions.
2. `docs/architecture.md`: layers, schema, workflows, algorithms, error handling.
3. `docs/implementation-plan.md`: the ordered task list. **This decides what to work on.**

If code and documents disagree, **stop and report the conflict**. Do not silently pick one.

## 3. How to work

1. Open `docs/implementation-plan.md`. Take the **first task whose Status is not done** in the highest open priority (P0, then P1, then P2, then P3). Respect the Depends on column.
2. Work on **one task at a time**. Keep changes small and focused.
3. Implement the task, write its tests, run the full test suite.
4. Update the task's Status in the plan. Update docs if behaviour or schema changed.
5. Finish with a short summary: what changed, which files, how it was tested, anything unclear.

**This is a learning project.** The owner must be able to explain every line in a viva. Therefore:

- Prefer simple, readable code over clever abstractions, decorators, metaclasses or heavy patterns.
- Explain non-obvious decisions in a brief comment or in your summary.
- Do not generate large amounts of unrelated code. Do not implement later tasks "while you're there".

## 4. Commands

```bash
python -m venv .venv                 # once
.venv\Scripts\activate               # Windows
source .venv/bin/activate            # macOS / Linux
python -m pip install -r requirements.txt

python main.py                       # run the app
python -m pytest                     # run all tests (must pass before you finish)
python -m pytest tests/test_billing_service.py -k fefo    # run a subset
python -m pytest --cov=pms/services  # coverage, only if pytest-cov is installed
```

## 5. Repository map

```
main.py                    entry point
pms/config.py              constants and settings
pms/logger.py              logging setup
pms/exceptions.py          PMSError hierarchy
pms/money.py               Decimal <-> integer minor units, rounding
pms/validators.py          input validation (raises ValidationError)
pms/security.py            password hashing, PERMISSIONS, require()
pms/database.py            connect(), init_schema(), transaction()
pms/schema.sql             database schema (source of truth)
pms/models.py              dataclasses
pms/repositories/          SQL only
pms/services/              business rules, permissions, transactions
pms/cli/                   menus and console helpers
scripts/                   seed_demo.py, backup_db.py
tests/                     pytest tests, conftest.py with in-memory DB
docs/                      prd.md, architecture.md, implementation-plan.md
```

## 6. Architecture rules (non-negotiable)

1. **Dependencies point downward only:** `cli` calls `services`, `services` call `repositories`, `repositories` use `database`. Never the reverse.
2. **Only `pms/cli/` may call `print()` or `input()`.**
3. **Only `pms/repositories/` may contain SQL.** All SQL is **parameterised** (`?` or `:name`). Never build SQL with f-strings, `%` or `+`.
4. **Only services start transactions and check permissions.** Repositories never commit. Use `with transaction(conn):`.
5. **Every service method takes `actor` (a `Session`) first** and calls `security.require(actor, "<permission>")` before doing anything.
6. **Services raise exceptions** from `pms/exceptions.py`. They never return error strings or `None` to mean failure.
7. **No business rules in the CLI**, and no rendering or printing in services (except the pure function that builds the bill text).
8. Menu functions wrap service calls in `try/except PMSError` and show `str(error)`.

## 7. Domain rules you must not break

- **Expiry belongs to batches.** Available stock = sum of `quantity` over batches with `expiry_date >= today`. Expired batches are never sold.
- **FEFO:** allocate from the earliest `expiry_date` first (tie: lowest `id`). A sale line spanning batches creates one `sale_items` row per batch.
- **Stock never goes negative.** Check in code and rely on the `CHECK` constraint as a backstop.
- **Money is integer minor units** in the database and `Decimal` in code. **Never use `float` for money.** Round half-up per line (BR-10). Prices are tax-exclusive.
- **Never hard-delete** employees, suppliers, medicines, batches, sales. Use `is_active` (and `status = 'VOIDED'` for sales).
- **Copy price and tax %** onto each sale line at sale time (BR-11).
- `create_sale`, `void_sale`, `receive_stock`, `adjust_stock`, write-off and password reset each run in **one transaction**, using `BEGIN IMMEDIATE`.
- Pass `today` (a `date`) into service methods that depend on it, defaulting to `date.today()`, so tests can control the clock.
- Dates are ISO `YYYY-MM-DD` text. Timestamps are local-time ISO text.

## 8. Security rules

- Passwords: PBKDF2-HMAC-SHA256, random salt, `config.PBKDF2_ITERATIONS`, stored as `pbkdf2_sha256$iterations$salt_hex$hash_hex`. Compare with `hmac.compare_digest`.
- Login errors are **generic**: never reveal whether the username or the password was wrong.
- **Never log or audit passwords, hashes or full input dictionaries.**
- Pharmacist data scoping (own sales only) is enforced **in the service**, not the menu.
- Output file names are generated by the program (bill number, timestamp), never taken from user input.
- Do not commit `data/`, `bills/`, `reports/`, `logs/`, `backups/`, `.venv/`, or any `*.db` file.

## 9. Code style

- Python 3.10+, PEP 8, 4 spaces, lines up to about 100 characters.
- **Type hints on every function.** A one- or two-line docstring on every public function and class.
- Names: `snake_case` functions and variables, `PascalCase` classes, `UPPER_CASE` constants. Files and test files as in the repository map.
- Use `dataclasses` for models. Use `pathlib` for paths. Use `logging`, not `print`, for diagnostics.
- Keep functions short and single-purpose. Avoid deep nesting; return early.
- Standard library only at runtime. **Do not add a dependency without asking.** `pytest` (and optionally `pytest-cov`) are for development only.

## 10. Testing rules

- Every task ships with tests. A bug fix ships with a test that fails before the fix.
- Tests use the **in-memory SQLite fixture** in `tests/conftest.py`. Never touch `data/pharmacy.db`.
- Control time by passing `today`. Lower `PBKDF2_ITERATIONS` in tests.
- Test the **service layer** most heavily. Required scenarios are listed in `docs/architecture.md`, section 13.
- Run the **whole suite** before finishing. Do not leave failing or skipped tests without explaining why.
- Target: at least 80 percent line coverage on `pms/services`.

## 11. Schema and documentation changes

- `pms/schema.sql` is the source of truth. If you change it, **in the same change** update:
  1. the reference schema and ER diagram in `docs/architecture.md`,
  2. the repositories that touch the changed tables,
  3. the tests and the `PRAGMA user_version` if it is a migration.
- If you change behaviour covered by a PRD requirement, update the PRD and the README.
- Never edit `docs/` to match code that violates a rule. Fix the code, or ask.

## 12. Git conventions

- Small commits, one logical change each.
- Messages follow `type: short summary` with types `feat`, `fix`, `test`, `docs`, `refactor`, `chore`. Example: `feat: allocate stock by FEFO`.
- Branches: `feature/<task-id>-<short-name>`, for example `feature/T-104-fefo-allocation`.
- Do not rewrite shared history. Do not commit secrets or database files.

## 13. Ask before you

- add a dependency or change the Python version,
- change the schema in a way that is not described in the docs,
- change a permission, business rule or requirement,
- rename or move modules, or change the layering,
- delete files or data,
- start a task that is not next in the plan.

## 14. Common pitfalls

| Pitfall | Do this instead |
|---|---|
| Forgetting `PRAGMA foreign_keys = ON` | It is set in `database.connect()`; always connect through it |
| Checking stock outside the transaction only | Re-check and allocate **inside** `BEGIN IMMEDIATE` |
| Using `float` for prices or tax | Use `Decimal`, store integer minor units |
| Counting expired stock as available | Always filter `expiry_date >= today` |
| Deleting a row that has history | Set `is_active = 0` |
| Putting `print()` in a service | Return data; let the CLI print |
| Hiding a menu item but not checking in the service | Always call `require()` in the service |
| Using today's real date inside tests | Pass `today` explicitly |
| Logging a password or hash | Never |
| Doing three tasks at once | One task, then test, then next |

## 15. Definition of done

A task is done only when the behaviour meets the plan's **Done when** column and the PRD criteria, the layering and domain rules above hold, type hints and docstrings exist, tests were added and the **full suite passes**, documentation was updated where needed, the commit message follows the convention, and the plan's Status column is updated.

## 16. Prompt examples

- "Do the next open task in `docs/implementation-plan.md`."
- "Implement T-104 (FEFO allocation) exactly as in `docs/architecture.md` section 7.1, with the tests listed in the plan."
- "Review `pms/services/billing_service.py` against the architecture rules and domain rules in `AGENTS.md`. List violations; do not change code yet."
- "Explain how `create_sale` works step by step, so I can describe it in my viva."
