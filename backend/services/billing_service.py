"""
Billing service.
"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import date
from backend.models import Session, CartLine, Sale
from backend.repositories.medicine_repository import MedicineRepository
from backend.repositories.batch_repository import BatchRepository
from backend.repositories.sale_repository import SaleRepository
from backend.services.medicine_service import MedicineService
from backend.services.fefo import allocate_fefo
from backend.exceptions import ValidationError, InsufficientStockError
from backend.security import require
from backend.money import round_half_up

class BillingService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.sale_repo = SaleRepository(conn)
        self.med_repo = MedicineRepository(conn)
        self.batch_repo = BatchRepository(conn)
        self.med_service = MedicineService(conn)

    def _write_audit(self, actor: Session, action: str, entity_id: int, details: str = None):
        self.conn.execute(
            "INSERT INTO audit_log (employee_id, action, entity, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (actor.employee_id, action, "Sale", entity_id, details)
        )

    def add_to_cart(self, actor: Session, cart: List[CartLine], medicine_id: int, quantity: int, today: date = None) -> List[CartLine]:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
            
        med = self.med_service.get_medicine(actor, medicine_id, today)
        if not med.is_active:
            raise ValidationError("Cannot sell inactive medicine.")
            
        existing_qty = sum(item.quantity for item in cart if item.medicine_id == medicine_id)
        total_qty = existing_qty + quantity
        if total_qty > med.available_stock:
            raise InsufficientStockError(
                f"Insufficient stock. Available: {med.available_stock}",
                available=med.available_stock
            )
            
        for item in cart:
            if item.medicine_id == medicine_id:
                item.quantity += quantity
                return cart
                
        cart.append(CartLine(
            medicine_id=med.id,
            medicine_name=f"{med.name} {med.form} {med.strength}".strip(),
            quantity=quantity,
            unit_price_minor=med.unit_price_minor,
            tax_percent=med.tax_percent,
            requires_prescription=bool(med.requires_prescription)
        ))
        
        return cart

    def calculate_totals(self, cart: List[CartLine], discount_percent: float = 0.0) -> Dict[str, int]:
        if discount_percent < 0 or discount_percent > 100:
            raise ValidationError("Discount percent must be between 0 and 100.")
            
        subtotal = 0
        discount_total = 0
        tax_total = 0
        
        from decimal import Decimal, ROUND_HALF_UP
        dp = Decimal(str(discount_percent)) / Decimal('100')
        
        for item in cart:
            line_base = item.quantity * item.unit_price_minor
            
            disc_dec = (Decimal(line_base) * dp).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            discount = int(disc_dec)
            
            tax_p = Decimal(str(item.tax_percent)) / Decimal('100')
            tax_dec = (Decimal(line_base - discount) * tax_p).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            tax = int(tax_dec)
            
            subtotal += line_base
            discount_total += discount
            tax_total += tax
            
        total = subtotal - discount_total + tax_total
        return {
            "subtotal": subtotal,
            "discount": discount_total,
            "tax": tax_total,
            "total": total
        }

    def _generate_bill_no(self, today: date) -> str:
        today_str = today.isoformat()
        count = self.sale_repo.count_sales_today(today_str)
        return f"PMS-{today.strftime('%Y%m%d')}-{count + 1:04d}"

    def create_sale(self, actor: Session, cart: List[CartLine], customer_name: Optional[str] = None,
                    prescription_note: Optional[str] = None, discount_percent: float = 0.0,
                    payment_method: str = "CASH", today: date = None) -> Sale:
        require(actor, "medicine.view") # Creating a sale requires viewing medicines implicitly
        
        if not cart:
            raise ValidationError("Cart is empty.")
            
        if today is None:
            today = date.today()
            
        from backend.config import MAX_PHARMACIST_DISCOUNT_PCT
        if actor.role == "PHARMACIST" and discount_percent > MAX_PHARMACIST_DISCOUNT_PCT:
            raise ValidationError(f"Pharmacist discount cannot exceed {MAX_PHARMACIST_DISCOUNT_PCT}%.")
            
        # Re-check stock and allocate FEFO per line
        allocations = []
        for item in cart:
            batches = self.batch_repo.list_by_medicine(item.medicine_id, active_only=True, today_str=today.isoformat())
            try:
                line_allocations = allocate_fefo(batches, item.quantity, today)
                allocations.append((item, line_allocations))
            except InsufficientStockError as e:
                raise InsufficientStockError(f"Insufficient stock for {item.medicine_name}. {str(e)}", available=e.available)

        totals = self.calculate_totals(cart, discount_percent)
        
        bill_no = self._generate_bill_no(today)
        
        sale_id = self.sale_repo.add_sale(
            bill_no=bill_no,
            employee_id=actor.employee_id,
            customer_name=customer_name,
            prescription_note=prescription_note,
            subtotal_minor=totals["subtotal"],
            discount_percent=discount_percent,
            discount_minor=totals["discount"],
            tax_minor=totals["tax"],
            total_minor=totals["total"],
            payment_method=payment_method
        )
        
        for item, line_allocations in allocations:
            for batch, qty_taken in line_allocations:
                batch_line_total = qty_taken * item.unit_price_minor
                self.sale_repo.add_sale_item(
                    sale_id=sale_id,
                    medicine_id=item.medicine_id,
                    batch_id=batch.id,
                    quantity=qty_taken,
                    unit_price_minor=item.unit_price_minor,
                    tax_percent=item.tax_percent,
                    line_total_minor=batch_line_total
                )
                
                self.batch_repo.update_quantity(batch.id, batch.quantity - qty_taken)
                
        self._write_audit(actor, "CREATE_SALE", sale_id, f"Bill No: {bill_no}, Total: {totals['total']}")
        
        return self.sale_repo.get_sale_by_bill_no(bill_no)

    def void_sale(self, actor: Session, bill_no: str, reason: str):
        require(actor, "inventory.adjust") # Admin only
        
        sale = self.sale_repo.get_sale_by_bill_no(bill_no)
        if not sale:
            raise ValidationError(f"Bill '{bill_no}' not found.")
        if sale.status != "COMPLETED":
            raise ValidationError(f"Bill '{bill_no}' is already {sale.status}.")
            
        if not reason.strip():
            raise ValidationError("Reason is required.")
            
        items = self.sale_repo.get_sale_items(sale.id)
        for item in items:
            batch = self.batch_repo.get(item.batch_id)
            if batch:
                self.batch_repo.update_quantity(batch.id, batch.quantity + item.quantity)
                self.conn.execute(
                    "INSERT INTO stock_adjustments (batch_id, employee_id, delta, reason, note) VALUES (?, ?, ?, ?, ?)",
                    (batch.id, actor.employee_id, item.quantity, "SALE_VOID", f"Voiding bill {bill_no}")
                )
                
        self.sale_repo.set_sale_status(sale.id, "VOIDED", reason, actor.employee_id)
        self._write_audit(actor, "VOID_SALE", sale.id, f"Bill No: {bill_no}, Reason: {reason}")

    def get_sales_history(self, actor: Session, date_filter: Optional[str] = None) -> List[Sale]:
        require(actor, "medicine.view")
        employee_id = None if actor.role == "ADMIN" else actor.employee_id
        return self.sale_repo.list_sales(employee_id=employee_id, date_str=date_filter)

    def get_sale_details(self, actor: Session, bill_no: str) -> Tuple[Sale, List[SaleItem]]:
        require(actor, "medicine.view")
        sale = self.sale_repo.get_sale_by_bill_no(bill_no)
        if not sale:
            raise ValidationError(f"Bill '{bill_no}' not found.")
            
        if actor.role != "ADMIN" and sale.employee_id != actor.employee_id:
            raise ValidationError(f"You do not have permission to view bill '{bill_no}'.")
            
        items = self.sale_repo.get_sale_items(sale.id)
        return sale, items
