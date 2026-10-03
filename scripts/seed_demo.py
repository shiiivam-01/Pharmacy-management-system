"""
Script to seed the database with realistic demo data.
(2 admins, 3 pharmacists, 50 medicines, 10 suppliers, 200 past sales)
"""
import os
import sys
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import connect, init_schema, transaction
from backend.models import Session
from backend.security import hash_password
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.supplier_repository import SupplierRepository
from backend.services.medicine_service import MedicineService
from backend.services.inventory_service import InventoryService
from backend.services.billing_service import BillingService

def main():
    print("Seeding demo data...")
    conn = connect()
    init_schema(conn)
    
    emp_repo = EmployeeRepository(conn)
    sup_repo = SupplierRepository(conn)
    med_service = MedicineService(conn)
    inv_service = InventoryService(conn)
    billing = BillingService(conn)
    
    with transaction(conn):
        # 1. Employees
        pw_hash = hash_password("password123")
        if not emp_repo.get_by_username("admin"):
            emp_repo.add("System Admin", "1234567890", "ADMIN", "admin", pw_hash)
        
        admin_id = emp_repo.get_by_username("admin").id
        actor = Session(employee_id=admin_id, username="admin", role="ADMIN", full_name="System Admin")
        
        # Add 1 more admin
        if not emp_repo.get_by_username("admin2"):
            emp_repo.add("Secondary Admin", "0987654321", "ADMIN", "admin2", pw_hash)
            
        # Add 3 pharmacists
        pharm_ids = []
        for i in range(1, 4):
            uname = f"pharm{i}"
            if not emp_repo.get_by_username(uname):
                emp_repo.add(f"Pharmacist {i}", f"111111111{i}", "PHARMACIST", uname, pw_hash)
            pharm_ids.append(emp_repo.get_by_username(uname).id)

        # 2. Suppliers
        suppliers = []
        for i in range(1, 11):
            sup_name = f"Supplier Co {i}"
            sup_repo.add(sup_name, f"Contact {i}", f"555-000{i}", f"supplier{i}@example.com", f"Address {i}")
        
        sup_records = sup_repo.list_all()
        
        # 3. Medicines
        medicines = []
        forms = ["Tablet", "Capsule", "Syrup", "Injection", "Ointment", "Drops"]
        categories = ["Pain Relief", "Antibiotic", "Vitamins", "Cardiovascular", "Dermatology", "Respiratory"]
        
        for i in range(1, 51):
            med = med_service.add_medicine(
                actor=actor,
                name=f"Medicine {i}",
                form=random.choice(forms),
                strength=f"{random.randint(1, 500)}mg",
                unit_price=Decimal(f"{random.randint(5, 50)}.{random.choice(['00', '50', '99'])}"),
                tax_percent=random.choice([0.0, 5.0, 12.0, 18.0]),
                reorder_level=random.randint(20, 100),
                requires_prescription=random.choice([True, False, False]),
                category=random.choice(categories),
                supplier_id=random.choice(sup_records).id
            )
            medicines.append(med)
            
            # Receive stock for each medicine
            inv_service.receive_stock(
                actor=actor,
                medicine_id=med.id,
                batch_no=f"BATCH-{i}-1",
                quantity=random.randint(100, 500),
                purchase_price=Decimal(f"{random.randint(2, 40)}.00"),
                expiry_date=(date.today() + timedelta(days=random.randint(30, 700))).isoformat(),
                today=date.today()
            )

        # 4. Sales
        # Create 200 sales over the last 30 days
        print("Generating 200 past sales...")
        for i in range(200):
            sale_date = date.today() - timedelta(days=random.randint(0, 30))
            
            # Pick a random employee (admin or pharm)
            seller_id = random.choice([admin_id] + pharm_ids)
            seller = emp_repo.get(seller_id)
            seller_session = Session(employee_id=seller.id, username=seller.username, role=seller.role, full_name=seller.full_name)
            
            # Create a cart with 1-5 random items
            cart = []
            num_items = random.randint(1, 5)
            for _ in range(num_items):
                med = random.choice(medicines)
                qty = random.randint(1, 5)
                try:
                    cart = billing.add_to_cart(seller_session, cart, med.id, qty, today=sale_date)
                except Exception:
                    pass # Ignore insufficient stock for demo data
                    
            if cart:
                try:
                    pmt = random.choice(["CASH", "CARD", "UPI"])
                    discount = 0.0
                    if random.random() < 0.2: # 20% chance of discount
                        discount = 5.0 if seller.role == "PHARMACIST" else 15.0
                        
                    billing.create_sale(
                        actor=seller_session,
                        cart=cart,
                        customer_name=f"Customer {i}",
                        prescription_note="Demo Rx" if any(c.requires_prescription for c in cart) else None,
                        discount_percent=discount,
                        payment_method=pmt,
                        today=sale_date
                    )
                except Exception as e:
                    pass # Ignore errors like stock out or discount limits
                    
    print("Demo data seeded successfully!")

if __name__ == "__main__":
    main()
