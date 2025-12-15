"""
=============================================================================
Sale Repository
=============================================================================
Provides data access methods for the SALE and SALE_DETAIL tables.
Uses stored procedures for all database operations.

Sales represent transactions with customers. Creating a sale automatically
validates stock and updates inventory via the usp_CreateSale stored procedure.

Table Schemas:
    SALE(Invoice_No, Customer_ID, Employee_ID, Sale_Date, Sale_Time, 
         Total_Amount, Discount, Net_Amount)
    SALE_DETAIL(Invoice_No, Product_Code, Quantity, Unit_Price, Line_Total)

Stored Procedures Used:
- usp_CreateSale: Create sale with items (via db.call_create_sale)
- usp_GetSaleById: Get single sale
- usp_ListSales: List all sales
- usp_GetSalesByCustomer: Get sales by customer
- usp_GetSalesByEmployee: Get sales by employee
- usp_GetSalesByDateRange: Get sales in date range
- usp_GetSaleDetails: Get sale line items
- usp_GetNextInvoiceNo: Generate next invoice number
- usp_GetDailySalesSummary: Get daily sales summary
- usp_GetTopSellingProducts: Get best sellers
- usp_GetSalesByCategory: Get sales grouped by category

=============================================================================
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal
import db


@dataclass
class SaleDetail:
    """
    Data class representing a sale line item.
    
    Attributes:
        invoice_no: Parent invoice number
        product_code: Product sold
        quantity: Number of units sold
        unit_price: Price per unit
        line_total: quantity * unit_price
        product_name: Product name (joined)
    """
    invoice_no: str
    product_code: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    product_name: Optional[str] = None
    
    @classmethod
    def from_row(cls, row) -> 'SaleDetail':
        """Create a SaleDetail instance from a database row."""
        return cls(
            invoice_no=row.Invoice_No,
            product_code=row.Product_Code,
            quantity=row.Quantity,
            unit_price=Decimal(str(row.Unit_Price)),
            line_total=Decimal(str(row.Line_Total)),
            product_name=getattr(row, 'Product_Name', None)
        )


@dataclass
class Sale:
    """
    Data class representing a sale/invoice.
    
    Attributes:
        invoice_no: Unique invoice number
        customer_id: Customer ID (foreign key)
        employee_id: Employee who processed sale (foreign key)
        sale_date: Date of sale
        sale_time: Time of sale
        total_amount: Sum of all line totals before discount
        discount: Discount amount applied
        net_amount: total_amount - discount
        customer_name: Customer name (joined)
        employee_name: Employee name (joined)
        details: List of line items
    """
    invoice_no: str
    customer_id: str
    employee_id: str
    sale_date: date
    sale_time: time
    total_amount: Decimal
    discount: Decimal
    net_amount: Decimal
    customer_name: Optional[str] = None
    employee_name: Optional[str] = None
    details: Optional[List[SaleDetail]] = None
    
    @classmethod
    def from_row(cls, row) -> 'Sale':
        """Create a Sale instance from a database row."""
        return cls(
            invoice_no=row.Invoice_No,
            customer_id=row.Customer_ID,
            employee_id=row.Employee_ID,
            sale_date=row.Sale_Date,
            sale_time=row.Sale_Time,
            total_amount=Decimal(str(row.Total_Amount)),
            discount=Decimal(str(row.Discount)),
            net_amount=Decimal(str(row.Net_Amount)),
            customer_name=getattr(row, 'Customer_Name', None),
            employee_name=getattr(row, 'Employee_Name', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'invoice_no': self.invoice_no,
            'customer_id': self.customer_id,
            'employee_id': self.employee_id,
            'sale_date': str(self.sale_date),
            'sale_time': str(self.sale_time),
            'total_amount': float(self.total_amount),
            'discount': float(self.discount),
            'net_amount': float(self.net_amount),
            'customer_name': self.customer_name,
            'employee_name': self.employee_name
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


class SaleRepository:
    """
    Repository class for SALE and SALE_DETAIL table operations.
    Uses stored procedures for all database operations.
    
    Uses usp_CreateSale stored procedure for creating sales,
    which handles stock validation, transaction management, and inventory updates.
    """
    
    @staticmethod
    def get_all(limit: int = 100) -> List[Sale]:
        """
        Retrieve recent sales with customer and employee names.
        
        Args:
            limit: Maximum number of sales to return (default: 100)
        
        Returns:
            List of Sale objects ordered by Sale_Date DESC
        """
        rows = db.call_procedure_with_result('usp_ListSales', (limit,))
        return [Sale.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(invoice_no: str) -> Optional[Sale]:
        """
        Retrieve a single sale with its details.
        
        Args:
            invoice_no: Invoice number to look up
        
        Returns:
            Sale object with details if found, None otherwise
        """
        # Get header
        rows = db.call_procedure_with_result('usp_GetSaleById', (invoice_no,))
        
        if not rows:
            return None
        
        sale = Sale.from_row(rows[0])
        
        # Get details
        detail_rows = db.call_procedure_with_result('usp_GetSaleDetails', (invoice_no,))
        sale.details = [SaleDetail.from_row(r) for r in detail_rows]
        
        return sale
    
    @staticmethod
    def get_by_customer(customer_id: str) -> List[Sale]:
        """
        Retrieve all sales for a specific customer.
        
        Args:
            customer_id: Customer ID to filter by
        
        Returns:
            List of Sale objects
        """
        rows = db.call_procedure_with_result('usp_GetSalesByCustomer', (customer_id,))
        return [Sale.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_employee(employee_id: str) -> List[Sale]:
        """
        Retrieve all sales processed by a specific employee.
        
        Args:
            employee_id: Employee ID to filter by
        
        Returns:
            List of Sale objects
        """
        rows = db.call_procedure_with_result('usp_GetSalesByEmployee', (employee_id,))
        return [Sale.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_date_range(start_date: date, end_date: date) -> List[Sale]:
        """
        Retrieve sales within a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
        
        Returns:
            List of Sale objects
        """
        rows = db.call_procedure_with_result('usp_GetSalesByDateRange', (start_date, end_date))
        return [Sale.from_row(row) for row in rows]
    
    @staticmethod
    def get_today_sales() -> List[Sale]:
        """
        Retrieve all sales from today.
        
        Returns:
            List of Sale objects from today
        """
        today = date.today()
        return SaleRepository.get_by_date_range(today, today)
    
    @staticmethod
    def create_sale(
        invoice_no: str,
        customer_id: str,
        employee_id: str,
        discount: float,
        details: List[Dict[str, Any]]
    ) -> db.ProcedureResult:
        """
        Create a new sale using the stored procedure.
        
        This calls usp_CreateSale which:
        1. Validates sufficient stock for all items
        2. Creates the SALE header
        3. Creates all SALE_DETAIL records
        4. Updates INVENTORY (decreases stock)
        5. All within a transaction
        
        Args:
            invoice_no: Unique invoice number
            customer_id: Customer ID (use 'C000' for walk-in)
            employee_id: Employee processing the sale
            discount: Discount amount
            details: List of dicts with Product_Code, Quantity, Unit_Price
        
        Returns:
            ProcedureResult with success status and any error message
        
        Example:
            result = SaleRepository.create_sale(
                invoice_no='INV002',
                customer_id='C000',
                employee_id='EMP001',
                discount=10.00,
                details=[
                    {'Product_Code': 'PRD001', 'Quantity': 2, 'Unit_Price': 49.99},
                    {'Product_Code': 'PRD004', 'Quantity': 1, 'Unit_Price': 29.99}
                ]
            )
        """
        return db.call_create_sale(invoice_no, customer_id, employee_id, discount, details)
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available invoice number using stored procedure.
        
        Returns:
            Next ID in format 'INV###' (e.g., 'INV002')
        """
        return db.call_procedure_scalar('usp_GetNextInvoiceNo', (), 'NextNo')
    
    @staticmethod
    def get_daily_summary(target_date: date = None) -> Dict[str, Any]:
        """
        Get sales summary for a specific date using stored procedure.
        
        Args:
            target_date: Date to summarize (default: today)
        
        Returns:
            Dict with total_sales, total_revenue, total_discount, etc.
        """
        if target_date is None:
            target_date = date.today()
        
        rows = db.call_procedure_with_result('usp_GetDailySalesSummary', (target_date,))
        
        if rows:
            row = rows[0]
            return {
                'date': str(target_date),
                'total_sales': getattr(row, 'Total_Sales', 0) or 0,
                'gross_revenue': float(getattr(row, 'Gross_Revenue', 0) or 0),
                'total_discount': float(getattr(row, 'Total_Discount', 0) or 0),
                'net_revenue': float(getattr(row, 'Net_Revenue', 0) or 0)
            }
        return {
            'date': str(target_date),
            'total_sales': 0,
            'gross_revenue': 0.0,
            'total_discount': 0.0,
            'net_revenue': 0.0
        }
    
    @staticmethod
    def get_top_selling_products(limit: int = 10, start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """
        Get top selling products by quantity using stored procedure.
        
        Args:
            limit: Number of products to return
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of dicts with product info and total quantity sold
        """
        rows = db.call_procedure_with_result('usp_GetTopSellingProducts', (limit, start_date, end_date))
        return [
            {
                'product_code': row.Product_Code,
                'product_name': row.Product_Name,
                'brand': getattr(row, 'Brand', None),
                'total_quantity': getattr(row, 'Total_Quantity', 0) or 0,
                'total_revenue': float(getattr(row, 'Total_Revenue', 0) or 0)
            }
            for row in rows
        ]
    
    @staticmethod
    def get_sales_by_category(start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """
        Get sales summary grouped by category using stored procedure.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of dicts with category info and totals
        """
        rows = db.call_procedure_with_result('usp_GetSalesByCategory', (start_date, end_date))
        return [
            {
                'cat_id': row.Cat_ID,
                'cat_name': row.Cat_Name,
                'sale_count': getattr(row, 'Sale_Count', 0) or 0,
                'total_quantity': getattr(row, 'Total_Quantity', 0) or 0,
                'total_revenue': float(getattr(row, 'Total_Revenue', 0) or 0)
            }
            for row in rows
        ]
    
    @staticmethod
    def get_sales_report(start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get comprehensive sales report with profit calculations using stored procedure.
        
        The usp_GetSalesReport procedure returns multiple result sets:
        1. Summary totals (Total_Sales, Total_Units_Sold, Total_Revenue, Total_Cost, Gross_Profit)
        2. Daily breakdown
        3. Top selling products
        4. Sales by category
        
        Args:
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Dict with summary, daily_breakdown, top_products, category_sales
        """
        # For now, we call the procedure and get the first result set (summary)
        rows = db.call_procedure_with_result('usp_GetSalesReport', (start_date, end_date))
        
        summary = {
            'total_sales': 0,
            'total_units_sold': 0,
            'total_revenue': 0.0,
            'total_cost': 0.0,
            'gross_profit': 0.0
        }
        
        if rows:
            row = rows[0]
            summary = {
                'total_sales': getattr(row, 'Total_Sales', 0) or 0,
                'total_units_sold': getattr(row, 'Total_Units_Sold', 0) or 0,
                'total_revenue': float(getattr(row, 'Total_Revenue', 0) or 0),
                'total_cost': float(getattr(row, 'Total_Cost', 0) or 0),
                'gross_profit': float(getattr(row, 'Gross_Profit', 0) or 0)
            }
        
        return summary
