"""
=============================================================================
Customer Repository
=============================================================================
Provides data access methods for the CUSTOMER table.

Customers are people who purchase products from our store. A special
"Walk-in Customer" (ID: C000) is used for anonymous/cash sales.

Table Schema:
    CUSTOMER(Customer_ID, Customer_Name, Phone, Email, Address, City, Date_Registered)

Changes Applied:
- MIGRATED TO STORED PROCEDURES for CRUD operations
- Uses usp_AddCustomer, usp_UpdateCustomer, usp_DeleteCustomer
- Uses usp_GetCustomerById, usp_ListCustomers, usp_GetNextCustomerId
- Maintains backward-compatible interface for existing UI code

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date
import db


@dataclass
class Customer:
    """
    Data class representing a customer.
    
    Attributes:
        customer_id: Unique customer identifier
        customer_name: Full name
        phone: Contact phone number
        email: Email address
        address: Street address
        city: City location
        registration_date: Date when customer registered
        total_purchases: Number of purchases (from stored procedure)
        total_spent: Total amount spent (from stored procedure)
    """
    customer_id: str
    customer_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    registration_date: Optional[date] = None
    total_purchases: int = 0
    total_spent: float = 0.0
    
    @classmethod
    def from_row(cls, row) -> 'Customer':
        """Create a Customer instance from a database row."""
        return cls(
            customer_id=row.Customer_ID,
            customer_name=row.Customer_Name,
            phone=getattr(row, 'Phone', None),
            email=getattr(row, 'Email', None),
            address=getattr(row, 'Address', None),
            city=getattr(row, 'City', None),
            registration_date=getattr(row, 'Date_Registered', None) or getattr(row, 'Registration_Date', None),
            total_purchases=getattr(row, 'Total_Purchases', 0) or 0,
            total_spent=float(getattr(row, 'Total_Spent', 0) or 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'registration_date': str(self.registration_date) if self.registration_date else None,
            'total_purchases': self.total_purchases,
            'total_spent': self.total_spent
        }
    
    @property
    def is_walkin(self) -> bool:
        """Check if this is the walk-in customer."""
        return self.customer_id == 'C000'
    
    @property
    def phone_number(self) -> Optional[str]:
        """Alias for phone - UI compatibility."""
        return self.phone


class CustomerRepository:
    """
    Repository class for CUSTOMER table operations.
    NOW USES STORED PROCEDURES for all database operations.
    """
    
    # Walk-in customer ID constant
    WALKIN_CUSTOMER_ID = 'C000'
    
    @staticmethod
    def get_all(include_walkin: bool = True) -> List[Customer]:
        """
        Retrieve all customers.
        Uses: usp_ListCustomers
        
        Args:
            include_walkin: If True, includes the walk-in customer in results
        
        Returns:
            List of Customer objects ordered by Customer_Name
        """
        rows = db.call_procedure_with_result('usp_ListCustomers')
        customers = [Customer.from_row(row) for row in rows]
        
        if not include_walkin:
            customers = [c for c in customers if c.customer_id != 'C000']
        
        return customers
    
    @staticmethod
    def get_by_id(customer_id: str) -> Optional[Customer]:
        """
        Retrieve a single customer by ID.
        Uses: usp_GetCustomerById
        
        Args:
            customer_id: Customer ID to look up
        
        Returns:
            Customer object if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetCustomerById', {'Customer_ID': customer_id})
        return Customer.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_phone(phone: str) -> Optional[Customer]:
        """
        Retrieve a customer by phone number.
        Uses: usp_ListCustomers (filters in Python)
        
        Args:
            phone: Phone number to search for
        
        Returns:
            Customer object if found, None otherwise
        """
        if not phone:
            return None
        
        # Clean phone number - remove spaces, dashes
        clean_phone = phone.replace(' ', '').replace('-', '').strip()
        
        rows = db.call_procedure_with_result('usp_ListCustomers')
        for row in rows:
            if row.Customer_ID == 'C000':
                continue
            row_phone = (row.Phone or '').replace(' ', '').replace('-', '').strip()
            if row_phone and row_phone == clean_phone:
                return Customer.from_row(row)
        return None
    
    @staticmethod
    def get_walkin_customer() -> Optional[Customer]:
        """
        Retrieve the walk-in customer record.
        
        Returns:
            Walk-in Customer object (ID: C000)
        """
        return CustomerRepository.get_by_id(CustomerRepository.WALKIN_CUSTOMER_ID)
    
    @staticmethod
    def search(search_term: str) -> List[Customer]:
        """
        Search customers by name, phone, email, or city.
        Uses: usp_ListCustomers (filters in Python)
        
        Args:
            search_term: Text to search for
        
        Returns:
            List of matching Customer objects (excludes walk-in)
        """
        rows = db.call_procedure_with_result('usp_ListCustomers')
        search_lower = search_term.lower() if search_term else ''
        results = []
        for row in rows:
            if row.Customer_ID == 'C000':
                continue
            # Search in name, phone, email, city
            if (search_lower in (row.Customer_Name or '').lower() or
                search_lower in (row.Phone or '').lower() or
                search_lower in (row.Email or '').lower() or
                search_lower in (row.City or '').lower()):
                results.append(Customer.from_row(row))
        return results
    
    @staticmethod
    def create(
        customer_id: str,
        customer_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        registration_date: Optional[date] = None
    ) -> bool:
        """
        Create a new customer.
        Uses: usp_AddCustomer
        
        Args:
            customer_id: Unique customer identifier
            customer_name: Full name
            phone: Phone number
            email: Email address
            address: Street address
            city: City
            registration_date: Ignored (procedure uses GETDATE())
        
        Returns:
            True if created successfully
        """
        # Note: usp_AddCustomer uses CustomerId, CustomerName (no underscore)
        # and does not have OUTPUT parameters
        try:
            result = db.call_procedure('usp_AddCustomer', {
                'CustomerId': customer_id,
                'CustomerName': customer_name,
                'Phone': phone,
                'Email': email,
                'Address': address,
                'City': city
            }, has_output=False)
            return result
        except Exception as e:
            print(f"[ERROR] create customer: {e}")
            return False
    
    @staticmethod
    def update(
        customer_id: str,
        customer_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Update an existing customer.
        Uses: usp_UpdateCustomer
        
        Args:
            customer_id: Customer ID to update
            customer_name: New name
            phone: New phone
            email: New email
            address: New address
            city: New city
        
        Returns:
            True if updated successfully
        """
        # Prevent modifying walk-in customer
        if customer_id == CustomerRepository.WALKIN_CUSTOMER_ID:
            return False
        
        # Note: usp_UpdateCustomer uses CustomerId, CustomerName (no underscore)
        try:
            result = db.call_procedure('usp_UpdateCustomer', {
                'CustomerId': customer_id,
                'CustomerName': customer_name,
                'Phone': phone,
                'Email': email,
                'Address': address,
                'City': city
            }, has_output=False)
            return result
        except Exception as e:
            print(f"[ERROR] update customer: {e}")
            return False
    
    @staticmethod
    def delete(customer_id: str) -> Tuple[bool, str]:
        """
        Delete a customer by ID.
        Uses: usp_DeleteCustomer
        
        Note: Cannot delete walk-in customer or customers with sales history.
        
        Args:
            customer_id: Customer ID to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Prevent deleting walk-in customer
        if customer_id == CustomerRepository.WALKIN_CUSTOMER_ID:
            return False, "Cannot delete the walk-in customer"
        
        # Note: usp_DeleteCustomer uses CustomerId (no underscore)
        try:
            result = db.call_procedure('usp_DeleteCustomer', {'CustomerId': customer_id}, has_output=False)
            if result:
                return True, "Customer deleted successfully"
            else:
                return False, "Delete failed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available customer ID.
        Uses: usp_GetNextCustomerId
        
        Returns:
            Next ID in format 'CUS###' (e.g., 'CUS001')
        """
        next_id = db.call_procedure_scalar('usp_GetNextCustomerId', column_name='NextId')
        return next_id or 'CUS001'
    
    @staticmethod
    def get_for_dropdown(include_walkin: bool = True) -> List[Dict[str, str]]:
        """
        Get customers for dropdown/combo box.
        Uses: usp_ListCustomers
        
        Args:
            include_walkin: If True, includes walk-in customer at top
        
        Returns:
            List of dicts with 'id' and 'name' keys
        """
        result = []
        
        if include_walkin:
            result.append({'id': 'C000', 'name': 'Walk-in Customer'})
        
        rows = db.call_procedure_with_result('usp_ListCustomers')
        
        for row in rows:
            if row.Customer_ID != 'C000':
                result.append({'id': row.Customer_ID, 'name': row.Customer_Name})
        
        return result
    
    @staticmethod
    def get_purchase_history(customer_id: str) -> List[Dict[str, Any]]:
        """
        Get purchase history for a customer.
        Uses: usp_GetCustomerPurchaseHistory
        
        Args:
            customer_id: Customer ID
        
        Returns:
            List of sale records with basic info
        """
        rows = db.call_procedure_with_result('usp_GetCustomerPurchaseHistory', (customer_id,))
        return [
            {
                'invoice_no': row.Invoice_No,
                'sale_date': row.Sale_Date,
                'total_amount': float(row.Total_Amount),
                'net_amount': float(row.Net_Amount),
                'employee_name': row.Employee_Name
            }
            for row in rows
        ]
    
    @staticmethod
    def create_customer(
        customer_name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new customer with auto-generated ID.
        Uses: usp_GetNextCustomerId, usp_AddCustomer
        
        Args:
            customer_name: Full name (required)
            phone: Phone number
            email: Email address
            address: Street address
            city: City
        
        Returns:
            Tuple of (success: bool, message: str, new_customer_id: Optional[str])
        """
        if not customer_name or not customer_name.strip():
            return False, "Customer name is required", None
        
        # Generate next ID using stored procedure
        customer_id = CustomerRepository.get_next_id()
        
        # Note: usp_AddCustomer uses CustomerId, CustomerName (no underscore)
        # and does not have OUTPUT parameters
        try:
            result = db.call_procedure('usp_AddCustomer', {
                'CustomerId': customer_id,
                'CustomerName': customer_name.strip(),
                'Phone': phone,
                'Email': email,
                'Address': address,
                'City': city
            }, has_output=False)
            
            if result:
                return True, f"Customer '{customer_name}' created successfully", customer_id
            else:
                return False, "Failed to create customer", None
        except Exception as e:
            return False, str(e), None
