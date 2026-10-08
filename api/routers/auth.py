from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from backend.services.auth_service import AuthService
from backend.exceptions import AuthenticationError, ValidationError
from api.deps import get_db
from api.schemas import LoginRequest, TokenResponse, RegisterStoreRequest, RegisterEmployeeRequest

router = APIRouter()

@router.post("/register/store")
def register_store(req: RegisterStoreRequest, conn: sqlite3.Connection = Depends(get_db)):
    auth_service = AuthService(conn)
    try:
        store = auth_service.register_store(req.store_name, req.owner_name, req.location, req.email, req.password)
        return {"message": "Store registered successfully", "store_uid": store.store_uid}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register/employee")
def register_employee(req: RegisterEmployeeRequest, conn: sqlite3.Connection = Depends(get_db)):
    auth_service = AuthService(conn)
    try:
        store = auth_service.register_employee(req.store_uid, req.full_name, req.email, req.password)
        return {"message": "Employee registered successfully", "store_name": store.name}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, conn: sqlite3.Connection = Depends(get_db)):
    auth_service = AuthService(conn)
    try:
        session = auth_service.login(request.username, request.password)
        # Using employee_id as a dummy token for this MVP bridge
        return TokenResponse(
            access_token=str(session.employee_id),
            role=session.role,
            full_name=session.full_name,
            store_name=session.store_name
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
