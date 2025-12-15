"""
=============================================================================
Product Repository
=============================================================================
Provides data access methods for the PRODUCT table.
Uses stored procedures for all database operations.

Products represent the mobile accessories sold in the store. Each product
belongs to a subcategory and has pricing, stock level, and descriptive info.

Table Schema:
    PRODUCT(Product_Code, Subcat_ID, Product_Name, Brand, Description,
            Cost_Price, Retail_Price, Min_Stock_Level, Date_Added)

Stored Procedures Used:
- usp_AddProduct: Create new product
- usp_UpdateProduct: Update existing product
- usp_DeleteProduct: Delete product
- usp_GetProductByCode: Get single product
- usp_ListProducts: Get all products
- usp_GetProductsByCategory: Get products by category
- usp_GetProductsBySubcategory: Get products by subcategory
- usp_SearchProducts: Search with filters
- usp_GetLowStockProducts: Get products below min stock
- usp_GetNextProductCode: Generate next product code

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import db


@dataclass
class Product:
    """
    Data class representing a product.
    
    Attributes:
        product_code: Unique product identifier (e.g., 'PRD001')
        subcat_id: Subcategory ID (foreign key)
        product_name: Display name
        brand: Manufacturer/brand name
        description: Detailed description
        cost_price: Purchase cost from supplier
        retail_price: Selling price to customers
        min_stock_level: Minimum stock before reorder alert
        date_added: Date product was added to system
        subcat_name: Subcategory name (joined)
        cat_name: Category name (joined)
        current_stock: Current inventory level (joined from INVENTORY)
    """
    product_code: str
    subcat_id: str
    product_name: str
    brand: Optional[str]
    description: Optional[str]
    cost_price: Decimal
    retail_price: Decimal
    min_stock_level: int
    date_added: date
    subcat_name: Optional[str] = None
    cat_name: Optional[str] = None
    current_stock: Optional[int] = None
    
    @classmethod
    def from_row(cls, row) -> 'Product':
        """Create a Product instance from a database row."""
        return cls(
            product_code=row.Product_Code,
            subcat_id=row.Subcat_ID,
            product_name=row.Product_Name,
            brand=getattr(row, 'Brand', None),
            description=getattr(row, 'Description', None),
            cost_price=Decimal(str(row.Cost_Price)),
            retail_price=Decimal(str(row.Retail_Price)),
            min_stock_level=row.Min_Stock_Level,
            date_added=row.Date_Added,
            subcat_name=getattr(row, 'Subcat_Name', None),
            cat_name=getattr(row, 'Cat_Name', None),
            current_stock=getattr(row, 'Current_Stock', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'product_code': self.product_code,
            'subcat_id': self.subcat_id,
            'product_name': self.product_name,
            'brand': self.brand,
            'description': self.description,
            'cost_price': float(self.cost_price),
            'retail_price': float(self.retail_price),
            'min_stock_level': self.min_stock_level,
            'date_added': str(self.date_added),
            'subcat_name': self.subcat_name,
            'cat_name': self.cat_name,
            'current_stock': self.current_stock
        }
    
    @property
    def profit_margin(self) -> Decimal:
        """Calculate profit margin per unit."""
        return self.retail_price - self.cost_price
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is below minimum stock level."""
        if self.current_stock is None:
            return True
        return self.current_stock < self.min_stock_level
    
    # Add property aliases for UI compatibility
    @property
    def product_id(self) -> str:
        """Alias for product_code."""
        return self.product_code
    
    @property
    def category_id(self) -> Optional[str]:
        """Get category ID from subcategory."""
        return None  # Would need join to get this
    
    @property
    def category_name(self) -> Optional[str]:
        """Alias for cat_name."""
        return self.cat_name
    
    @property
    def subcategory_id(self) -> str:
        """Alias for subcat_id."""
        return self.subcat_id
    
    @property
    def subcategory_name(self) -> Optional[str]:
        """Alias for subcat_name."""
        return self.subcat_name
    
    @property
    def unit_price(self) -> Decimal:
        """Alias for cost_price."""
        return self.cost_price
    
    @property
    def price(self) -> Decimal:
        """Alias for retail_price."""
        return self.retail_price
        return self.current_stock <= self.min_stock_level
    
    # =========================================================================
    # UI Compatibility Aliases
    # =========================================================================
    
    @property
    def product_id(self) -> str:
        """Alias for product_code - UI compatibility."""
        return self.product_code
    
    @property
    def price(self) -> Decimal:
        """Alias for retail_price - UI compatibility."""
        return self.retail_price
    
    @property
    def sku(self) -> Optional[str]:
        """Alias - returns product_code as SKU."""
        return self.product_code
    
    @property
    def barcode(self) -> Optional[str]:
        """Alias - returns product_code as barcode."""
        return self.product_code


