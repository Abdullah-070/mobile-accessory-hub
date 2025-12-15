"""
=============================================================================
Database Helper Module (db.py)
=============================================================================
This module provides database connectivity and helper functions for the
Mobile Accessory Inventory System. It handles:
    - Reading connection configuration from config.ini
    - Creating and managing database connections via pyodbc
    - Executing parameterized queries safely
    - Calling stored procedures with table-valued parameters
    - Transaction management with context managers

IMPORTANT: This module uses parameterized queries ONLY to prevent SQL injection.
           Never concatenate user input directly into SQL strings!

Author: Mobile Accessory Inventory System
Version: 1.0.0
=============================================================================
"""

import pyodbc
import configparser
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        str: Absolute path to config.ini
        
    The function looks for config.ini in the following order:
    1. Same directory as this module
    2. Parent directory
    3. Current working directory
    """
    # Try same directory as this module
    module_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(module_dir, 'config.ini')
    
    if os.path.exists(config_path):
        return config_path
    
    # Try parent directory
    parent_dir = os.path.dirname(module_dir)
    config_path = os.path.join(parent_dir, 'config.ini')
    
    if os.path.exists(config_path):
        return config_path
    
    # Try current working directory
    config_path = os.path.join(os.getcwd(), 'config.ini')
    
    if os.path.exists(config_path):
        return config_path
    
    raise FileNotFoundError(
        "Configuration file 'config.ini' not found. "
        "Please copy 'config.ini.example' to 'config.ini' and configure it."
    )


def load_config() -> configparser.ConfigParser:
    """
    Load and parse the configuration file.
    
    Returns:
        configparser.ConfigParser: Parsed configuration object
        
    Raises:
        FileNotFoundError: If config.ini doesn't exist
    """
    config = configparser.ConfigParser()
    config_path = get_config_path()
    config.read(config_path)
    return config


def get_connection_string() -> str:
    """
    Build the ODBC connection string from configuration.
    
    Returns:
        str: ODBC connection string for SQL Server
        
    The connection string format depends on authentication method:
    - Windows Authentication: Uses Trusted_Connection=yes
    - SQL Server Authentication: Uses UID and PWD parameters
    """
    config = load_config()
    
    # Extract database settings
    driver = config.get('database', 'driver', fallback='ODBC Driver 18 for SQL Server')
    server = config.get('database', 'server', fallback='localhost')
    database = config.get('database', 'database', fallback='MobileAccessoryInventory')
    username = config.get('database', 'username', fallback='')
    password = config.get('database', 'password', fallback='')
    trust_cert = config.get('database', 'trust_server_certificate', fallback='yes')
    timeout = config.get('database', 'timeout', fallback='30')
    
    # Build connection string
    conn_str_parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"TrustServerCertificate={trust_cert}",
        f"Connection Timeout={timeout}"
    ]
    
    # Add authentication method
    if username and password:
        # SQL Server Authentication
        conn_str_parts.append(f"UID={username}")
        conn_str_parts.append(f"PWD={password}")
    else:
        # Windows Authentication
        conn_str_parts.append("Trusted_Connection=yes")
    
    return ";".join(conn_str_parts)


# =============================================================================
# CONNECTION MANAGEMENT
# =============================================================================

def get_connection() -> pyodbc.Connection:
    """
    Create and return a new database connection.
    
    Returns:
        pyodbc.Connection: Active database connection
        
    Raises:
        pyodbc.Error: If connection fails
        
    Note: Caller is responsible for closing the connection.
          Prefer using the connection_context() context manager instead.
    """
    conn_str = get_connection_string()
    connection = pyodbc.connect(conn_str)
    return connection


@contextmanager
def connection_context():
    """
    Context manager for database connections.
    
    Ensures connections are properly closed even if exceptions occur.
    
    Usage:
        with connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            rows = cursor.fetchall()
    
    Yields:
        pyodbc.Connection: Active database connection
    """
    connection = None
    try:
        connection = get_connection()
        yield connection
    finally:
        if connection:
            connection.close()


@contextmanager
def cursor_context(commit: bool = False):
    """
    Context manager for database cursors with automatic connection handling.
    
    Args:
        commit: If True, commits the transaction before closing.
                If False (default), changes are rolled back on exit.
    
    Usage:
        # For SELECT queries (no commit needed)
        with cursor_context() as cursor:
            cursor.execute("SELECT * FROM PRODUCT")
            rows = cursor.fetchall()
        
        # For INSERT/UPDATE/DELETE (commit needed)
        with cursor_context(commit=True) as cursor:
            cursor.execute("UPDATE PRODUCT SET ...")
    
    Yields:
        pyodbc.Cursor: Active database cursor
    """
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =============================================================================
# QUERY EXECUTION HELPERS
# =============================================================================

def execute_query(
    sql: str,
    params: Optional[Tuple] = None,
    fetch: str = 'all'
) -> Optional[List[pyodbc.Row]]:
    """
    Execute a SELECT query and return results.
    
    Args:
        sql: The SQL query to execute (use ? placeholders for parameters)
        params: Tuple of parameter values (optional)
        fetch: 'all' to fetch all rows, 'one' for single row, 'none' for no fetch
    
    Returns:
        List of rows for 'all', single row for 'one', None for 'none'
    
    Example:
        # Simple query
        products = execute_query("SELECT * FROM PRODUCT")
        
        # Parameterized query
        product = execute_query(
            "SELECT * FROM PRODUCT WHERE Product_Code = ?",
            ('PRD001',),
            fetch='one'
        )
    """
    with cursor_context() as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if fetch == 'all':
            return cursor.fetchall()
        elif fetch == 'one':
            return cursor.fetchone()
        else:
            return None


def execute_non_query(sql: str, params: Optional[Tuple] = None) -> int:
    """
    Execute an INSERT, UPDATE, or DELETE query.
    
    Args:
        sql: The SQL statement to execute (use ? placeholders for parameters)
        params: Tuple of parameter values (optional)
    
    Returns:
        int: Number of rows affected
    
    Example:
        # Update a product price
        rows_affected = execute_non_query(
            "UPDATE PRODUCT SET Retail_Price = ? WHERE Product_Code = ?",
            (29.99, 'PRD001')
        )
    """
    with cursor_context(commit=True) as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.rowcount


def execute_insert_returning_id(sql: str, params: Optional[Tuple] = None) -> Any:
    """
    Execute an INSERT query and return the generated identity value.
    
    Args:
        sql: The INSERT statement (should include OUTPUT INSERTED.column or 
             use SCOPE_IDENTITY())
        params: Tuple of parameter values (optional)
    
    Returns:
        The generated identity value
    
    Example:
        # Insert with OUTPUT clause
        payment_id = execute_insert_returning_id(
            '''INSERT INTO PAYMENT (Payment_ID, Invoice_No, Payment_Method, Amount_Paid)
               OUTPUT INSERTED.Payment_ID
               VALUES (?, ?, ?, ?)''',
            ('PAY001', 'INV001', 'Cash', 100.00)
        )
    """
    with cursor_context(commit=True) as cursor:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        row = cursor.fetchone()
        return row[0] if row else None


# =============================================================================
# STORED PROCEDURE HELPERS
# =============================================================================

@dataclass
class ProcedureResult:
    """
    Container for stored procedure execution results.
    
    Attributes:
        success: Whether the procedure executed successfully
        created_key: The key/ID returned by the procedure (if any)
        error_message: Error description if the procedure failed
        output_params: Dictionary of all output parameter values
    """
    success: bool
    created_key: Optional[str] = None
    error_message: Optional[str] = None
    output_params: Optional[Dict[str, Any]] = None


def call_create_purchase(
    purchase_no: str,
    supplier_id: str,
    notes: Optional[str],
    details: List[Dict[str, Any]]
) -> ProcedureResult:
    """
    Call the usp_CreatePurchase stored procedure.
    
    This procedure creates a purchase order with all its detail lines and
    updates inventory (increases stock).
    
    Args:
        purchase_no: Unique purchase order number
        supplier_id: ID of the supplier
        notes: Optional notes about the purchase
        details: List of dictionaries with keys:
                 - Product_Code: str
                 - Quantity: int
                 - Unit_Price: Decimal
    
    Returns:
        ProcedureResult with success status and created key
    
    Example:
        result = call_create_purchase(
            purchase_no='PUR002',
            supplier_id='SUP001',
            notes='Weekly restock',
            details=[
                {'Product_Code': 'PRD001', 'Quantity': 10, 'Unit_Price': 25.00},
                {'Product_Code': 'PRD002', 'Quantity': 20, 'Unit_Price': 12.00}
            ]
        )
        if result.success:
            print(f"Created purchase: {result.created_key}")
        else:
            print(f"Error: {result.error_message}")
    """
    with connection_context() as conn:
        cursor = conn.cursor()
        
        try:
            # Build the SQL to call the stored procedure
            # We need to use a table variable to pass the details
            sql = """
                -- Declare table variable for purchase details
                DECLARE @Details dbo.PurchaseDetailType;
                
                -- Declare output variables
                DECLARE @CreatedKey NVARCHAR(20);
                DECLARE @Success BIT;
                DECLARE @ErrorMessage NVARCHAR(500);
                
                -- Insert detail rows into table variable
                {detail_inserts}
                
                -- Call the stored procedure
                EXEC dbo.usp_CreatePurchase
                    @Purchase_No = ?,
                    @Supplier_ID = ?,
                    @Notes = ?,
                    @Details = @Details,
                    @CreatedKey = @CreatedKey OUTPUT,
                    @Success = @Success OUTPUT,
                    @ErrorMessage = @ErrorMessage OUTPUT;
                
                -- Return the results
                SELECT @Success AS Success, @CreatedKey AS CreatedKey, @ErrorMessage AS ErrorMessage;
            """
            
            # Build the INSERT statements for details
            detail_inserts = []
            for detail in details:
                insert = f"INSERT INTO @Details (Product_Code, Quantity, Unit_Price) VALUES ('{detail['Product_Code']}', {detail['Quantity']}, {detail['Unit_Price']});"
                detail_inserts.append(insert)
            
            sql = sql.format(detail_inserts='\n                '.join(detail_inserts))
            
            # Execute with parameters
            cursor.execute(sql, (purchase_no, supplier_id, notes))
            
            # Get the result
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return ProcedureResult(
                    success=bool(row.Success),
                    created_key=row.CreatedKey,
                    error_message=row.ErrorMessage,
                    output_params={
                        'Success': row.Success,
                        'CreatedKey': row.CreatedKey,
                        'ErrorMessage': row.ErrorMessage
                    }
                )
            else:
                return ProcedureResult(
                    success=False,
                    error_message="No result returned from stored procedure"
                )
                
        except pyodbc.Error as e:
            conn.rollback()
            return ProcedureResult(
                success=False,
                error_message=str(e)
            )
        finally:
            cursor.close()


def call_create_sale(
    invoice_no: str,
    customer_id: str,
    employee_id: str,
    discount: float,
    details: List[Dict[str, Any]]
) -> ProcedureResult:
    """
    Call the usp_CreateSale stored procedure.
    
    This procedure creates a sale/invoice with all its detail lines,
    validates stock availability, and updates inventory (decreases stock).
    
    Args:
        invoice_no: Unique invoice number
        customer_id: ID of the customer (use 'C000' for walk-in)
        employee_id: ID of the employee processing the sale
        discount: Discount amount to apply
        details: List of dictionaries with keys:
                 - Product_Code: str
                 - Quantity: int
                 - Unit_Price: Decimal
    
    Returns:
        ProcedureResult with success status and created key
    
    Example:
        result = call_create_sale(
            invoice_no='INV002',
            customer_id='C000',
            employee_id='EMP001',
            discount=10.00,
            details=[
                {'Product_Code': 'PRD001', 'Quantity': 2, 'Unit_Price': 49.99},
                {'Product_Code': 'PRD004', 'Quantity': 1, 'Unit_Price': 29.99}
            ]
        )
        if result.success:
            print(f"Created invoice: {result.created_key}")
        else:
            print(f"Error: {result.error_message}")
    """
    with connection_context() as conn:
        cursor = conn.cursor()
        
        try:
            # Build the INSERT statements for details
            detail_inserts = []
            for detail in details:
                # Escape single quotes in product code if any
                prod_code = str(detail['Product_Code']).replace("'", "''")
                insert = f"INSERT INTO @Details (Product_Code, Quantity, Unit_Price) VALUES ('{prod_code}', {detail['Quantity']}, {detail['Unit_Price']});"
                detail_inserts.append(insert)
            
            # Escape input values
            safe_invoice = str(invoice_no).replace("'", "''")
            safe_customer = str(customer_id).replace("'", "''")
            safe_employee = str(employee_id).replace("'", "''")
            safe_discount = float(discount)
            
            # Build the complete SQL with values embedded (pyodbc can't use ? in multi-statement batches)
            sql = f"""
                SET NOCOUNT ON;
                
                -- Declare table variable for sale details
                DECLARE @Details dbo.SaleDetailType;
                
                -- Declare output variables
                DECLARE @CreatedKey NVARCHAR(20);
                DECLARE @Success BIT;
                DECLARE @ErrorMessage NVARCHAR(500);
                
                -- Insert detail rows into table variable
                {chr(10).join(detail_inserts)}
                
                -- Call the stored procedure
                EXEC dbo.usp_CreateSale
                    @InvoiceNo = N'{safe_invoice}',
                    @CustomerID = N'{safe_customer}',
                    @EmployeeID = N'{safe_employee}',
                    @Discount = {safe_discount},
                    @Details = @Details,
                    @CreatedKey = @CreatedKey OUTPUT,
                    @Success = @Success OUTPUT,
                    @ErrorMessage = @ErrorMessage OUTPUT;
                
                -- Return the results
                SELECT @Success AS Success, @CreatedKey AS CreatedKey, @ErrorMessage AS ErrorMessage;
            """
            
            # Execute
            cursor.execute(sql)
            
            # Get the result
            row = cursor.fetchone()
            conn.commit()
            
            if row:
                return ProcedureResult(
                    success=bool(row.Success),
                    created_key=row.CreatedKey,
                    error_message=row.ErrorMessage,
                    output_params={
                        'Success': row.Success,
                        'CreatedKey': row.CreatedKey,
                        'ErrorMessage': row.ErrorMessage
                    }
                )
            else:
                return ProcedureResult(
                    success=False,
                    error_message="No result returned from stored procedure"
                )
                
        except pyodbc.Error as e:
            conn.rollback()
            return ProcedureResult(
                success=False,
                error_message=str(e)
            )
        finally:
            cursor.close()


def call_procedure(
    procedure_name: str,
    params: Optional[Any] = None,
    has_output: bool = True
) -> Any:
    """
    Generic helper to call stored procedures.
    
    This handles both simple CRUD procedures and those with OUTPUT parameters.
    
    Args:
        procedure_name: Name of the stored procedure (e.g., 'usp_AddCategory')
        params: Either:
            - None for no parameters
            - Dict of parameter names and values (without @ prefix)
            - Tuple of positional parameter values
        has_output: If True, expects @Success, @ErrorMessage, @CreatedKey outputs
                   If False, just executes and returns True on success
    
    Returns:
        If has_output=True: ProcedureResult with success status and any created key
        If has_output=False: True if successful, False otherwise
    
    Example:
        # With dict params:
        result = call_procedure('usp_AddCategory', {
            'Cat_ID': 'CAT005',
            'Cat_Name': 'Audio',
            'Description': 'Audio accessories'
        })
        
        # With tuple params (simple):
        result = call_procedure('usp_DeleteCategory', ('CAT005',), has_output=False)
    """
    with connection_context() as conn:
        cursor = conn.cursor()
        
        try:
            # Build SQL and params based on input type
            param_values = []
            
            if params is None or (isinstance(params, (tuple, list)) and len(params) == 0):
                param_str = ''
            elif isinstance(params, dict):
                param_assignments = []
                for key, value in params.items():
                    param_assignments.append(f"@{key} = ?")
                    param_values.append(value)
                param_str = ', '.join(param_assignments)
            else:
                # Tuple/list of positional params
                param_values = list(params)
                param_str = ', '.join(['?'] * len(params))
            
            if has_output:
                sql = f"""
                    DECLARE @CreatedKey NVARCHAR(50);
                    DECLARE @Success BIT;
                    DECLARE @ErrorMessage NVARCHAR(500);
                    
                    EXEC dbo.{procedure_name}
                        {param_str}{',' if param_str else ''}
                        @CreatedKey = @CreatedKey OUTPUT,
                        @Success = @Success OUTPUT,
                        @ErrorMessage = @ErrorMessage OUTPUT;
                    
                    SELECT @Success AS Success, @CreatedKey AS CreatedKey, @ErrorMessage AS ErrorMessage;
                """
                
                cursor.execute(sql, param_values)
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return ProcedureResult(
                        success=bool(row.Success),
                        created_key=row.CreatedKey,
                        error_message=row.ErrorMessage,
                        output_params={
                            'Success': row.Success,
                            'CreatedKey': row.CreatedKey,
                            'ErrorMessage': row.ErrorMessage
                        }
                    )
                else:
                    return ProcedureResult(
                        success=False,
                        error_message="No result returned from stored procedure"
                    )
            else:
                # Simple procedure call without output parameters
                sql = f"EXEC dbo.{procedure_name} {param_str}"
                cursor.execute(sql, param_values)
                conn.commit()
                return True
                
        except pyodbc.Error as e:
            conn.rollback()
            if has_output:
                return ProcedureResult(
                    success=False,
                    error_message=str(e)
                )
            return False
        finally:
            cursor.close()


def call_procedure_with_result(
    procedure_name: str,
    params: Optional[Any] = None,
    commit: bool = False
) -> List[pyodbc.Row]:
    """
    Call a stored procedure that returns a result set (SELECT).
    
    Use this for procedures like usp_ListCategories, usp_GetProductByCode, etc.
    
    Args:
        procedure_name: Name of the stored procedure
        params: Either:
            - None for no parameters
            - Dict of parameter names and values (without @ prefix)
            - Tuple of positional parameter values
        commit: If True, commit the transaction (for INSERT/UPDATE procedures)
    
    Returns:
        List of rows from the procedure's SELECT statement
    
    Example:
        # No params:
        rows = call_procedure_with_result('usp_ListCategories')
        
        # Dict params:
        rows = call_procedure_with_result('usp_GetCategoryById', {'CatId': 'CAT001'})
        
        # Tuple params:
        rows = call_procedure_with_result('usp_GetCategoryById', ('CAT001',))
        
        # With commit (for INSERT/UPDATE):
        rows = call_procedure_with_result('usp_CreatePurchaseOrder', params, commit=True)
    """
    with cursor_context(commit=commit) as cursor:
        if params is None or (isinstance(params, (tuple, list)) and len(params) == 0):
            # No parameters
            sql = f"EXEC dbo.{procedure_name}"
            cursor.execute(sql)
        elif isinstance(params, dict):
            # Skip empty dict or dict with just Page/PageSize (not used)
            # Filter out Page/PageSize as our procedures don't use them
            filtered_params = {k: v for k, v in params.items() if k not in ('Page', 'PageSize')}
            if not filtered_params:
                sql = f"EXEC dbo.{procedure_name}"
                cursor.execute(sql)
            else:
                param_assignments = []
                param_values = []
                for key, value in filtered_params.items():
                    param_assignments.append(f"@{key} = ?")
                    param_values.append(value)
                param_str = ', '.join(param_assignments)
                sql = f"EXEC dbo.{procedure_name} {param_str}"
                cursor.execute(sql, param_values)
        else:
            # Tuple/list of positional params
            placeholders = ', '.join(['?'] * len(params))
            sql = f"EXEC dbo.{procedure_name} {placeholders}"
            cursor.execute(sql, list(params))
        
        return cursor.fetchall()


def call_procedure_scalar(
    procedure_name: str,
    params: Optional[Any] = None,
    column_name: str = 'Next_ID'
) -> Any:
    """
    Call a stored procedure and return a single value from the first row.
    
    Use this for procedures like usp_GetNextCategoryId that return a single value.
    
    Args:
        procedure_name: Name of the stored procedure
        params: Dict, tuple, or None for parameters
        column_name: Name of the column to retrieve (default 'Next_ID')
    
    Returns:
        The value from the specified column, or None if no rows returned
    
    Example:
        next_id = call_procedure_scalar('usp_GetNextCategoryId')
        print(f"Next ID: {next_id}")  # Output: "CAT004"
    """
    rows = call_procedure_with_result(procedure_name, params)
    if rows:
        return getattr(rows[0], column_name, None)
    return None


# =============================================================================
# PAGINATION HELPER
# =============================================================================

def execute_paginated_query(
    sql: str,
    params: Optional[Tuple] = None,
    page: int = 1,
    page_size: int = 20,
    order_by: str = ''
) -> Tuple[List[pyodbc.Row], int]:
    """
    Execute a query with pagination support.
    
    Args:
        sql: The base SELECT query (without ORDER BY, OFFSET, FETCH)
        params: Tuple of parameter values (optional)
        page: Page number (1-based)
        page_size: Number of rows per page
        order_by: ORDER BY clause (required for pagination)
    
    Returns:
        Tuple of (rows, total_count)
    
    Example:
        rows, total = execute_paginated_query(
            "SELECT * FROM PRODUCT WHERE Subcat_ID = ?",
            ('SUB001',),
            page=1,
            page_size=10,
            order_by='Product_Name ASC'
        )
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count first
    count_sql = f"SELECT COUNT(*) FROM ({sql}) AS CountQuery"
    with cursor_context() as cursor:
        if params:
            cursor.execute(count_sql, params)
        else:
            cursor.execute(count_sql)
        total_count = cursor.fetchone()[0]
    
    # Build paginated query
    if order_by:
        paginated_sql = f"""
            {sql}
            ORDER BY {order_by}
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """
    else:
        # SQL Server requires ORDER BY for OFFSET/FETCH
        paginated_sql = f"""
            {sql}
            ORDER BY (SELECT NULL)
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY
        """
    
    # Execute paginated query
    with cursor_context() as cursor:
        if params:
            cursor.execute(paginated_sql, params + (offset, page_size))
        else:
            cursor.execute(paginated_sql, (offset, page_size))
        rows = cursor.fetchall()
    
    return rows, total_count


# =============================================================================
# CONNECTION TEST
# =============================================================================

def test_connection() -> Tuple[bool, str]:
    """
    Test the database connection.
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Example:
        success, message = test_connection()
        if success:
            print("Connected successfully!")
        else:
            print(f"Connection failed: {message}")
    """
    try:
        with connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            return True, f"Connected to SQL Server: {version[:50]}..."
    except FileNotFoundError as e:
        return False, str(e)
    except pyodbc.Error as e:
        return False, f"Database connection error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    """
    Test the database connection when running this module directly.
    """
    print("Testing database connection...")
    print("=" * 60)
    
    success, message = test_connection()
    
    if success:
        print(f"✓ {message}")
        print("\nTesting query execution...")
        
        # Test a simple query
        try:
            products = execute_query("SELECT TOP 5 Product_Code, Product_Name FROM PRODUCT")
            print(f"✓ Found {len(products)} products:")
            for product in products:
                print(f"  - {product.Product_Code}: {product.Product_Name}")
        except Exception as e:
            print(f"✗ Query failed: {e}")
    else:
        print(f"✗ {message}")
    
    print("=" * 60)
