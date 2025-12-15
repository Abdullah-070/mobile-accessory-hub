"""
=============================================================================
Inventory Repository
=============================================================================
Provides data access methods for the INVENTORY table.
Uses stored procedures for all database operations.

Inventory tracks current stock levels for each product. Stock is updated
automatically by the purchase and sale stored procedures.

Table Schema:
    INVENTORY(Product_Code, Current_Stock, Last_Updated)

Stored Procedures Used:
- usp_ListInventory: Get all inventory with product details
- usp_GetInventoryByProduct: Get inventory for a specific product
- usp_GetLowStockProducts: Get products below min stock level
- usp_AdjustInventory: Manually adjust stock level
- usp_GetInventorySummary: Get inventory statistics

=============================================================================
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import db


@dataclass
class Inventory:
    """
    Data class representing an inventory record (simple version).
    
    Attributes:
        inventory_id: Primary key
        product_id: Product identifier
        quantity_in_stock: Current stock quantity
        reorder_level: Minimum stock level before reorder
    """
    inventory_id: int
    product_id: int
    quantity_in_stock: int
    reorder_level: int


@dataclass
class InventoryItem:
    """
    Data class representing an inventory record.
    
    Attributes:
        product_code: Product identifier (foreign key to PRODUCT)
        current_stock: Number of units in stock
        last_updated: Timestamp of last stock change
        product_name: Product name (joined)
        brand: Product brand (joined)
        min_stock_level: Minimum stock level (joined from PRODUCT)
        retail_price: Selling price (joined from PRODUCT)
        cost_price: Purchase price (joined from PRODUCT)
    """
    product_code: str
    current_stock: int
    last_updated: datetime
    product_name: Optional[str] = None
    brand: Optional[str] = None
    min_stock_level: Optional[int] = None
    retail_price: Optional[float] = None
    cost_price: Optional[float] = None
    subcat_name: Optional[str] = None
    cat_name: Optional[str] = None
    
    @classmethod
    def from_row(cls, row) -> 'InventoryItem':
        """Create an InventoryItem instance from a database row."""
        return cls(
            product_code=row.Product_Code,
            current_stock=row.Current_Stock,
            last_updated=row.Last_Updated,
            product_name=getattr(row, 'Product_Name', None),
            brand=getattr(row, 'Brand', None),
            min_stock_level=getattr(row, 'Min_Stock_Level', None),
            retail_price=getattr(row, 'Retail_Price', None),
            cost_price=getattr(row, 'Cost_Price', None),
            subcat_name=getattr(row, 'Subcat_Name', None),
            cat_name=getattr(row, 'Cat_Name', None)
        )
    
    @property
    def product_id(self) -> str:
        """Alias for product_code - UI compatibility."""
        return self.product_code
    
    @property
    def quantity_in_stock(self) -> int:
        """Alias for current_stock - UI compatibility."""
        return self.current_stock
    
    @property
    def category_name(self) -> Optional[str]:
        """Alias for cat_name - UI compatibility."""
        return self.cat_name
    
    @property
    def subcategory_name(self) -> Optional[str]:
        """Alias for subcat_name - UI compatibility."""
        return self.subcat_name
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is at or below minimum level."""
        if self.min_stock_level is None:
            return False
        return self.current_stock <= self.min_stock_level
    
    @property
    def stock_value(self) -> float:
        """Calculate total value of stock at cost price."""
        if self.cost_price is None:
            return 0.0
        return self.current_stock * self.cost_price
    
    @property
    def retail_value(self) -> float:
        """Calculate total value of stock at retail price."""
        if self.retail_price is None:
            return 0.0
        return self.current_stock * self.retail_price


