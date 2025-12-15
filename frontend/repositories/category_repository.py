"""
=============================================================================
Category Repository
=============================================================================
Provides data access methods for the CATEGORY table.

Categories are the top-level classification for products (e.g., "Protection",
"Power & Charging"). Each category can have multiple subcategories.

Table Schema:
    CATEGORY(Cat_ID, Cat_Name, Description)

Changes Applied:
- MIGRATED TO STORED PROCEDURES for all CRUD operations
- Uses usp_AddCategory, usp_UpdateCategory, usp_DeleteCategory
- Uses usp_GetCategoryById, usp_ListCategories, usp_GetNextCategoryId
- Maintains backward-compatible interface for existing UI code

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import db
from repositories.field_mapper import map_category


@dataclass
class Category:
    """
    Data class representing a product category.
    
    Attributes:
        cat_id: Unique category identifier (e.g., 'CAT001')
        cat_name: Display name of the category
        description: Optional detailed description
    """
    cat_id: str
    cat_name: str
    description: Optional[str] = None
    
    @classmethod
    def from_row(cls, row) -> 'Category':
        """Create a Category instance from a database row."""
        return cls(
            cat_id=row.Cat_ID,
            cat_name=row.Cat_Name,
            description=getattr(row, 'Description', None)
        )
    
    # Add property aliases for UI compatibility
    @property
    def category_id(self) -> str:
        return self.cat_id
    
    @property
    def category_name(self) -> str:
        return self.cat_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'cat_id': self.cat_id,
            'cat_name': self.cat_name,
            'description': self.description
        }


class CategoryRepository:
    """
    Repository class for CATEGORY table operations.
    
    All methods are static for convenience. 
    NOW USES STORED PROCEDURES for all database operations.
    """
    
    @staticmethod
    def get_all() -> List[Category]:
        """
        Retrieve all categories from the database.
        Uses: usp_ListCategories
        
        Returns:
            List of Category objects ordered by Cat_ID
        
        Example:
            categories = CategoryRepository.get_all()
            for cat in categories:
                print(f"{cat.cat_id}: {cat.cat_name}")
        """
        rows = db.call_procedure_with_result('usp_ListCategories')
        return [Category.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(cat_id: str) -> Optional[Category]:
        """
        Retrieve a single category by its ID.
        Uses: usp_GetCategoryById
        
        Args:
            cat_id: The category ID to look up
        
        Returns:
            Category object if found, None otherwise
        
        Example:
            category = CategoryRepository.get_by_id('CAT001')
            if category:
                print(category.cat_name)
        """
        rows = db.call_procedure_with_result('usp_GetCategoryById', {'Cat_ID': cat_id})
        return Category.from_row(rows[0]) if rows else None
    
    @staticmethod
    def create(cat_id: str, cat_name: str, description: Optional[str] = None) -> bool:
        """
        Create a new category.
        Uses: usp_AddCategory
        
        Args:
            cat_id: Unique category identifier
            cat_name: Display name for the category
            description: Optional description
        
        Returns:
            True if created successfully, False otherwise
        
        Example:
            success = CategoryRepository.create(
                cat_id='CAT003',
                cat_name='Audio',
                description='Audio accessories like earphones and speakers'
            )
        """
        return db.call_procedure('usp_AddCategory', (cat_id, cat_name, description), has_output=False)
    
    @staticmethod
    def update(cat_id: str, cat_name: str, description: Optional[str] = None) -> bool:
        """
        Update an existing category.
        Uses: usp_UpdateCategory
        
        Args:
            cat_id: Category ID to update
            cat_name: New category name
            description: New description
        
        Returns:
            True if updated successfully, False otherwise
        """
        return db.call_procedure('usp_UpdateCategory', (cat_id, cat_name, description), has_output=False)
    
    @staticmethod
    def delete(cat_id: str) -> tuple[bool, str]:
        """
        Delete a category by ID.
        Uses: usp_DeleteCategory
        
        Note: This will fail if subcategories exist for this category
        due to foreign key constraints.
        
        Args:
            cat_id: Category ID to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = db.call_procedure('usp_DeleteCategory', (cat_id,), has_output=False)
            if success:
                return True, "Category deleted successfully"
            else:
                return False, "Delete failed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available category ID.
        Uses: usp_GetNextCategoryId
        
        Returns:
            Next ID in format 'CAT###' (e.g., 'CAT004')
        """
        next_id = db.call_procedure_scalar('usp_GetNextCategoryId', column_name='NextId')
        return next_id or 'CAT001'
    
    @staticmethod
    def get_all_categories() -> List[Category]:
        """
        Alias for get_all() - for UI consistency.
        Uses: usp_ListCategories
        
        Returns:
            List of Category objects ordered by Cat_Name
        """
        rows = db.call_procedure_with_result('usp_ListCategories')
        return [Category.from_row(row) for row in rows]
    
    @staticmethod
    def create_category(cat_name: str, description: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new category with auto-generated ID.
        Uses: usp_GetNextCategoryId, usp_AddCategory
        
        Args:
            cat_name: Display name for the category (required)
            description: Optional description
        
        Returns:
            Tuple of (success: bool, message: str, new_cat_id: Optional[str])
        """
        if not cat_name or not cat_name.strip():
            return False, "Category name is required", None
        
        # Generate next ID using stored procedure
        cat_id = CategoryRepository.get_next_id()
        
        try:
            success = db.call_procedure('usp_AddCategory', (cat_id, cat_name.strip(), description), has_output=False)
            if success:
                return True, f"Category '{cat_name}' created successfully", cat_id
            else:
                return False, "Failed to create category", None
        except Exception as e:
            return False, str(e), None
