from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterStoreRequest(BaseModel):
    store_name: str
    owner_name: str
    location: str
    email: str
    password: str

class RegisterEmployeeRequest(BaseModel):
    store_uid: str
    full_name: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    store_name: str

class MedicineSchema(BaseModel):
    id: Optional[int]
    name: str
    generic_name: str
    form: str
    strength: str
    category: str
    manufacturer: str
    unit_price_minor: int
    tax_percent: int
    reorder_level: int
    requires_prescription: bool
    is_active: bool
    description: Optional[str] = None

class EmployeeSchema(BaseModel):
    id: int
    full_name: str
    role: str
    is_active: bool
    store_uid: Optional[str] = None
