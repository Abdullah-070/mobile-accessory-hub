"""
=============================================================================
Purchase Repository
=============================================================================
Provides data access methods for the PURCHASE and PURCHASE_DETAIL tables.
Uses stored procedures for all database operations.

Purchases represent orders placed with suppliers. Creating a purchase
automatically updates inventory via the usp_CreatePurchase stored procedure.

Table Schemas:
    PURCHASE(Purchase_No, Supplier_ID, Purchase_Date, Total_Amount, Payment_Status, Notes)
    PURCHASE_DETAIL(Purchase_No, Product_Code, Quantity, Unit_Price, Line_Total)

Stored Procedures Used:
- usp_CreatePurchase: Create purchase with items (via db.call_create_purchase)
- usp_GetPurchaseById: Get single purchase
- usp_ListPurchases: List all purchases
- usp_GetPurchasesBySupplier: Get purchases by supplier
- usp_GetPurchasesByDateRange: Get purchases in date range
- usp_GetPurchaseDetails: Get purchase line items
- usp_MarkPurchaseReceived: Mark as received and update inventory
- usp_UpdatePurchaseStatus: Update payment status
- usp_GetNextPurchaseNo: Generate next purchase number

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import db


@dataclass
class PurchaseDetail:
    """
    Data class representing a purchase line item.
    
    Attributes:
        purchase_no: Parent purchase number
        product_code: Product being purchased
        quantity: Number of units
        unit_price: Price per unit from supplier
        line_total: quantity * unit_price
        product_name: Product name (joined)
    """
    purchase_no: str
    product_code: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product_name: Optional[str] = None
    
    @classmethod
    def from_row(cls, row) -> 'PurchaseDetail':
        """Create a PurchaseDetail instance from a database row."""
        return cls(
            purchase_no=row.Purchase_No,
            product_code=row.Product_Code,
            quantity=row.Quantity,
            unit_price=Decimal(str(row.Unit_Price)),
            line_total=Decimal(str(row.Line_Total)),
            product_name=getattr(row, 'Product_Name', None)
        )


@dataclass
class Purchase:
    """
    Data class representing a purchase order.
    
    Attributes:
        purchase_no: Unique purchase order number
        supplier_id: Supplier ID (foreign key)
        purchase_date: Date of purchase
        total_amount: Sum of all line totals
        payment_status: 'Pending', 'Paid', 'Partial'
        notes: Optional notes
        supplier_name: Supplier name (joined)
        details: List of line items
    """
    purchase_no: str
    supplier_id: str
    purchase_date: date
    total_amount: Decimal
    payment_status: str
    notes: Optional[str] = None
    supplier_name: Optional[str] = None
    details: Optional[List[PurchaseDetail]] = None
    
    @classmethod
    def from_row(cls, row) -> 'Purchase':
        """Create a Purchase instance from a database row."""
        return cls(
            purchase_no=row.Purchase_No,
            supplier_id=row.Supplier_ID,
            purchase_date=row.Purchase_Date,
            total_amount=Decimal(str(row.Total_Amount)),
            payment_status=row.Payment_Status,
            notes=getattr(row, 'Notes', None),
            supplier_name=getattr(row, 'Supplier_Name', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'purchase_no': self.purchase_no,
            'supplier_id': self.supplier_id,
            'purchase_date': str(self.purchase_date),
            'total_amount': float(self.total_amount),
            'payment_status': self.payment_status,
            'notes': self.notes,
            'supplier_name': self.supplier_name
        }
        
        if self.details:
            result['details'] = [
                {
                    'product_code': d.product_code,
                    'product_name': d.product_name,
                    'quantity': d.quantity,
                    'unit_price': float(d.unit_price),
                    'line_total': float(d.line_total)
                }
                for d in self.details
            ]
        
        return result


class PurchaseRepository:
    """
    Repository class for PURCHASE and PURCHASE_DETAIL table operations.
    Uses stored procedures for all database operations.
    
    Uses usp_CreatePurchase stored procedure for creating purchases,
    which handles transaction management and inventory updates.
    """
    
    @staticmethod
    def get_all() -> List[Purchase]:
        """
        Retrieve all purchases with supplier names.
        
        Returns:
            List of Purchase objects ordered by Purchase_Date DESC
        """
        rows = db.call_procedure_with_result('usp_ListPurchases', ())
        return [Purchase.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(purchase_no: str) -> Optional[Purchase]:
        """
        Retrieve a single purchase with its details.
        
        Args:
            purchase_no: Purchase number to look up
        
        Returns:
            Purchase object with details if found, None otherwise
        """
        # Get header
        rows = db.call_procedure_with_result('usp_GetPurchaseById', (purchase_no,))
        
        if not rows:
            return None
        
        purchase = Purchase.from_row(rows[0])
        
        # Get details
        detail_rows = db.call_procedure_with_result('usp_GetPurchaseDetails', (purchase_no,))
        purchase.details = [PurchaseDetail.from_row(r) for r in detail_rows]
        
        return purchase
    
    @staticmethod
    def get_by_supplier(supplier_id: str) -> List[Purchase]:
        """
        Retrieve all purchases from a specific supplier.
        
        Args:
            supplier_id: Supplier ID to filter by
        
        Returns:
            List of Purchase objects
        """
        rows = db.call_procedure_with_result('usp_GetPurchasesBySupplier', (supplier_id,))
        return [Purchase.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_date_range(start_date: date, end_date: date) -> List[Purchase]:
        """
        Retrieve purchases within a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
        
        Returns:
            List of Purchase objects
        """
        rows = db.call_procedure_with_result('usp_GetPurchasesByDateRange', (start_date, end_date))
        return [Purchase.from_row(row) for row in rows]
    
    @staticmethod
    def create_purchase(
        purchase_no: str,
        supplier_id: str,
        notes: Optional[str],
        details: List[Dict[str, Any]]
    ) -> db.ProcedureResult:
        """
        Create a new purchase order using the stored procedure.
        
        This calls usp_CreatePurchase which:
        1. Creates the PURCHASE header
        2. Creates all PURCHASE_DETAIL records
        3. Updates INVENTORY (increases stock)
        4. All within a transaction
        
        Args:
            purchase_no: Unique purchase order number
            supplier_id: Supplier ID
            notes: Optional notes
            details: List of dicts with Product_Code, Quantity, Unit_Price
        
        Returns:
            ProcedureResult with success status and any error message
        
        Example:
            result = PurchaseRepository.create_purchase(
                purchase_no='PUR002',
                supplier_id='SUP001',
                notes='Weekly restock',
                details=[
                    {'Product_Code': 'PRD001', 'Quantity': 10, 'Unit_Price': 25.00},
                    {'Product_Code': 'PRD002', 'Quantity': 20, 'Unit_Price': 12.00}
                ]
            )
        """
        return db.call_create_purchase(purchase_no, supplier_id, notes, details)
    
    @staticmethod
    def update_payment_status(purchase_no: str, status: str) -> bool:
        """
        Update the payment status of a purchase.
        
        Args:
            purchase_no: Purchase number to update
            status: New status ('Pending', 'Paid', 'Partial')
        
        Returns:
            True if updated successfully
        """
        try:
            return db.call_procedure('usp_UpdatePurchaseStatus', (
                purchase_no, status
            ), has_output=False)
        except Exception:
            return False
    
    @staticmethod
    def create_with_product(
        supplier_id: str,
        product_code: str,
        quantity: int,
        unit_price: Decimal,
        purchase_date: date = None,
        notes: str = None
    ) -> bool:
        """
        Create a simple purchase order with a single product (Pending status).
        Used when adding a new product with initial stock.
        
        The purchase is created with 'Pending' status. Inventory will be updated
        when the purchase is marked as 'Received' via mark_as_received().
        
        Args:
            supplier_id: Supplier ID
            product_code: Product code being purchased
            quantity: Number of units
            unit_price: Cost price per unit
            purchase_date: Date of purchase (default: today)
            notes: Optional notes
        
        Returns:
            True if created successfully
        """
        if purchase_date is None:
            purchase_date = date.today()
        
        # Generate purchase number
        purchase_no = PurchaseRepository.get_next_id()
        
        # Use usp_CreatePurchaseOrder which creates Pending purchase
        # (does NOT update inventory - that happens when marked Received)
        result = db.call_procedure_with_result('usp_CreatePurchaseOrder', (
            purchase_no,
            supplier_id,
            product_code,
            quantity,
            float(unit_price),
            notes
        ), commit=True)
        
        # Result returns [(1, 'PURxxx')] on success
        return result is not None and len(result) > 0 and result[0][0] == 1
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available purchase number using stored procedure.
        
        Returns:
            Next ID in format 'PUR###' (e.g., 'PUR002')
        """
        return db.call_procedure_scalar('usp_GetNextPurchaseNo', None, 'NextNo') or 'PUR001'
    
    @staticmethod
    def mark_as_received(purchase_no: str) -> tuple:
        """
        Mark a purchase as received and update inventory using stored procedure.
        
        Args:
            purchase_no: Purchase number to mark as received
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            result = db.call_procedure('usp_MarkPurchaseReceived', (purchase_no,), has_output=False)
            if result:
                return True, "Purchase marked as received. Inventory updated."
            else:
                return False, "Purchase not found or already received"
        except Exception as e:
            error_msg = str(e)
            if 'not found' in error_msg.lower():
                return False, "Purchase not found"
            elif 'already' in error_msg.lower():
                return False, "Purchase already marked as received"
            return False, f"Error: {error_msg}"
    
    @staticmethod
    def cancel_purchase(purchase_no: str) -> tuple:
        """
        Cancel a pending purchase order using stored procedure.
        Only pending purchases can be cancelled.
        
        Args:
            purchase_no: Purchase number to cancel
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            result = db.call_procedure('usp_CancelPurchase', (purchase_no,), has_output=False)
            if result:
                return True, "Purchase order cancelled successfully."
            else:
                return False, "Purchase not found or cannot be cancelled"
        except Exception as e:
            error_msg = str(e)
            if 'received' in error_msg.lower():
                return False, "Cannot cancel a received purchase"
            return False, f"Error: {error_msg}"
    
    @staticmethod
    def get_summary_by_supplier() -> List[Dict[str, Any]]:
        """
        Get purchase summary grouped by supplier using stored procedure.
        
        Returns:
            List of dicts with supplier info and total purchases
        """
        rows = db.call_procedure_with_result('usp_GetPurchaseSummaryBySupplier', ())
        return [
            {
                'supplier_id': row.Supplier_ID,
                'supplier_name': row.Supplier_Name,
                'purchase_count': getattr(row, 'Purchase_Count', 0) or 0,
                'total_value': float(getattr(row, 'Total_Value', 0) or 0)
            }
            for row in rows
        ]
