"""
=============================================================================
Employee Repository
=============================================================================
Provides data access methods for the EMPLOYEE table with authentication.

All operations use stored procedures from stored_procedures.sql:
- usp_ListEmployees: List all employees
- usp_GetEmployeeById: Get employee by ID
- usp_GetEmployeeByUsername: Get employee by username (includes password_hash)
- usp_GetEmployeeWithPassword: Get employee with password for authentication
- usp_AddEmployee: Create new employee
- usp_UpdateEmployee: Update employee details
- usp_DeleteEmployee: Delete employee
- usp_GetNextEmployeeId: Generate next employee ID
- usp_ChangeEmployeePassword: Change employee password
- usp_CheckSalesExistForEmployee: Check if employee has sales records

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import db

# Password hashing with pbkdf2_sha256
from passlib.hash import pbkdf2_sha256


@dataclass
class Employee:
    """Data class representing an employee."""
    employee_id: str
    employee_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    salary: Optional[Decimal] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    role: str = 'Employee'
    
    @classmethod
    def from_row(cls, row) -> 'Employee':
        """Create an Employee instance from a database row."""
        return cls(
            employee_id=row.Employee_ID,
            employee_name=row.Employee_Name,
            phone=getattr(row, 'Phone', None),
            email=getattr(row, 'Email', None),
            position=getattr(row, 'Position', None),
            hire_date=getattr(row, 'Hire_Date', None),
            salary=Decimal(str(row.Salary)) if getattr(row, 'Salary', None) else None,
            username=getattr(row, 'Username', None),
            password_hash=getattr(row, 'password_hash', None),
            role=getattr(row, 'role', 'Employee')
        )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'phone': self.phone,
            'email': self.email,
            'position': self.position,
            'hire_date': str(self.hire_date) if self.hire_date else None,
            'salary': float(self.salary) if self.salary else None,
            'username': self.username,
            'role': self.role
        }
        if include_sensitive:
            result['password_hash'] = self.password_hash
        return result
    
    @property
    def is_admin(self) -> bool:
        """Check if employee has admin role."""
        return self.role == 'Admin'
    
    @property
    def phone_number(self) -> Optional[str]:
        """Alias for phone attribute."""
        return self.phone


class EmployeeRepository:
    """
    Repository class for EMPLOYEE table operations.
    ALL METHODS USE STORED PROCEDURES.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using pbkdf2_sha256."""
        return pbkdf2_sha256.hash(password)
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pbkdf2_sha256.verify(password, password_hash)
        except Exception:
            return False
    
    @staticmethod
    def authenticate(username: str, password: str) -> Tuple[bool, Optional[Employee], str]:
        """
        Authenticate an employee by username and password.
        Uses: usp_GetEmployeeWithPassword
        
        Returns:
            Tuple of (success: bool, employee: Employee or None, message: str)
        """
        # Get employee with password hash using stored procedure
        rows = db.call_procedure_with_result('usp_GetEmployeeWithPassword', (username,))
        
        if not rows:
            return False, None, "Invalid username or password"
        
        employee = Employee.from_row(rows[0])
        
        if not employee.password_hash:
            return False, None, "Account not set up for login"
        
        if EmployeeRepository.verify_password(password, employee.password_hash):
            return True, employee, "Login successful"
        else:
            return False, None, "Invalid username or password"
    
    @staticmethod
    def get_all() -> List[Employee]:
        """
        Retrieve all employees.
        Uses: usp_ListEmployees
        """
        rows = db.call_procedure_with_result('usp_ListEmployees')
        return [Employee.from_row(row) for row in rows]
    
    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        """
        Get all employees as list of dictionaries.
        Uses: usp_ListEmployees
        """
        employees = EmployeeRepository.get_all()
        return [
            {
                'employee_id': emp.employee_id,
                'employee_name': emp.employee_name,
                'username': emp.username,
                'role': emp.role,
                'email': emp.email or '',
                'phone': emp.phone or ''
            }
            for emp in employees
        ]
    
    @staticmethod
    def get_by_id(employee_id: str) -> Optional[Employee]:
        """
        Retrieve a single employee by ID.
        Uses: usp_GetEmployeeById
        """
        rows = db.call_procedure_with_result('usp_GetEmployeeById', (employee_id,))
        return Employee.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[Employee]:
        """
        Retrieve a single employee by username.
        Uses: usp_GetEmployeeByUsername
        """
        rows = db.call_procedure_with_result('usp_GetEmployeeByUsername', (username,))
        return Employee.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available employee ID.
        Uses: usp_GetNextEmployeeId
        """
        next_id = db.call_procedure_scalar('usp_GetNextEmployeeId', column_name='NextId')
        return next_id or 'EMP001'
    
    @staticmethod
    def generate_next_id() -> str:
        """Alias for get_next_id()."""
        return EmployeeRepository.get_next_id()
    
    @staticmethod
    def create(
        employee_id: str,
        employee_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        position: Optional[str] = None,
        hire_date: Optional[date] = None,
        salary: Optional[Decimal] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        role: str = 'Employee'
    ) -> Tuple[bool, str]:
        """
        Create a new employee.
        Uses: usp_AddEmployee
        """
        # Check if username is already taken
        if username:
            existing = EmployeeRepository.get_by_username(username)
            if existing:
                return False, "Username already exists"
        
        # Hash password if provided
        password_hash = None
        if password:
            password_hash = EmployeeRepository.hash_password(password)
        
        try:
            # usp_AddEmployee params: EmployeeId, EmployeeName, Phone, Email, 
            # Position, Salary, Username, PasswordHash, Role
            success = db.call_procedure('usp_AddEmployee', (
                employee_id,
                employee_name,
                phone,
                email,
                position or 'Staff',
                float(salary) if salary else None,
                username,
                password_hash,
                role
            ), has_output=False)
            
            if success:
                return True, "Employee created successfully"
            else:
                return False, "Failed to create employee"
        except Exception as e:
            return False, f"Failed to create employee: {str(e)}"
    
    @staticmethod
    def create_employee(
        employee_name: str,
        username: str,
        password: str,
        role: str = 'Employee',
        phone: Optional[str] = None,
        email: Optional[str] = None,
        position: Optional[str] = None,
        salary: Optional[Decimal] = None
    ) -> Tuple[bool, str]:
        """
        Create a new employee with auto-generated ID (admin operation).
        Uses: usp_GetNextEmployeeId, usp_AddEmployee
        """
        if not employee_name or not username or not password:
            return False, "Employee name, username, and password are required"
        
        # Check if username already exists
        existing = EmployeeRepository.get_by_username(username)
        if existing:
            return False, "Username already exists"
        
        # Generate new employee ID
        new_id = EmployeeRepository.get_next_id()
        
        return EmployeeRepository.create(
            employee_id=new_id,
            employee_name=employee_name,
            phone=phone,
            email=email,
            position=position,
            salary=salary,
            username=username,
            password=password,
            role=role
        )
    
    @staticmethod
    def create_from_signup(employee: 'Employee') -> Optional[str]:
        """
        Create employee from signup (auto-generates ID).
        Uses: usp_GetNextEmployeeId, usp_AddEmployee
        """
        new_id = EmployeeRepository.get_next_id()
        
        success, _ = EmployeeRepository.create(
            employee_id=new_id,
            employee_name=employee.employee_name,
            phone=employee.phone,
            email=employee.email,
            position=employee.position or 'Staff',
            username=employee.username,
            password=None,  # Password hash already in employee object
            role=employee.role
        )
        
        # If password_hash is already set, update it directly
        if success and employee.password_hash:
            db.call_procedure('usp_ChangeEmployeePassword', (new_id, employee.password_hash), has_output=False)
        
        return new_id if success else None
    
    @staticmethod
    def update(
        employee_id: str,
        employee_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        position: Optional[str] = None,
        salary: Optional[Decimal] = None,
        username: Optional[str] = None,
        role: str = 'Employee'
    ) -> Tuple[bool, str]:
        """
        Update an existing employee (does not change password).
        Uses: usp_UpdateEmployee
        """
        # Check if new username is taken by another employee
        if username:
            existing = EmployeeRepository.get_by_username(username)
            if existing and existing.employee_id != employee_id:
                return False, "Username already exists"
        
        try:
            # usp_UpdateEmployee params: EmployeeId, EmployeeName, Phone, Email, 
            # Position, Salary, Username, Role
            success = db.call_procedure('usp_UpdateEmployee', (
                employee_id,
                employee_name,
                phone,
                email,
                position,
                float(salary) if salary else None,
                username,
                role
            ), has_output=False)
            
            if success:
                return True, "Employee updated successfully"
            else:
                return False, "Employee not found"
        except Exception as e:
            return False, f"Failed to update employee: {str(e)}"
    
    @staticmethod
    def change_password(employee_id: str, new_password: str) -> Tuple[bool, str]:
        """
        Change an employee's password.
        Uses: usp_ChangeEmployeePassword
        """
        password_hash = EmployeeRepository.hash_password(new_password)
        
        try:
            success = db.call_procedure('usp_ChangeEmployeePassword', (employee_id, password_hash), has_output=False)
            if success:
                return True, "Password changed successfully"
            else:
                return False, "Employee not found"
        except Exception as e:
            return False, f"Failed to change password: {str(e)}"
    
    @staticmethod
    def reset_password(employee_id: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset an employee's password (admin function).
        Uses: usp_ChangeEmployeePassword
        """
        return EmployeeRepository.change_password(employee_id, new_password)
    
    @staticmethod
    def delete(employee_id: str) -> Tuple[bool, str]:
        """
        Delete an employee by ID.
        Uses: usp_CheckSalesExistForEmployee, usp_DeleteEmployee
        """
        # Check for existing sales
        rows = db.call_procedure_with_result('usp_CheckSalesExistForEmployee', (employee_id,))
        if rows and rows[0].SaleCount > 0:
            return False, f"Cannot delete: {rows[0].SaleCount} sales processed by this employee"
        
        try:
            success = db.call_procedure('usp_DeleteEmployee', (employee_id,), has_output=False)
            if success:
                return True, "Employee deleted successfully"
            else:
                return False, "Employee not found"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    @staticmethod
    def delete_employee(employee_id: str) -> Tuple[bool, str]:
        """Alias for delete()."""
        return EmployeeRepository.delete(employee_id)
    
    @staticmethod
    def get_for_dropdown() -> List[Dict[str, str]]:
        """
        Get employees for dropdown/combo box.
        Uses: usp_ListEmployees
        """
        employees = EmployeeRepository.get_all()
        return [{'id': emp.employee_id, 'name': emp.employee_name} for emp in employees]
    
    @staticmethod
    def setup_initial_admin(username: str, password: str) -> Tuple[bool, str]:
        """
        Set up the initial admin account password.
        Uses: usp_GetEmployeeByUsername, usp_ChangeEmployeePassword
        """
        employee = EmployeeRepository.get_by_username(username)
        if not employee:
            return False, f"Employee with username '{username}' not found"
        
        return EmployeeRepository.change_password(employee.employee_id, password)
