"""
=============================================================================
Payment Repository
=============================================================================
Provides data access methods for the PAYMENT table.
Uses stored procedures for all database operations.

Payments record money received against sales/invoices. Multiple payments
can be made against a single invoice (split payments).

Table Schema:
    PAYMENT(Payment_ID, Invoice_No, Payment_Method, Amount_Paid, Payment_Date)

Stored Procedures Used:
- usp_AddPayment: Create new payment
- usp_GetPaymentById: Get single payment
- usp_GetPaymentsBySale: Get payments for an invoice
- usp_ListPayments: List all payments
- usp_GetPaymentSummary: Get payment statistics

=============================================================================
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import db


@dataclass
class Payment:
    """
    Data class representing a payment.
    
    Attributes:
        payment_id: Unique payment identifier
        invoice_no: Invoice being paid (foreign key)
        payment_method: How payment was made ('Cash', 'Card', 'Mobile', etc.)
        amount_paid: Amount of payment
        payment_date: Date/time of payment
    """
    payment_id: str
    invoice_no: str
    payment_method: str
    amount_paid: Decimal
    payment_date: datetime
    
    @classmethod
    def from_row(cls, row) -> 'Payment':
        """Create a Payment instance from a database row."""
        return cls(
            payment_id=row.Payment_ID,
            invoice_no=row.Invoice_No,
            payment_method=row.Payment_Method,
            amount_paid=Decimal(str(row.Amount_Paid)),
            payment_date=row.Payment_Date
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'payment_id': self.payment_id,
            'invoice_no': self.invoice_no,
            'payment_method': self.payment_method,
            'amount_paid': float(self.amount_paid),
            'payment_date': str(self.payment_date)
        }


class PaymentRepository:
    """
    Repository class for PAYMENT table operations.
    Uses stored procedures for all database operations.
    """
    
    # Common payment methods
    PAYMENT_METHODS = ['Cash', 'Card', 'Mobile Payment', 'Bank Transfer', 'Check']
    
    @staticmethod
    def get_all(limit: int = 100) -> List[Payment]:
        """
        Retrieve recent payments.
        
        Args:
            limit: Maximum number of payments to return
        
        Returns:
            List of Payment objects ordered by Payment_Date DESC
        """
        rows = db.call_procedure_with_result('usp_ListPayments', (limit,))
        return [Payment.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(payment_id: str) -> Optional[Payment]:
        """
        Retrieve a single payment by ID.
        
        Args:
            payment_id: Payment ID to look up
        
        Returns:
            Payment object if found, None otherwise
        """
        rows = db.call_procedure_with_result('usp_GetPaymentById', (payment_id,))
        return Payment.from_row(rows[0]) if rows else None
    
    @staticmethod
    def get_by_invoice(invoice_no: str) -> List[Payment]:
        """
        Retrieve all payments for a specific invoice.
        
        Args:
            invoice_no: Invoice number to look up
        
        Returns:
            List of Payment objects for the invoice
        """
        rows = db.call_procedure_with_result('usp_GetPaymentsBySale', (invoice_no,))
        return [Payment.from_row(row) for row in rows]
    
    @staticmethod
    def get_total_paid(invoice_no: str) -> Decimal:
        """
        Get total amount paid against an invoice.
        
        Args:
            invoice_no: Invoice number
        
        Returns:
            Total amount paid
        """
        payments = PaymentRepository.get_by_invoice(invoice_no)
        return sum((p.amount_paid for p in payments), Decimal('0'))
    
    @staticmethod
    def get_balance_due(invoice_no: str) -> Decimal:
        """
        Get remaining balance due on an invoice.
        
        Args:
            invoice_no: Invoice number
        
        Returns:
            Balance due (invoice net amount - total payments)
        """
        # Get invoice total from sale
        sql = "EXEC usp_GetSaleById @InvoiceNo = ?"
        try:
            rows = db.call_procedure_with_result('usp_GetSaleById', (invoice_no,))
            if rows:
                net_amount = Decimal(str(rows[0].Net_Amount))
                total_paid = PaymentRepository.get_total_paid(invoice_no)
                return net_amount - total_paid
        except Exception:
            pass
        return Decimal('0')
    
    @staticmethod
    def create(
        payment_id: str,
        invoice_no: str,
        payment_method: str,
        amount_paid: Decimal,
        payment_date: datetime = None
    ) -> tuple[bool, str]:
        """
        Create a new payment record using stored procedure.
        
        Args:
            payment_id: Unique payment identifier
            invoice_no: Invoice being paid
            payment_method: Payment method used
            amount_paid: Amount of payment
            payment_date: Date/time of payment (default: now)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if payment_date is None:
            payment_date = datetime.now()
        
        try:
            result = db.call_procedure('usp_AddPayment', (
                payment_id,
                invoice_no,
                payment_method,
                float(amount_paid),
                payment_date
            ), has_output=False)
            
            if result:
                return True, "Payment recorded successfully"
            else:
                return False, "Failed to record payment"
        except Exception as e:
            error_msg = str(e)
            if 'invoice' in error_msg.lower() or 'not found' in error_msg.lower():
                return False, "Invoice not found"
            return False, f"Failed to record payment: {error_msg}"
    
    @staticmethod
    def delete(payment_id: str) -> tuple[bool, str]:
        """
        Delete a payment record.
        
        Args:
            payment_id: Payment ID to delete
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            result = db.call_procedure('usp_DeletePayment', (payment_id,), has_output=False)
            if result:
                return True, "Payment deleted successfully"
            else:
                return False, "Payment not found"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    @staticmethod
    def get_next_id() -> str:
        """
        Generate the next available payment ID.
        
        Returns:
            Next ID in format 'PAY###' (e.g., 'PAY001')
        """
        return db.call_procedure_scalar('usp_GetNextPaymentId', (), 'NextId')
    
    @staticmethod
    def get_payment_summary_by_method(start_date=None, end_date=None) -> List[Dict[str, Any]]:
        """
        Get payment totals grouped by payment method.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
        
        Returns:
            List of dicts with payment_method, count, and total
        """
        rows = db.call_procedure_with_result('usp_GetPaymentSummary', (start_date, end_date))
        return [
            {
                'payment_method': row.Payment_Method,
                'payment_count': getattr(row, 'Payment_Count', 0) or 0,
                'total_amount': float(getattr(row, 'Total_Amount', 0) or 0)
            }
            for row in rows
        ]
