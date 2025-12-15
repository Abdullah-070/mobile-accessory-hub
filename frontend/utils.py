"""
=============================================================================
Utility Functions Module (utils.py)
=============================================================================
This module provides common utility functions used throughout the application:
    - Data validation (phone, email, currency, etc.)
    - Formatting functions (currency, dates, etc.)
    - Helper functions for UI operations

=============================================================================
"""

import re
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, time
from typing import Optional, Union, Tuple


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def is_valid_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format, False otherwise
    
    Example:
        >>> is_valid_email('user@example.com')
        True
        >>> is_valid_email('invalid-email')
        False
    """
    if not email:
        return True  # Empty is valid (optional field)
    
    # Simple email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Validate a phone number format.
    
    Accepts various formats including:
    - +1-555-0100
    - (555) 555-5555
    - 555-555-5555
    - 5555555555
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid phone format, False otherwise
    """
    if not phone:
        return True  # Empty is valid (optional field)
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone)
    
    # Check if remaining characters are digits and length is reasonable
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def is_valid_decimal(value: str, min_value: float = None, max_value: float = None) -> bool:
    """
    Validate a decimal/currency value.
    
    Args:
        value: String value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
    
    Returns:
        True if valid decimal within range, False otherwise
    """
    try:
        decimal_value = Decimal(value)
        
        if min_value is not None and decimal_value < Decimal(str(min_value)):
            return False
        
        if max_value is not None and decimal_value > Decimal(str(max_value)):
            return False
        
        return True
    except (InvalidOperation, ValueError):
        return False


def is_valid_integer(value: str, min_value: int = None, max_value: int = None) -> bool:
    """
    Validate an integer value.
    
    Args:
        value: String value to validate
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
    
    Returns:
        True if valid integer within range, False otherwise
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False
        
        if max_value is not None and int_value > max_value:
            return False
        
        return True
    except ValueError:
        return False


def is_not_empty(value: str) -> bool:
    """
    Check if a string value is not empty or whitespace only.
    
    Args:
        value: String to check
    
    Returns:
        True if value contains non-whitespace characters
    """
    return bool(value and value.strip())


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================

def format_currency(
    amount: Union[Decimal, float, int, str],
    symbol: str = 'Rs. ',
    decimal_places: int = 2
) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: Amount to format
        symbol: Currency symbol (default: 'Rs. ')
        decimal_places: Number of decimal places (default: 2)
    
    Returns:
        Formatted currency string
    
    Example:
        >>> format_currency(1234.5)
        'Rs. 1,234.50'
        >>> format_currency(1234.5, '€')
        '€1,234.50'
    """
    try:
        if isinstance(amount, str):
            amount = Decimal(amount)
        elif isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        # Format with thousands separator and decimal places
        formatted = f"{float(amount):,.{decimal_places}f}"
        return f"{symbol}{formatted}"
    except (InvalidOperation, ValueError):
        return f"{symbol}0.00"


def format_date(
    value: Union[date, datetime, str],
    format_str: str = '%Y-%m-%d'
) -> str:
    """
    Format a date value.
    
    Args:
        value: Date to format
        format_str: Output format string (default: 'YYYY-MM-DD')
    
    Returns:
        Formatted date string
    
    Example:
        >>> format_date(date(2024, 1, 15))
        '2024-01-15'
        >>> format_date(date(2024, 1, 15), '%d/%m/%Y')
        '15/01/2024'
    """
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return value
    
    if isinstance(value, datetime):
        value = value.date()
    
    if isinstance(value, date):
        return value.strftime(format_str)
    
    return str(value)


def format_datetime(
    value: Union[datetime, str],
    format_str: str = '%Y-%m-%d %H:%M:%S'
) -> str:
    """
    Format a datetime value.
    
    Args:
        value: Datetime to format
        format_str: Output format string
    
    Returns:
        Formatted datetime string
    """
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return value
    
    if isinstance(value, datetime):
        return value.strftime(format_str)
    
    return str(value)


def format_time(value: Union[time, datetime, str], format_str: str = '%H:%M') -> str:
    """
    Format a time value.
    
    Args:
        value: Time to format
        format_str: Output format string (default: 'HH:MM')
    
    Returns:
        Formatted time string
    """
    if isinstance(value, str):
        return value
    
    if isinstance(value, datetime):
        value = value.time()
    
    if isinstance(value, time):
        return value.strftime(format_str)
    
    return str(value)


def format_quantity(value: int, singular: str = 'item', plural: str = None) -> str:
    """
    Format a quantity with appropriate singular/plural label.
    
    Args:
        value: Quantity value
        singular: Singular form label
        plural: Plural form label (default: singular + 's')
    
    Returns:
        Formatted quantity string
    
    Example:
        >>> format_quantity(1, 'product')
        '1 product'
        >>> format_quantity(5, 'product')
        '5 products'
    """
    if plural is None:
        plural = singular + 's'
    
    label = singular if value == 1 else plural
    return f"{value:,} {label}"


