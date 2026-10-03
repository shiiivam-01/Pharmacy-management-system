from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
from typing import List
from backend.services.medicine_service import MedicineService
from backend.models import Session
from api.deps import get_db, get_current_actor
from api.schemas import MedicineSchema

router = APIRouter()

@router.get("/search", response_model=List[MedicineSchema])
def search_medicines(
    query: str = Query("", description="Search by name or category"),
    include_inactive: bool = Query(False),
    conn: sqlite3.Connection = Depends(get_db),
    actor: Session = Depends(get_current_actor)
):
    med_service = MedicineService(conn)
    try:
        meds = med_service.search_medicines(actor, query, include_inactive)
        
        # Convert raw dicts to Pydantic models
        results = []
        for m in meds:
            results.append(MedicineSchema(
                id=m["id"],
                name=m["name"],
                generic_name=m["generic_name"],
                form=m["form"],
                strength=m["strength"],
                category=m["category"],
                manufacturer=m["manufacturer"],
                unit_price_minor=m["unit_price_minor"],
                tax_percent=m["tax_percent"],
                reorder_level=m["reorder_level"],
                requires_prescription=bool(m["requires_prescription"]),
                is_active=bool(m["is_active"])
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
