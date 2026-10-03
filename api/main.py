from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.database import init_schema
from api.routers import auth, medicines

app = FastAPI(title="Pharmacy Management System API", version="1.0")

# Allow any frontend (like Flet or a Web UI) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure database is initialized when API starts
    init_schema()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pharmacy Management System API!"}

# Register our API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(medicines.router, prefix="/api/medicines", tags=["Medicines"])

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
