from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.database import connect
from backend.services.auth_service import AuthService
from backend.models import Session
import sqlite3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()

# For a real cloud app, you'd use JWTs. For this quick MVP bridge, 
# we verify by re-authenticating the username/pass or an API key. 
# Here we simulate a session by looking up the active employee.
def get_current_actor(token: str = Depends(oauth2_scheme), conn: sqlite3.Connection = Depends(get_db)) -> Session:
    # In a full app, 'token' would be a decoded JWT.
    # We will simulate decoding by just fetching the employee ID directly from the token string for MVP purposes.
    # DO NOT use this plain token approach in production.
    try:
        employee_id = int(token)
        cursor = conn.execute("SELECT * FROM employees WHERE id = ? AND is_active = 1", (employee_id,))
        row = cursor.fetchone()
        if not row:
            raise Exception()
            
        return Session(
            employee_id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            role=row["role"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
