# Pharmacy Management System - Test Cases

| ID | Scenario | Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-01 | **Login:** Valid Admin login | Username: admin, Password: password123 | Grants access, opens main menu with Admin options | As expected | Pass |
| TC-02 | **Login:** Invalid credentials | Username: admin, Password: wrong | Shows "Invalid username or password" | As expected | Pass |
| TC-03 | **Login:** Inactive user | Username: old_user (inactive), Password: password123 | Shows "Invalid username or password" | As expected | Pass |
| TC-04 | **Login:** Lockout | Fail login 5 times | Account locks for 5 minutes, error on 6th attempt | As expected | Pass |
| TC-05 | **Suppliers:** Add duplicate | Name: existing supplier name | Rejects with ValidationError | As expected | Pass |
| TC-06 | **Medicines:** Add medicine | Valid details for Paracetamol | Medicine added, appears in list | As expected | Pass |
| TC-07 | **Medicines:** Search | Query: "para" | Returns Paracetamol in results | As expected | Pass |
| TC-08 | **Inventory:** Receive stock | Med ID: 1, Qty: 100, Expiry: Future | Batch created, available stock increases by 100 | As expected | Pass |
| TC-09 | **Inventory:** Expired stock | Med ID: 1, Qty: 50, Expiry: Past | Rejected with "Expiry date must be in the future" | As expected | Pass |
| TC-10 | **Billing:** FEFO Allocation | Cart has 10 units of Med 1 (Batches expire 2026 and 2027) | Takes from 2026 batch first | As expected | Pass |
| TC-11 | **Billing:** Insufficient Stock | Order 1000 units, only 100 available | Rejected, available quantity shown | As expected | Pass |
| TC-12 | **Billing:** Pharmacist cap | Pharmacist applies 15% discount | Rejected (cap is 10%) | As expected | Pass |
| TC-13 | **Billing:** Admin discount | Admin applies 15% discount | Allowed, total correctly updated | As expected | Pass |
| TC-14 | **Billing:** Prescription check | Cart contains Rx medicine | Prompts "Has a valid prescription been verified?" | As expected | Pass |
| TC-15 | **Billing:** Rollback on error | DB fails during sale creation | Cart discarded, no stock deducted, no sale recorded | As expected | Pass |
| TC-16 | **Alerts:** Low Stock | Stock falls below reorder level | Dashboard shows 1 low stock item | As expected | Pass |
| TC-17 | **Reports:** Daily Sales | Date: Today | Sums total revenue by payment method | As expected | Pass |
| TC-18 | **Reports:** Visibility | Pharmacist views Daily Sales | Sees only their own sales | As expected | Pass |
| TC-19 | **Hardening:** Void Sale | Admin voids sale | Sale status VOIDED, stock restored | As expected | Pass |
| TC-20 | **Hardening:** Void Twice | Admin voids already voided sale | Rejected | As expected | Pass |
| TC-21 | **Hardening:** Audit Log | Admin views logs | All system actions (login, add, sell) are listed | As expected | Pass |
