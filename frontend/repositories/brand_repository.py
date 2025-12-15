"""
=============================================================================
Brand Repository
=============================================================================
Provides data access methods for the BRAND table.

Table Schema:
    BRAND(Brand_ID, Brand_Name, Description)

Uses stored procedures for all CRUD operations.
=============================================================================
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import db


@dataclass
class Brand:
    """Data class representing a product brand."""
    brand_id: str
    brand_name: str
    description: Optional[str] = None
    
    @classmethod
    def from_row(cls, row) -> 'Brand':
        """Create a Brand instance from a database row."""
        return cls(
            brand_id=row.Brand_ID,
            brand_name=row.Brand_Name,
            description=getattr(row, 'Description', None)
        )


class BrandRepository:
    """Repository class for BRAND table operations."""
    
    @staticmethod
    def get_all() -> List[Brand]:
        """Get all brands ordered by name."""
        rows = db.call_procedure_with_result('usp_ListBrands')
        return [Brand.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(brand_id: str) -> Optional[Brand]:
        """Get a brand by its ID."""
        rows = db.call_procedure_with_result('usp_GetBrandById', (brand_id,))
        return Brand.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_name(brand_name: str) -> Optional[Brand]:
        """Get a brand by its name."""
        rows = db.call_procedure_with_result('usp_GetBrandByName', (brand_name,))
        return Brand.from_row(rows[0]) if rows else None
    
    @staticmethod
    def create(brand_id: str, brand_name: str, description: Optional[str] = None) -> bool:
        """Create a new brand."""
        return db.call_procedure('usp_AddBrand', (brand_id, brand_name, description), has_output=False)
    
    @staticmethod
    def update(brand_id: str, brand_name: str, description: Optional[str] = None) -> bool:
        """Update an existing brand."""
        return db.call_procedure('usp_UpdateBrand', (brand_id, brand_name, description), has_output=False)
    
    @staticmethod
    def delete(brand_id: str) -> Tuple[bool, str]:
        """Delete a brand by ID."""
        try:
            success = db.call_procedure('usp_DeleteBrand', (brand_id,), has_output=False)
            if success:
                return True, "Brand deleted successfully"
            else:
                return False, "Delete failed"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_products_exist(brand_name: str) -> Tuple[int, int, int]:
        """
        Check if products exist for a brand and if they have inventory.
        
        Args:
            brand_name: The brand name to check
            
        Returns:
            Tuple of (total_products, products_with_stock, total_stock_quantity)
        """
        rows = db.call_procedure_with_result('usp_CheckProductsExistForBrand', (brand_name,))
        if rows and len(rows) > 0:
            row = rows[0]
            return (
                getattr(row, 'ProductCount', 0),
                getattr(row, 'ProductsWithStock', 0),
                getattr(row, 'TotalStockQty', 0)
            )
        return (0, 0, 0)
    
    @staticmethod
    def get_next_id() -> str:
        """Generate the next available brand ID."""
        next_id = db.call_procedure_scalar('usp_GetNextBrandId', column_name='NextId')
        return next_id or 'BRD001'
    
    @staticmethod
    def create_brand(brand_name: str, description: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new brand with auto-generated ID.
        
        Returns:
            Tuple of (success: bool, message: str, new_brand_id: Optional[str])
        """
        if not brand_name or not brand_name.strip():
            return False, "Brand name is required", None
        
        brand_id = BrandRepository.get_next_id()
        
        try:
            success = db.call_procedure('usp_AddBrand', (brand_id, brand_name.strip(), description), has_output=False)
            if success:
                return True, f"Brand '{brand_name}' created successfully", brand_id
            else:
                return False, "Failed to create brand", None
        except Exception as e:
            return False, str(e), None
    
    @staticmethod
    def get_brand_names() -> List[str]:
        """Get list of all brand names for dropdowns."""
        brands = BrandRepository.get_all()
        return [b.brand_name for b in brands]
