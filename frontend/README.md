# Mobile Accessory Inventory Management System

A professional desktop application for managing mobile accessory retail inventory, built with Python and PySide6.

## Features

- **User Authentication**: Secure login with bcrypt password hashing
- **Role-Based Access**: Admin and Employee roles with different permissions
- **Dashboard**: At-a-glance view of sales, inventory, and alerts
- **Point of Sale (POS)**: Fast, cashier-friendly sales interface with barcode scanning
- **Product Management**: Full CRUD for products with categories and subcategories
- **Inventory Tracking**: Real-time stock levels with low-stock alerts
- **Customer Management**: Track customer information for sales
- **Supplier Management**: Manage supplier information and purchases
- **Purchase Orders**: Record inventory purchases from suppliers
- **Reports**: Sales and inventory reports (Admin only)

## Screenshots

(Screenshots would go here)

## Requirements

### Software Requirements

- **Python**: 3.10 or higher
- **Microsoft SQL Server**: 2019 or higher
- **ODBC Driver**: Microsoft ODBC Driver 18 for SQL Server

### Python Dependencies

```
PySide6>=6.5.0
pyodbc>=4.0.39
passlib[bcrypt]>=1.7.4
```

## Installation

### Step 1: Install SQL Server

1. Download and install [SQL Server 2022 Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
2. Install [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)

### Step 2: Install ODBC Driver

1. Download [Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Run the installer and follow the prompts

### Step 3: Create the Database

1. Open SQL Server Management Studio (SSMS)
2. Connect to your SQL Server instance
3. Open the `MobileAccessoryInventory.sql` file
4. Execute the entire script to create the database, tables, and sample data

### Step 4: Set Up Python Environment

```bash
# Navigate to the frontend directory
cd "d:\database project\frontend"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Database Connection

1. Copy `config.ini.example` to `config.ini`
2. Edit `config.ini` with your database connection settings:

```ini
[database]
server = YOUR_SERVER_NAME
database = MobileAccessoryInventory
driver = ODBC Driver 18 for SQL Server
trusted_connection = yes
```

For SQL Server Express with default instance:
```ini
server = localhost\SQLEXPRESS
```

For SQL Server Authentication (instead of Windows Authentication):
```ini
trusted_connection = no
username = your_username
password = your_password
```

## Running the Application

```bash
# Make sure virtual environment is activated
cd "d:\database project\frontend"
venv\Scripts\activate

# Run the application
python main.py
```

## Default Login Credentials

After running the SQL script, you can log in with these credentials:

| Username | Password  | Role     |
|----------|-----------|----------|
| admin    | admin123  | Admin    |
| john.doe | pass123   | Employee |

**Important**: Change these passwords after first login in a production environment!

## Project Structure

```
database project/
├── MobileAccessoryInventory.sql    # Database schema and seed data
└── frontend/
    ├── main.py                     # Application entry point
    ├── requirements.txt            # Python dependencies
    ├── config.ini                  # Database configuration
    ├── config.ini.example          # Example configuration
    ├── db.py                       # Database connection helper
    ├── utils.py                    # Utility functions
    ├── repositories/               # Data access layer
    │   ├── __init__.py
    │   ├── category_repository.py
    │   ├── subcategory_repository.py
    │   ├── product_repository.py
    │   ├── inventory_repository.py
    │   ├── supplier_repository.py
    │   ├── customer_repository.py
    │   ├── employee_repository.py
    │   ├── purchase_repository.py
    │   ├── sale_repository.py
    │   └── payment_repository.py
    ├── styles/
    │   └── theme.qss               # Qt stylesheet
    └── views/                      # UI screens
        ├── __init__.py
        ├── login_view.py
        ├── dashboard_view.py
        ├── product_list_view.py
        ├── product_form_view.py
        ├── sale_pos_view.py
        └── main_window.py
```

## Architecture

### Data Access Pattern

The application uses the **Repository Pattern** for data access:

- Each database table has a corresponding Repository class
- Repositories handle all SQL queries using parameterized queries
- The `db.py` module provides connection management with context managers

### Security

- **Password Hashing**: Employee passwords are hashed using bcrypt via passlib
- **Parameterized Queries**: All database queries use parameters to prevent SQL injection
- **Configuration**: Database credentials are stored in `config.ini` (not in code)

### UI Architecture

- **Main Window**: Contains navigation sidebar and stacked widget for views
- **Views**: Each screen is a separate QWidget class
- **Signals**: Views communicate via Qt signals
- **Stylesheet**: Modern dark sidebar with light content area (theme.qss)

## Keyboard Shortcuts

### Global
- `F5` - Refresh current view
- `Ctrl+H` - Go to Dashboard
- `Ctrl+Shift+P` - Go to POS

### Point of Sale
- `F1` - Focus search/barcode input
- `F2` - Checkout
- `F3` - Clear cart
- `Enter` - Add product (when searching)
- `Delete` - Remove selected item

### Product List
- `Ctrl+N` - Add new product
- `Ctrl+F` - Focus search
- `F5` - Refresh list
- `Delete` - Delete selected product
- `Enter` - Edit selected product

## Troubleshooting

### "Database Connection Error"

1. **Check SQL Server is running**: Open Services (services.msc) and ensure "SQL Server (MSSQLSERVER)" or "SQL Server (SQLEXPRESS)" is running

2. **Check database exists**: Open SSMS and verify "MobileAccessoryInventory" database exists

3. **Check ODBC Driver**: Run `odbcad32.exe` and verify "ODBC Driver 18 for SQL Server" is listed under Drivers tab

4. **Check connection settings**: Verify `config.ini` has correct server name

### "Login Failed"

1. Check you're using the correct username and password
2. Ensure the EMPLOYEE table has records (run the seed data section of SQL script)

### "Import Error: No module named 'PySide6'"

```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Development

### Adding a New View

1. Create a new file in `views/` directory
2. Create a QWidget subclass with signals for navigation
3. Add the view to `MainWindow._create_views()`
4. Connect navigation signals in `MainWindow._connect_signals()`
5. Add navigation handling in `MainWindow._navigate_to()`
6. Update `views/__init__.py` with the new import

### Adding a New Repository

1. Create a new file in `repositories/` directory
2. Create a dataclass for the entity
3. Implement `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()` methods
4. Update `repositories/__init__.py` with the new import

## License

This project is for educational purposes.

## Support

For issues or questions, please open an issue in the project repository.
