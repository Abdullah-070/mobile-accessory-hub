"""
=============================================================================
Subcategory Repository
=============================================================================
Provides data access methods for the SUBCATEGORY table.

Subcategories provide a second level of classification under categories
(e.g., "Phone Cases" under "Protection").

Table Schema:
    SUBCATEGORY(Subcat_ID, Cat_ID, Subcat_Name, Description)

Changes Applied:
- MIGRATED TO STORED PROCEDURES for all CRUD operations
- Uses usp_AddSubcategory, usp_UpdateSubcategory, usp_DeleteSubcategory
- Uses usp_GetSubcategoryById, usp_ListSubcategories, usp_GetNextSubcategoryId
- Maintains backward-compatible interface for existing UI code

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import db
from repositories.field_mapper import map_subcategory


@dataclass
class Subcategory:
    """
    Data class representing a product subcategory.
    
    Attributes:
        subcat_id: Unique subcategory identifier
        cat_id: Parent category ID (foreign key)
        subcat_name: Display name
        description: Optional detailed description
        cat_name: Parent category name (for display, loaded via JOIN)
    """
    subcat_id: str
    cat_id: str
    subcat_name: str
    description: Optional[str] = None
    cat_name: Optional[str] = None  # Joined from CATEGORY table
    
    @classmethod
    def from_row(cls, row) -> 'Subcategory':
        """Create a Subcategory instance from a database row."""
        return cls(
            subcat_id=row.Subcat_ID,
            cat_id=row.Cat_ID,
            subcat_name=row.Subcat_Name,
            description=getattr(row, 'Description', None),
            cat_name=getattr(row, 'Cat_Name', None)
        )
    
    # Add property aliases for UI compatibility
    @property
    def subcategory_id(self) -> str:
        return self.subcat_id
    
    @property
    def subcategory_name(self) -> str:
        return self.subcat_name
    
    @property
    def category_id(self) -> str:
        return self.cat_id
    
    @property
    def category_name(self) -> Optional[str]:
        return self.cat_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'subcat_id': self.subcat_id,
            'cat_id': self.cat_id,
            'subcat_name': self.subcat_name,
            'description': self.description,
            'cat_name': self.cat_name
        }


class SubcategoryRepository:
    """
    Repository class for SUBCATEGORY table operations.
    NOW USES STORED PROCEDURES for all database operations.
    """
    
    @staticmethod
    def get_all() -> List[Subcategory]:
        """
        Retrieve all subcategories with their parent category names.
        Uses: usp_ListSubcategories
        
        Returns:
            List of Subcategory objects ordered by Cat_ID, Subcat_ID
        """
        rows = db.call_procedure_with_result('usp_ListSubcategories')
        return [Subcategory.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(subcat_id: str) -> Optional[Subcategory]:
        """
        Retrieve a single subcategory by its ID.
        Uses: usp_GetSubcategoryById
        
        Args:
            subcat_id: The subcategory ID to look up
        
        Returns:
            Subcategory object if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetSubcategoryById', {'Subcat_ID': subcat_id})
        return Subcategory.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_category(cat_id: str) -> List[Subcategory]:
        """
        Retrieve all subcategories for a specific category.
        Uses: usp_GetSubcategoriesByCategory
        
        Args:
            cat_id: Parent category ID
        
        Returns:
            List of Subcategory objects for the specified category
        """
        rows = db.call_procedure_with_result('usp_GetSubcategoriesByCategory', (cat_id,))
        return [Subcategory.from_row(row) for row in rows]
    
    @staticmethod
    def create(subcat_id: str, cat_id: str, subcat_name: str, 
               description: Optional[str] = None) -> bool:
        """
        Create a new subcategory.
        Uses: usp_AddSubcategory
        
        Args:
            subcat_id: Unique subcategory identifier
            cat_id: Parent category ID
            subcat_name: Display name
            description: Optional description
        
        Returns:
            True if created successfully
        """
        return db.call_procedure('usp_AddSubcategory', (subcat_id, cat_id, subcat_name, description), has_output=False)
    
    @staticmethod
    def update(subcat_id: str, cat_id: str, subcat_name: str,
               description: Optional[str] = None) -> bool:
        """
        Update an existing subcategory.
        Uses: usp_UpdateSubcategory
        
        Args:
            subcat_id: Subcategory ID to update
            cat_id: New parent category ID
            subcat_name: New name
            description: New description
        
        Returns:
            True if updated successfully
        """
        return db.call_procedure('usp_UpdateSubcategory', (subcat_id, cat_id, subcat_name, description), has_output=False)
    
    @staticmethod
    def delete(subcat_id: str) -> tuple[bool, str]:
        """
        Delete a subcategory by ID.
        Uses: usp_DeleteSubcategory
        
        Note: This will fail if products exist for this subcategory.
        
        Args:
            subcat_id: Subcategory ID to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = db.call_procedure('usp_DeleteSubcategory', (subcat_id,), has_output=False)
            if success:
                return True, "Subcategory deleted successfully"
            else:
                return False, "Delete failed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def delete_by_category(cat_id: str) -> bool:
        """
        Delete all subcategories for a given category.
        Uses: usp_DeleteSubcategoriesByCategory
        
        Args:
            cat_id: Category ID whose subcategories to delete
        
        Returns:
            True if deleted successfully (or no subcategories exist)
        """
        try:
            db.call_procedure('usp_DeleteSubcategoriesByCategory', (cat_id,), has_output=False)
            return True
        except Exception:
            return False
    
    @staticmethod
    def update_name(subcat_id: str, subcat_name: str) -> bool:
        """
        Update just the subcategory name.
        Uses: usp_UpdateSubcategory (gets current data first)
        
        Args:
            subcat_id: Subcategory ID to update
            subcat_name: New name
        
        Returns:
            True if updated successfully
        """
        # Get current subcategory to preserve other fields
        current = SubcategoryRepository.get_by_id(subcat_id)
        if not current:
            return False
        
        return SubcategoryRepository.update(
            subcat_id=subcat_id,
            cat_id=current.cat_id,
            subcat_name=subcat_name,
            description=current.description
        )
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available subcategory ID.
        Uses: usp_GetNextSubcategoryId
        
        Returns:
            Next ID in format 'SUB###' (e.g., 'SUB004')
        """
        next_id = db.call_procedure_scalar('usp_GetNextSubcategoryId', column_name='NextId')
        return next_id or 'SUB001'
    
    @staticmethod
    def get_subcategories_for_category(cat_id: str) -> List[Subcategory]:
        """
        Alias for get_by_category() - for UI consistency.
        Uses: usp_ListSubcategories
        
        Args:
            cat_id: Parent category ID
        
        Returns:
            List of Subcategory objects for the specified category
        """
        return SubcategoryRepository.get_by_category(cat_id)
    
    @staticmethod
    def create_subcategory(cat_id: str, subcat_name: str, 
                          description: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new subcategory with auto-generated ID.
        Uses: usp_GetNextSubcategoryId, usp_AddSubcategory
        
        Args:
            cat_id: Parent category ID (required)
            subcat_name: Display name (required)
            description: Optional description
        
        Returns:
            Tuple of (success: bool, message: str, new_subcat_id: Optional[str])
        """
        if not cat_id or not subcat_name or not subcat_name.strip():
            return False, "Category ID and subcategory name are required", None
        
        # Generate next ID using stored procedure
        subcat_id = SubcategoryRepository.get_next_id()
        
        try:
            success = db.call_procedure('usp_AddSubcategory', (subcat_id, cat_id, subcat_name.strip(), description), has_output=False)
            if success:
                return True, f"Subcategory '{subcat_name}' created successfully", subcat_id
            else:
                return False, "Failed to create subcategory", None
        except Exception as e:
            return False, str(e), None
