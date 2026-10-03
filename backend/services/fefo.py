"""
FEFO (First Expired First Out) stock allocation algorithm.
"""
from typing import List, Tuple
from datetime import date
from backend.models import Batch
from backend.exceptions import InsufficientStockError

def allocate_fefo(batches: List[Batch], quantity_needed: int, today: date = None) -> List[Tuple[Batch, int]]:
    """
    Allocates stock using FEFO.
    Returns a list of (Batch, quantity_taken) tuples.
    Raises InsufficientStockError if total available < quantity_needed.
    """
    if today is None:
        today = date.today()
        
    if quantity_needed <= 0:
        return []

    # Filter out expired and zero-quantity batches
    available = []
    total_avail = 0
    for b in batches:
        b_exp = date.fromisoformat(b.expiry_date)
        if b.quantity > 0 and b_exp >= today:
            available.append(b)
            total_avail += b.quantity
            
    if total_avail < quantity_needed:
        raise InsufficientStockError(
            f"Not enough stock. Needed {quantity_needed}, but only {total_avail} available.",
            available=total_avail
        )
        
    # Sort by expiry_date ASC, then id ASC (tie breaker)
    available.sort(key=lambda b: (b.expiry_date, b.id))
    
    allocation = []
    remaining = quantity_needed
    
    for b in available:
        if remaining <= 0:
            break
            
        take = min(b.quantity, remaining)
        allocation.append((b, take))
        remaining -= take
        
    return allocation
