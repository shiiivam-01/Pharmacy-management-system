"""
Console UI helpers for the Pharmacy Management System.
"""
from datetime import date
from decimal import Decimal
from typing import List, Any
import pms.validators as validators
from pms.exceptions import ValidationError

def ask_text(prompt: str, required: bool = True) -> str:
    while True:
        value = input(f"{prompt}: ").strip()
        if not value and required:
            print("This field is required.")
            continue
        return value

def ask_int(prompt: str, required: bool = True, allow_zero: bool = False) -> int | None:
    while True:
        value = input(f"{prompt}: ").strip()
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
        try:
            return validators.validate_positive_int(value, "Value", allow_zero=allow_zero)
        except ValidationError as e:
            print(str(e))

def ask_decimal(prompt: str, required: bool = True) -> Decimal | None:
    while True:
        value = input(f"{prompt}: ").strip()
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
        try:
            dec = Decimal(value)
            if dec < 0:
                print("Value cannot be negative.")
                continue
            return dec
        except Exception:
            print("Must be a valid number.")

def ask_date(prompt: str, required: bool = True) -> date | None:
    while True:
        value = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if not value:
            if required:
                print("This field is required.")
                continue
            return None
        try:
            return validators.validate_date(value, "Date")
        except ValidationError as e:
            print(str(e))

def ask_choice(prompt: str, choices: List[str]) -> str:
    options = "/".join(choices)
    while True:
        value = input(f"{prompt} [{options}]: ").strip().upper()
        if value in choices:
            return value
        print(f"Please enter one of {options}.")

def confirm(prompt: str) -> bool:
    while True:
        value = input(f"{prompt} [Y/N]: ").strip().upper()
        if value in ('Y', 'YES'):
            return True
        if value in ('N', 'NO'):
            return False

def print_table(headers: List[str], rows: List[List[Any]]):
    """Prints a simple aligned table with pagination."""
    if not headers and not rows:
        return
        
    from pms.config import PAGE_SIZE
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
                
    def print_page(page_rows):
        header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, widths))
        print(header_line)
        print("-" * len(header_line))
        for row in page_rows:
            print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))

    total_rows = len(rows)
    if total_rows <= PAGE_SIZE:
        print_page(rows)
        return
        
    current_page = 0
    total_pages = (total_rows + PAGE_SIZE - 1) // PAGE_SIZE
    
    while True:
        start_idx = current_page * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_rows)
        page_rows = rows[start_idx:end_idx]
        
        print_page(page_rows)
        print(f"\nPage {current_page + 1} of {total_pages} ({total_rows} total rows)")
        
        options = []
        if current_page > 0:
            options.append("P = Previous")
        if current_page < total_pages - 1:
            options.append("N = Next")
        options.append("Q = Quit")
        
        prompt = " / ".join(options) + " : "
        choice = input(prompt).strip().upper()
        
        if choice == 'Q':
            break
        elif choice == 'P' and current_page > 0:
            current_page -= 1
        elif choice == 'N' and current_page < total_pages - 1:
            current_page += 1
