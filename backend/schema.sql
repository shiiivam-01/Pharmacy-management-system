PRAGMA foreign_keys = ON;

CREATE TABLE employees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT    NOT NULL,
    phone           TEXT,
    role            TEXT    NOT NULL CHECK (role IN ('ADMIN', 'PHARMACIST')),
    username        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    -- format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    password_hash   TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT,
    hired_on        TEXT    NOT NULL DEFAULT (date('now', 'localtime')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE suppliers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    contact_person TEXT,
    phone          TEXT,
    email          TEXT,
    address        TEXT,
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE medicines (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT    NOT NULL COLLATE NOCASE,
    generic_name          TEXT    COLLATE NOCASE,
    form                  TEXT    NOT NULL COLLATE NOCASE,   -- tablet, capsule, syrup, injection ...
    strength              TEXT    NOT NULL DEFAULT '' COLLATE NOCASE,   -- e.g. 500mg
    category              TEXT    COLLATE NOCASE,
    manufacturer          TEXT,
    supplier_id           INTEGER REFERENCES suppliers (id),
    unit_price_minor      INTEGER NOT NULL CHECK (unit_price_minor > 0),
    tax_percent           REAL    NOT NULL DEFAULT 0 CHECK (tax_percent BETWEEN 0 AND 100),
    reorder_level         INTEGER NOT NULL DEFAULT 10 CHECK (reorder_level >= 0),
    requires_prescription INTEGER NOT NULL DEFAULT 0 CHECK (requires_prescription IN (0, 1)),
    is_active             INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at            TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at            TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (name, form, strength)
);
CREATE INDEX idx_medicines_generic  ON medicines (generic_name);
CREATE INDEX idx_medicines_category ON medicines (category);

CREATE TABLE batches (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id          INTEGER NOT NULL REFERENCES medicines (id),
    supplier_id          INTEGER REFERENCES suppliers (id),
    batch_no             TEXT    NOT NULL,
    quantity             INTEGER NOT NULL CHECK (quantity >= 0),
    initial_quantity     INTEGER NOT NULL CHECK (initial_quantity > 0),
    purchase_price_minor INTEGER NOT NULL CHECK (purchase_price_minor >= 0),
    expiry_date          TEXT    NOT NULL,                  -- YYYY-MM-DD
    received_on          TEXT    NOT NULL DEFAULT (date('now', 'localtime')),
    received_by          INTEGER REFERENCES employees (id),
    UNIQUE (medicine_id, batch_no)
);
CREATE INDEX idx_batches_fefo   ON batches (medicine_id, expiry_date) WHERE quantity > 0;
CREATE INDEX idx_batches_expiry ON batches (expiry_date);

CREATE TABLE sales (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_no           TEXT    NOT NULL UNIQUE,             -- PMS-YYYYMMDD-NNNN
    employee_id       INTEGER NOT NULL REFERENCES employees (id),
    customer_name     TEXT,
    prescription_note TEXT,
    subtotal_minor    INTEGER NOT NULL CHECK (subtotal_minor >= 0),
    discount_percent  REAL    NOT NULL DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 100),
    discount_minor    INTEGER NOT NULL DEFAULT 0 CHECK (discount_minor >= 0),
    tax_minor         INTEGER NOT NULL DEFAULT 0 CHECK (tax_minor >= 0),
    total_minor       INTEGER NOT NULL CHECK (total_minor >= 0),
    payment_method    TEXT    NOT NULL DEFAULT 'CASH' CHECK (payment_method IN ('CASH', 'CARD', 'ONLINE')),
    status            TEXT    NOT NULL DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED', 'VOIDED')),
    void_reason       TEXT,
    voided_by         INTEGER REFERENCES employees (id),
    voided_at         TEXT,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX idx_sales_created  ON sales (created_at);
CREATE INDEX idx_sales_employee ON sales (employee_id, created_at);

CREATE TABLE sale_items (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id          INTEGER NOT NULL REFERENCES sales (id),
    medicine_id      INTEGER NOT NULL REFERENCES medicines (id),
    batch_id         INTEGER NOT NULL REFERENCES batches (id),
    quantity         INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_minor INTEGER NOT NULL CHECK (unit_price_minor > 0),  -- copied at sale time (BR-11)
    tax_percent      REAL    NOT NULL DEFAULT 0,                      -- copied at sale time
    line_total_minor INTEGER NOT NULL                                 -- quantity x unit price, before discount and tax
);
CREATE INDEX idx_sale_items_sale     ON sale_items (sale_id);
CREATE INDEX idx_sale_items_medicine ON sale_items (medicine_id);

CREATE TABLE stock_adjustments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id    INTEGER NOT NULL REFERENCES batches (id),
    employee_id INTEGER NOT NULL REFERENCES employees (id),
    delta       INTEGER NOT NULL CHECK (delta <> 0),
    reason      TEXT    NOT NULL CHECK (reason IN ('DAMAGED', 'LOST', 'EXPIRED_WRITE_OFF', 'CORRECTION', 'SALE_VOID')),
    note        TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER REFERENCES employees (id),   -- NULL for failed logins of unknown users
    action      TEXT    NOT NULL,
    entity      TEXT,
    entity_id   INTEGER,
    details     TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX idx_audit_created ON audit_log (created_at);

PRAGMA user_version = 1;