class InventoryRepository:
    """
    Repository class for INVENTORY table operations.
    Uses stored procedures for all database operations.
    
    Note: Stock levels are typically modified by stored procedures
    (usp_CreatePurchase increases stock, usp_CreateSale decreases stock).
    Direct updates should be used only for manual adjustments.
    """
    
    @staticmethod
    def get_all() -> List[InventoryItem]:
        """
        Retrieve all inventory records with product details.
        
        Returns:
            List of InventoryItem objects
        """
        rows = db.call_procedure_with_result('usp_ListInventory', ())
        return [InventoryItem.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_product_code(product_code: str) -> Optional[InventoryItem]:
        """
        Retrieve inventory for a specific product.
        
        Args:
            product_code: Product code to look up
        
        Returns:
            InventoryItem if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetInventoryByProduct', (product_code,))
        return InventoryItem.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_stock_level(product_code: str) -> int:
        """
        Get current stock level for a product.
        
        Args:
            product_code: Product code to check
        
        Returns:
            Current stock level (0 if not found)
        """
        rows = db.call_procedure_with_result('usp_GetInventoryByProduct', (product_code,))
        if rows:
            return rows[0].Current_Stock
        return 0
    
    @staticmethod
    def get_low_stock_items() -> List[InventoryItem]:
        """
        Retrieve all items with stock at or below minimum level.
        
        Returns:
            List of InventoryItem objects needing restock
        """
        rows = db.call_procedure_with_result('usp_GetLowStockProducts', ())
        return [InventoryItem.from_row(row) for row in rows]
    
    @staticmethod
    def get_low_stock_count() -> int:
        """
        Get count of products with low stock.
        
        Returns:
            Number of products at or below minimum stock level
        """
        rows = db.call_procedure_with_result('usp_GetLowStockProducts', ())
        return len(rows)
    
    @staticmethod
    def update_stock(product_code: str, new_stock: int) -> bool:
        """
        Manually update stock level for a product.
        
        Use this for manual stock adjustments only. Normal stock changes
        should go through the purchase and sale stored procedures.
        
        Args:
            product_code: Product code to update
            new_stock: New stock level (must be >= 0)
        
        Returns:
            True if updated successfully
        """
        if new_stock < 0:
            return False
        
        current = InventoryRepository.get_stock_level(product_code)
        adjustment = new_stock - current
        
        try:
            return db.call_procedure('usp_AdjustInventory', (
                product_code,
                adjustment,
                'Manual stock update'
            ), has_output=False)
        except Exception:
            return False
    
    @staticmethod
    def adjust_stock(product_code: str, adjustment: int, reason: str = '') -> bool:
        """
        Adjust stock level by a given amount (positive or negative).
        
        Args:
            product_code: Product code to adjust
            adjustment: Amount to add (positive) or subtract (negative)
            reason: Reason for adjustment (for logging)
        
        Returns:
            True if adjusted successfully
        
        Note: This will fail if adjustment would result in negative stock.
        """
        try:
            return db.call_procedure('usp_AdjustInventory', (
                product_code,
                adjustment,
                reason if reason else 'Manual adjustment'
            ), has_output=False)
        except Exception:
            return False
    
    @staticmethod
    def check_stock_available(product_code: str, quantity: int) -> bool:
        """
        Check if sufficient stock is available for a product.
        
        Args:
            product_code: Product code to check
            quantity: Required quantity
        
        Returns:
            True if quantity is available, False otherwise
        """
        current = InventoryRepository.get_stock_level(product_code)
        return current >= quantity
    
    @staticmethod
    def get_total_inventory_value() -> Dict[str, float]:
        """
        Calculate total inventory value at cost and retail prices.
        
        Returns:
            Dict with 'cost_value' and 'retail_value'
        """
        rows = db.call_procedure_with_result('usp_GetInventorySummary', ())
        if rows:
            row = rows[0]
            return {
                'cost_value': float(getattr(row, 'Cost_Value', 0) or 0),
                'retail_value': float(getattr(row, 'Retail_Value', 0) or 0)
            }
        return {'cost_value': 0.0, 'retail_value': 0.0}
    
    @staticmethod
    def get_inventory_summary() -> Dict[str, Any]:
        """
        Get summary statistics for inventory.
        
        Returns:
            Dict with total_products, total_units, low_stock_count,
            cost_value, retail_value
        """
        rows = db.call_procedure_with_result('usp_GetInventorySummary', ())
        if rows:
            row = rows[0]
            return {
                'total_products': getattr(row, 'Total_Products', 0) or 0,
                'total_units': getattr(row, 'Total_Units', 0) or 0,
                'low_stock_count': getattr(row, 'Low_Stock_Count', 0) or 0,
                'cost_value': float(getattr(row, 'Cost_Value', 0) or 0),
                'retail_value': float(getattr(row, 'Retail_Value', 0) or 0)
            }
        return {
            'total_products': 0,
            'total_units': 0,
            'low_stock_count': 0,
            'cost_value': 0.0,
            'retail_value': 0.0
        }
