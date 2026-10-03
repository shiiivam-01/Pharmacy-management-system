import pytest
from pms.services.employee_service import EmployeeService
from pms.exceptions import ValidationError, AuthorizationError

def test_employee_service_add_list_update(db, admin, pharmacist):
    service = EmployeeService(db)
    
    # Pharmacist cannot manage employees
    with pytest.raises(AuthorizationError):
        service.add_employee(pharmacist, "Test", "123", "PHARMACIST", "test1", "password123")
        
    # Admin can add employee
    emp1 = service.add_employee(admin, "User One", "111", "PHARMACIST", "u1", "password123")
    assert emp1.id is not None
    assert emp1.username == "u1"
    
    # Cannot add existing username
    with pytest.raises(ValidationError, match="already taken"):
        service.add_employee(admin, "User Two", "222", "ADMIN", "u1", "password123")
        
    # List employees
    emps = service.list_employees(admin)
    assert len(emps) >= 2 # Includes admin + emp1
    
    # Update employee
    emp1_updated = service.update_employee(admin, emp1.id, "User One Updated", "999", "ADMIN")
    assert emp1_updated.full_name == "User One Updated"
    assert emp1_updated.phone == "999"
    assert emp1_updated.role == "ADMIN"

def test_deactivate_and_last_admin(db, admin):
    service = EmployeeService(db)
    
    # Add a second admin
    admin2 = service.add_employee(admin, "Admin Two", "123", "ADMIN", "admin2", "password123")
    
    # Cannot deactivate self
    with pytest.raises(ValidationError, match="cannot deactivate yourself"):
        service.deactivate_employee(admin, admin.employee_id)
        
    # Admin1 deactivates Admin2
    service.deactivate_employee(admin, admin2.id)
    admin2_reloaded = service.repo.get(admin2.id)
    assert admin2_reloaded.is_active == 0
    
    # Now admin is the last active admin
    with pytest.raises(ValidationError, match="Cannot change the role of the last active Admin"):
        service.update_employee(admin, admin.employee_id, "Admin Name", "123", "PHARMACIST")
        
def test_reset_password(db, admin):
    service = EmployeeService(db)
    
    emp = service.add_employee(admin, "User Pw", "123", "PHARMACIST", "user_pw", "password123")
    
    service.reset_password(admin, emp.id, "new_password")
    
    emp_reloaded = service.repo.get(emp.id)
    assert emp_reloaded.password_hash != "password123"
    assert "pbkdf2_sha256$" in emp_reloaded.password_hash