class ProductRepository:
    """
    Repository class for PRODUCT table operations.
    Uses stored procedures for all database operations.
    """
    
    @staticmethod
    def get_all() -> List[Product]:
        """
        Retrieve all products with their category and inventory info.
        
        Returns:
            List of Product objects ordered by Product_Code
        """
        rows = db.call_procedure_with_result('usp_ListProducts', ())
        return [Product.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(product_code: str) -> Optional[Product]:
        """
        Retrieve a single product by its code.
        
        Args:
            product_code: The product code to look up
        
        Returns:
            Product object if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetProductByCode', (product_code,))
        return Product.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_subcategory(subcat_id: str) -> List[Product]:
        """
        Retrieve all products in a specific subcategory.
        
        Args:
            subcat_id: Subcategory ID to filter by
        
        Returns:
            List of Product objects
        """
        rows = db.call_procedure_with_result('usp_GetProductsBySubcategory', (subcat_id,))
        return [Product.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_category(cat_id: str) -> List[Product]:
        """
        Retrieve all products in a specific category (all subcategories).
        
        Args:
            cat_id: Category ID to filter by
        
        Returns:
            List of Product objects
        """
        rows = db.call_procedure_with_result('usp_GetProductsByCategory', (cat_id,))
        return [Product.from_row(row) for row in rows]
    
    @staticmethod
    def search(
        search_term: str = '',
        cat_id: Optional[str] = None,
        subcat_id: Optional[str] = None,
        low_stock_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Product], int]:
        """
        Search products with filters and pagination.
        
        Args:
            search_term: Search in product name, code, brand, description
            cat_id: Filter by category
            subcat_id: Filter by subcategory
            low_stock_only: Only show products below min stock level
            page: Page number (1-based)
            page_size: Number of results per page
        
        Returns:
            Tuple of (list of products, total count)
        """
        rows = db.call_procedure_with_result('usp_SearchProducts', (
            search_term if search_term else None,
            cat_id,
            subcat_id,
            1 if low_stock_only else 0,
            page,
            page_size
        ))
        products = [Product.from_row(row) for row in rows]
        
        # For total count estimation: if full page, there may be more
        total = len(products) if len(products) < page_size else page * page_size + 1
        
        return products, total
    
    @staticmethod
    def get_low_stock() -> List[Product]:
        """
        Retrieve all products with stock at or below minimum level.
        
        Returns:
            List of Product objects needing restock
        """
        rows = db.call_procedure_with_result('usp_GetLowStockProducts', ())
        return [Product.from_row(row) for row in rows]
    
    @staticmethod
    def create(
        product_code: str,
        subcat_id: str,
        product_name: str,
        brand: Optional[str],
        description: Optional[str],
        cost_price: Decimal,
        retail_price: Decimal,
        min_stock_level: int = 5,
        date_added: Optional[date] = None,
        initial_stock: int = 0
    ) -> bool:
        """
        Create a new product using stored procedure.
        
        Args:
            product_code: Unique product identifier
            subcat_id: Subcategory ID
            product_name: Display name
            brand: Manufacturer/brand
            description: Detailed description
            cost_price: Purchase cost
            retail_price: Selling price
            min_stock_level: Minimum stock level (default: 5)
            date_added: Date added (ignored - uses GETDATE() in SQL)
            initial_stock: Initial stock quantity (default: 0)
        
        Returns:
            True if created successfully
        """
        try:
            # Stored procedure params: ProductCode, SubcatId, ProductName, Brand, 
            # Description, CostPrice, RetailPrice, MinStockLevel, InitialStock
            result = db.call_procedure('usp_AddProduct', (
                product_code,
                subcat_id,
                product_name,
                brand,
                description,
                float(cost_price),
                float(retail_price),
                min_stock_level,
                initial_stock  # Not date_added - SP uses GETDATE() internally
            ), has_output=False)
            return result
        except Exception as e:
            print(f"ERROR creating product: {e}")
            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                raise ValueError(f"Product code '{product_code}' already exists")
            return False
    
    @staticmethod
    def update(
        product_code: str,
        subcat_id: str,
        product_name: str,
        brand: Optional[str],
        description: Optional[str],
        cost_price: Decimal,
        retail_price: Decimal,
        min_stock_level: int
    ) -> bool:
        """
        Update an existing product using stored procedure.
        
        Args:
            product_code: Product code to update
            subcat_id: New subcategory ID
            product_name: New name
            brand: New brand
            description: New description
            cost_price: New cost price
            retail_price: New retail price
            min_stock_level: New minimum stock level
        
        Returns:
            True if updated successfully
        """
        try:
            return db.call_procedure('usp_UpdateProduct', (
                product_code,
                subcat_id,
                product_name,
                brand,
                description,
                float(cost_price),
                float(retail_price),
                min_stock_level
            ), has_output=False)
        except Exception:
            return False
    
    @staticmethod
    def delete(product_code: str) -> Tuple[bool, str]:
        """
        Delete a product by code using stored procedure.
        
        Note: This will fail if the product has purchase or sale history.
        
        Args:
            product_code: Product code to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            result = db.call_procedure('usp_DeleteProduct', (product_code,), has_output=False)
            if result:
                return True, "Product deleted successfully"
            else:
                return False, "Product not found or could not be deleted"
        except Exception as e:
            error_msg = str(e)
            if 'purchase' in error_msg.lower():
                return False, "Cannot delete: Product has purchase records"
            elif 'sale' in error_msg.lower():
                return False, "Cannot delete: Product has sale records"
            return False, f"Delete failed: {error_msg}"
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available product code using stored procedure.
        
        Returns:
            Next ID in format 'PRD###' (e.g., 'PRD006')
        """
        return db.call_procedure_scalar('usp_GetNextProductCode', (), 'NextCode')
    
    @staticmethod
    def get_for_autocomplete(search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get products for autocomplete/search dropdown.
        
        Args:
            search_term: Search string
            limit: Maximum results to return
        
        Returns:
            List of dicts with product_code, product_name, brand, retail_price, current_stock
        """
        # Use search procedure with limited results
        rows = db.call_procedure_with_result('usp_SearchProducts', (
            search_term,
            None,  # cat_id
            None,  # subcat_id
            0,     # low_stock_only
            1,     # page
            limit  # page_size
        ))
        
        return [
            {
                'product_code': row.Product_Code,
                'product_name': row.Product_Name,
                'brand': getattr(row, 'Brand', None),
                'retail_price': float(row.Retail_Price) if hasattr(row, 'Retail_Price') and row.Retail_Price else 0.0,
                'current_stock': getattr(row, 'Current_Stock', 0) or 0
            }
            for row in rows
        ]
