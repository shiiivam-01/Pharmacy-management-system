from fastapi import APIRouter, Depends, HTTPException, status
import sqlite3
from backend.services.auth_service import AuthService
from backend.exceptions import AuthenticationError, LockoutError
from api.deps import get_db
from api.schemas import LoginRequest, TokenResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, conn: sqlite3.Connection = Depends(get_db)):
    auth_service = AuthService(conn)
    try:
        session = auth_service.login(request.username, request.password)
        # Using employee_id as a dummy token for this MVP bridge
        return TokenResponse(
            access_token=str(session.employee_id),
            role=session.role,
            full_name=session.full_name
        )
    except LockoutError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
