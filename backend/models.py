"""
Data models for the Pharmacy Management System.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Session:
    """Represents the logged-in user."""
    employee_id: int
    store_id: int
    store_name: str
    username: str
    role: str
    full_name: str

@dataclass
class Store:
    id: int
    store_uid: str
    name: str
    owner_name: str
    location: Optional[str]
    created_at: str

@dataclass
class Employee:
    id: int
    store_id: int
    full_name: str
    phone: Optional[str]
    role: str
    username: str
    password_hash: str
    is_active: int
    failed_attempts: int
    locked_until: Optional[str]
    hired_on: str
    created_at: str

@dataclass
class Supplier:
    id: int
    store_id: int
    name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    is_active: int
    created_at: str
    medicine_count: int = 0

@dataclass
class Medicine:
    id: int
    store_id: int
    name: str
    generic_name: Optional[str]
    form: str
    strength: str
    category: Optional[str]
    manufacturer: Optional[str]
    supplier_id: Optional[int]
    unit_price_minor: int
    tax_percent: float
    reorder_level: int
    requires_prescription: int
    is_active: int
    created_at: str
    updated_at: str
    description: Optional[str] = None
    available_stock: int = 0

@dataclass
class Batch:
    id: int
    store_id: int
    medicine_id: int
    supplier_id: Optional[int]
    batch_no: str
    quantity: int
    initial_quantity: int
    purchase_price_minor: int
    expiry_date: str
    received_on: str
    received_by: Optional[int]
    days_to_expiry: int = 0

@dataclass
class Sale:
    id: int
    store_id: int
    bill_no: str
    employee_id: int
    customer_name: Optional[str]
    prescription_note: Optional[str]
    subtotal_minor: int
    discount_percent: float
    discount_minor: int
    tax_minor: int
    total_minor: int
    payment_method: str
    status: str
    void_reason: Optional[str]
    voided_by: Optional[int]
    voided_at: Optional[str]
    created_at: str

@dataclass
class SaleItem:
    id: int
    store_id: int
    sale_id: int
    medicine_id: int
    batch_id: int
    quantity: int
    unit_price_minor: int
    tax_percent: float
    line_total_minor: int

@dataclass
class StockAdjustment:
    id: int
    store_id: int
    batch_id: int
    employee_id: int
    delta: int
    reason: str
    note: Optional[str]
    created_at: str

@dataclass
class AuditEntry:
    id: int
    store_id: Optional[int]
    employee_id: Optional[int]
    action: str
    entity: Optional[str]
    entity_id: Optional[int]
    details: Optional[str]
    created_at: str

@dataclass
class CartLine:
    medicine_id: int
    medicine_name: str
    quantity: int
    unit_price_minor: int
    tax_percent: float
    requires_prescription: bool
