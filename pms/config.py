"""
Configuration settings for the Pharmacy Management System.
"""
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "pharmacy.db"
BILLS_DIR = BASE_DIR / "bills"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"

# Shop details
SHOP_NAME = "CITY PHARMACY"
SHOP_ADDRESS = ""
CURRENCY_SYMBOL = ""

# Business rules
EXPIRY_WARNING_DAYS = 30
MAX_PHARMACIST_DISCOUNT_PCT = 10
PBKDF2_ITERATIONS = 600000
LOCKOUT_ATTEMPTS = 5
LOCKOUT_MINUTES = 5

# UI settings
PAGE_SIZE = 15
