from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from backend.database import init_schema
from api.routers import auth, medicines, profile
import os

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
    from backend.database import connect, init_schema
    conn = connect()
    try:
        conn.execute("SELECT 1 FROM stores LIMIT 1")
    except Exception:
        init_schema(conn)
    conn.close()

# Mount the static web folder
web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "web")
app.mount("/static", StaticFiles(directory=web_dir), name="static")

class NoCacheFileResponse(FileResponse):
    def set_stat_headers(self, stat_result) -> None:
        super().set_stat_headers(stat_result)
        self.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        self.headers["Pragma"] = "no-cache"
        self.headers["Expires"] = "0"

@app.get("/")
def read_root():
    return NoCacheFileResponse(os.path.join(web_dir, "login.html"))

@app.get("/dashboard")
def dashboard():
    return NoCacheFileResponse(os.path.join(web_dir, "dashboard.html"))

@app.get("/pos")
def pos():
    return NoCacheFileResponse(os.path.join(web_dir, "pos.html"))

@app.get("/inventory")
def inventory():
    return NoCacheFileResponse(os.path.join(web_dir, "inventory.html"))

@app.get("/analytics")
def analytics():
    return NoCacheFileResponse(os.path.join(web_dir, "analytics.html"))

@app.get("/profile")
def profile_page():
    return NoCacheFileResponse(os.path.join(web_dir, "profile.html"))

# Register our API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(medicines.router, prefix="/api/medicines", tags=["Medicines"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
