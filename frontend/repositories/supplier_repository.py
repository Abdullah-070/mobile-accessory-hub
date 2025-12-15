"""
=============================================================================
Supplier Repository
=============================================================================
Provides data access methods for the SUPPLIER table.

Suppliers are vendors from whom we purchase products for the store.

Table Schema:
    SUPPLIER(Supplier_ID, Supplier_Name, Contact_Person, Phone, Email, Address, City)

Changes Applied:
- MIGRATED TO STORED PROCEDURES for all CRUD operations
- Uses usp_AddSupplier, usp_UpdateSupplier, usp_DeleteSupplier
- Uses usp_GetSupplierById, usp_ListSuppliers, usp_GetNextSupplierId
- Maintains backward-compatible interface for existing UI code

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import db


@dataclass
class Supplier:
    """
    Data class representing a supplier/vendor.
    
    Attributes:
        supplier_id: Unique supplier identifier
        supplier_name: Company name
        contact_person: Name of main contact
        phone: Contact phone number
        email: Contact email address
        address: Street address
        city: City location
    """
    supplier_id: str
    supplier_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    total_purchases: int = 0
    total_purchase_value: float = 0.0
    
    @classmethod
    def from_row(cls, row) -> 'Supplier':
        """Create a Supplier instance from a database row."""
        return cls(
            supplier_id=row.Supplier_ID,
            supplier_name=row.Supplier_Name,
            contact_person=getattr(row, 'Contact_Person', None),
            phone=getattr(row, 'Phone', None),
            email=getattr(row, 'Email', None),
            address=getattr(row, 'Address', None),
            city=getattr(row, 'City', None),
            total_purchases=getattr(row, 'Total_Purchases', 0) or 0,
            total_purchase_value=float(getattr(row, 'Total_Purchase_Value', 0) or 0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'total_purchases': self.total_purchases,
            'total_purchase_value': self.total_purchase_value
        }
    
    @property
    def contact_name(self) -> Optional[str]:
        """Alias for contact_person - UI compatibility."""
        return self.contact_person
    
    @property
    def phone_number(self) -> Optional[str]:
        """Alias for phone - UI compatibility."""
        return self.phone


class SupplierRepository:
    """
    Repository class for SUPPLIER table operations.
    NOW USES STORED PROCEDURES for all database operations.
    """
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available supplier ID.
        Uses: usp_GetNextSupplierId
        
        Returns:
            Next ID in format 'SUP###' (e.g., 'SUP001')
        """
        next_id = db.call_procedure_scalar('usp_GetNextSupplierId', column_name='NextId')
        return next_id or 'SUP001'
    
    @staticmethod
    def get_all() -> List[Supplier]:
        """
        Retrieve all suppliers.
        Uses: usp_ListSuppliers
        
        Returns:
            List of Supplier objects ordered by Supplier_Name
        """
        rows = db.call_procedure_with_result('usp_ListSuppliers')
        return [Supplier.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(supplier_id: str) -> Optional[Supplier]:
        """
        Retrieve a single supplier by ID.
        Uses: usp_GetSupplierById
        
        Args:
            supplier_id: Supplier ID to look up
        
        Returns:
            Supplier object if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetSupplierById', {'Supplier_ID': supplier_id})
        return Supplier.from_row(rows[0]) if rows else None
    
    @staticmethod
    def search(search_term: str) -> List[Supplier]:
        """
        Search suppliers by name, contact person, or city.
        Note: Uses direct SQL as no search procedure exists.
        
        Args:
            search_term: Text to search for
        
        Returns:
            List of matching Supplier objects
        """
        # Uses: usp_SearchSuppliers
        rows = db.call_procedure_with_result('usp_SearchSuppliers', (search_term,))
        return [Supplier.from_row(row) for row in rows]
    
    @staticmethod
    def create(
        supplier_id: str,
        supplier_name: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Create a new supplier.
        Uses: usp_AddSupplier
        
        Args:
            supplier_id: Unique supplier identifier
            supplier_name: Company name
            contact_person: Main contact name
            phone: Phone number
            email: Email address
            address: Street address
            city: City
        
        Returns:
            True if created successfully
        """
        result = db.call_procedure('usp_AddSupplier', {
            'Supplier_ID': supplier_id,
            'Supplier_Name': supplier_name,
            'Contact_Person': contact_person,
            'Phone': phone,
            'Email': email,
            'Address': address,
            'City': city
        })
        return result.success
    
    @staticmethod
    def update(
        supplier_id: str,
        supplier_name: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None
    ) -> bool:
        """
        Update an existing supplier.
        Uses: usp_UpdateSupplier
        
        Args:
            supplier_id: Supplier ID to update
            supplier_name: New company name
            contact_person: New contact name
            phone: New phone
            email: New email
            address: New address
            city: New city
        
        Returns:
            True if updated successfully
        """
        result = db.call_procedure('usp_UpdateSupplier', {
            'Supplier_ID': supplier_id,
            'Supplier_Name': supplier_name,
            'Contact_Person': contact_person,
            'Phone': phone,
            'Email': email,
            'Address': address,
            'City': city
        })
        return result.success
    
    @staticmethod
    def delete(supplier_id: str) -> Tuple[bool, str]:
        """
        Delete a supplier by ID.
        Uses: usp_DeleteSupplier
        
        Note: This will fail if purchases exist for this supplier.
        
        Args:
            supplier_id: Supplier ID to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        result = db.call_procedure('usp_DeleteSupplier', {'Supplier_ID': supplier_id})
        
        if result.success:
            return True, "Supplier deleted successfully"
        else:
            return False, result.error_message or "Delete failed"
    
    @staticmethod
    def get_for_dropdown() -> List[Dict[str, str]]:
        """
        Get suppliers for dropdown/combo box.
        Uses: usp_ListSuppliers
        
        Returns:
            List of dicts with 'id' and 'name' keys
        """
        rows = db.call_procedure_with_result('usp_ListSuppliers')
        return [{'id': row.Supplier_ID, 'name': row.Supplier_Name} for row in rows]
    
    @staticmethod
    def create_supplier(
        supplier_name: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new supplier with auto-generated ID.
        Uses: usp_GetNextSupplierId, usp_AddSupplier
        
        Args:
            supplier_name: Company name (required)
            contact_person: Main contact name
            phone: Phone number
            email: Email address
            address: Street address
            city: City
        
        Returns:
            Tuple of (success: bool, message: str, new_supplier_id: Optional[str])
        """
        if not supplier_name or not supplier_name.strip():
            return False, "Supplier name is required", None
        
        # Generate next ID using stored procedure
        supplier_id = SupplierRepository.get_next_id()
        
        result = db.call_procedure('usp_AddSupplier', {
            'Supplier_ID': supplier_id,
            'Supplier_Name': supplier_name.strip(),
            'Contact_Person': contact_person,
            'Phone': phone,
            'Email': email,
            'Address': address,
            'City': city
        })
        
        if result.success:
            return True, f"Supplier '{supplier_name}' created successfully", result.created_key or supplier_id
        else:
            return False, result.error_message or "Failed to create supplier", None