def format_percentage(value: Union[float, Decimal], decimal_places: int = 1) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: Value to format (0.5 = 50%)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    try:
        percentage = float(value) * 100
        return f"{percentage:.{decimal_places}f}%"
    except (TypeError, ValueError):
        return "0.0%"


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def parse_currency(value: str) -> Optional[Decimal]:
    """
    Parse a currency string to Decimal.
    
    Args:
        value: Currency string (e.g., '$1,234.50')
    
    Returns:
        Decimal value or None if parsing fails
    """
    if not value:
        return None
    
    try:
        # Remove currency symbols and thousands separators
        cleaned = re.sub(r'[^\d.-]', '', value)
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_integer(value: str) -> Optional[int]:
    """
    Parse a string to integer.
    
    Args:
        value: String value
    
    Returns:
        Integer value or None if parsing fails
    """
    if not value:
        return None
    
    try:
        # Remove any non-digit characters except minus sign
        cleaned = re.sub(r'[^\d-]', '', value)
        return int(cleaned)
    except ValueError:
        return None


# =============================================================================
# ID GENERATION HELPERS
# =============================================================================

def generate_id(prefix: str, number: int, width: int = 3) -> str:
    """
    Generate a formatted ID string.
    
    Args:
        prefix: ID prefix (e.g., 'PRD', 'INV')
        number: Numeric part
        width: Minimum width of numeric part (default: 3)
    
    Returns:
        Formatted ID string
    
    Example:
        >>> generate_id('PRD', 5)
        'PRD005'
        >>> generate_id('INV', 123, 4)
        'INV0123'
    """
    return f"{prefix}{number:0{width}d}"


def parse_id_number(id_string: str, prefix: str) -> Optional[int]:
    """
    Extract the numeric part from an ID string.
    
    Args:
        id_string: Full ID string (e.g., 'PRD005')
        prefix: Expected prefix
    
    Returns:
        Numeric part as integer, or None if parsing fails
    """
    if not id_string or not id_string.startswith(prefix):
        return None
    
    try:
        return int(id_string[len(prefix):])
    except ValueError:
        return None


# =============================================================================
# STRING HELPERS
# =============================================================================

def truncate_string(value: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        value: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated (default: '...')
    
    Returns:
        Truncated string
    """
    if not value or len(value) <= max_length:
        return value or ''
    
    return value[:max_length - len(suffix)] + suffix


def title_case(value: str) -> str:
    """
    Convert string to title case, handling common abbreviations.
    
    Args:
        value: String to convert
    
    Returns:
        Title-cased string
    """
    if not value:
        return ''
    
    # Words that should remain uppercase
    uppercase_words = {'ID', 'USB', 'LED', 'LCD', 'HD', 'SD'}
    
    words = value.split()
    result = []
    
    for word in words:
        upper = word.upper()
        if upper in uppercase_words:
            result.append(upper)
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)


# =============================================================================
# VALIDATION RESULT CLASS
# =============================================================================

class ValidationResult:
    """
    Class to hold validation results with error messages.
    
    Usage:
        result = ValidationResult()
        if not is_not_empty(name):
            result.add_error('name', 'Name is required')
        if not result.is_valid:
            for field, message in result.errors:
                print(f"{field}: {message}")
    """
    
    def __init__(self):
        """Initialize an empty validation result."""
        self._errors: list[Tuple[str, str]] = []
    
    def add_error(self, field: str, message: str):
        """
        Add a validation error.
        
        Args:
            field: Field name that failed validation
            message: Error message
        """
        self._errors.append((field, message))
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self._errors) == 0
    
    @property
    def errors(self) -> list[Tuple[str, str]]:
        """Get list of (field, message) tuples."""
        return self._errors
    
    @property
    def error_messages(self) -> list[str]:
        """Get list of error messages only."""
        return [msg for _, msg in self._errors]
    
    @property
    def first_error(self) -> Optional[str]:
        """Get the first error message, or None if valid."""
        return self._errors[0][1] if self._errors else None
    
    def get_field_error(self, field: str) -> Optional[str]:
        """
        Get error message for a specific field.
        
        Args:
            field: Field name to check
        
        Returns:
            Error message or None if no error for this field
        """
        for f, msg in self._errors:
            if f == field:
                return msg
        return None


# =============================================================================
# ERROR REPORTING FUNCTIONS
# =============================================================================

import logging
import traceback
import os
from pathlib import Path

# Set up logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app_errors.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
    ]
)

_logger = logging.getLogger("MobileAccessoryInventory")


def log_info(message: str) -> None:
    """Log an informational message."""
    _logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    _logger.warning(message)


def log_error(message: str, exc: Exception = None) -> None:
    """Log an error message with optional exception."""
    if exc:
        _logger.error(f"{message}: {str(exc)}\n{traceback.format_exc()}")
    else:
        _logger.error(message)


def log_debug(message: str) -> None:
    """Log a debug message."""
    _logger.debug(message)


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """Test utility functions when running this module directly."""
    
    print("Testing utility functions...")
    print("=" * 60)
    
    # Test currency formatting
    print("\nCurrency formatting:")
    print(f"  format_currency(1234.5) = {format_currency(1234.5)}")
    print(f"  format_currency(1234.5, '€') = {format_currency(1234.5, '€')}")
    
    # Test validation
    print("\nValidation:")
    print(f"  is_valid_email('test@example.com') = {is_valid_email('test@example.com')}")
    print(f"  is_valid_email('invalid') = {is_valid_email('invalid')}")
    print(f"  is_valid_phone('+1-555-0100') = {is_valid_phone('+1-555-0100')}")
    
    # Test ID generation
    print("\nID generation:")
    print(f"  generate_id('PRD', 5) = {generate_id('PRD', 5)}")
    print(f"  generate_id('INV', 123, 4) = {generate_id('INV', 123, 4)}")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
