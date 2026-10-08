from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from pydantic import BaseModel
from backend.models import Session
from backend.repositories.store_repository import StoreRepository
from backend.services.auth_service import AuthService
from api.deps import get_db, get_current_actor

router = APIRouter()

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.get("/store-uid")
def get_store_uid(conn: sqlite3.Connection = Depends(get_db), actor: Session = Depends(get_current_actor)):
    store_repo = StoreRepository(conn)
    store = store_repo.get(actor.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    return {"store_uid": store.store_uid, "store_name": store.name, "location": store.location}

@router.post("/change-password")
def change_password(req: ChangePasswordRequest, conn: sqlite3.Connection = Depends(get_db), actor: Session = Depends(get_current_actor)):
    auth_service = AuthService(conn)
    try:
        auth_service.change_password(actor, req.current_password, req.new_password)
        conn.commit()
        return {"message": "Password changed successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from typing import List
from api.schemas import EmployeeSchema
from backend.repositories.employee_repository import EmployeeRepository

@router.get("/members", response_model=List[EmployeeSchema])
def get_store_members(conn: sqlite3.Connection = Depends(get_db), actor: Session = Depends(get_current_actor)):
    # This ensures that only employees of the same store can be retrieved
    emp_repo = EmployeeRepository(conn)
    employees = emp_repo.get_all(actor.store_id)
    
    store_repo = StoreRepository(conn)
    store = store_repo.get(actor.store_id)
    store_uid = store.store_uid if store else "UNKNOWN"
    
    # Return mapped schema
    results = []
    for emp in employees:
        results.append(EmployeeSchema(
            id=emp.id,
            full_name=emp.full_name,
            role=emp.role,
            is_active=bool(emp.is_active),
            store_uid=store_uid
        ))
    return results
