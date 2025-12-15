-- ============================================================================
-- MOBILE ACCESSORY INVENTORY SYSTEM - DATABASE SCHEMA ONLY
-- ============================================================================
-- This file contains ONLY the database structure (tables, indexes, types).
-- All business logic is in stored_procedures.sql
-- 
-- SETUP ORDER:
--   1. Run this file FIRST (creates database + tables)
--   2. Run stored_procedures.sql SECOND (creates all procedures)
-- ============================================================================

USE master;
GO

-- Drop database if exists (for clean re-install)
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'MobileAccessoryInventory')
BEGIN
    ALTER DATABASE MobileAccessoryInventory SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE MobileAccessoryInventory;
END
GO

CREATE DATABASE MobileAccessoryInventory;
GO

USE MobileAccessoryInventory;
GO

-- ============================================================================
-- TABLES
-- ============================================================================

-- CATEGORY: Main product categories (e.g., Cases, Chargers, Cables)
CREATE TABLE dbo.CATEGORY (
    Cat_ID          NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Cat_Name        NVARCHAR(50)    NOT NULL,
    Description     NVARCHAR(200)   NULL
);
GO

-- SUBCATEGORY: Sub-categories within each category
CREATE TABLE dbo.SUBCATEGORY (
    Subcat_ID       NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Cat_ID          NVARCHAR(10)    NOT NULL,
    Subcat_Name     NVARCHAR(50)    NOT NULL,
    Description     NVARCHAR(200)   NULL,
    CONSTRAINT FK_SUBCATEGORY_CATEGORY FOREIGN KEY (Cat_ID) REFERENCES dbo.CATEGORY(Cat_ID)
);
GO

-- BRAND: Product manufacturers/brands
CREATE TABLE dbo.BRAND (
    Brand_ID        NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Brand_Name      NVARCHAR(50)    NOT NULL,
    Description     NVARCHAR(200)   NULL
);
GO

-- PRODUCT: All products sold in the store
CREATE TABLE dbo.PRODUCT (
    Product_Code    NVARCHAR(20)    NOT NULL PRIMARY KEY,
    Subcat_ID       NVARCHAR(10)    NOT NULL,
    Product_Name    NVARCHAR(100)   NOT NULL,
    Brand           NVARCHAR(50)    NULL,
    Description     NVARCHAR(300)   NULL,
    Cost_Price      DECIMAL(10,2)   NOT NULL CHECK (Cost_Price >= 0),
    Retail_Price    DECIMAL(10,2)   NOT NULL CHECK (Retail_Price >= 0),
    Min_Stock_Level INT             NOT NULL DEFAULT 5 CHECK (Min_Stock_Level >= 0),
    Date_Added      DATE            NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_PRODUCT_SUBCATEGORY FOREIGN KEY (Subcat_ID) REFERENCES dbo.SUBCATEGORY(Subcat_ID)
);
GO

-- INVENTORY: Current stock for each product
CREATE TABLE dbo.INVENTORY (
    Product_Code    NVARCHAR(20)    NOT NULL PRIMARY KEY,
    Current_Stock   INT             NOT NULL DEFAULT 0 CHECK (Current_Stock >= 0),
    Last_Updated    DATETIME        NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_INVENTORY_PRODUCT FOREIGN KEY (Product_Code) REFERENCES dbo.PRODUCT(Product_Code)
);
GO

-- SUPPLIER: Vendors we purchase from
CREATE TABLE dbo.SUPPLIER (
    Supplier_ID     NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Supplier_Name   NVARCHAR(100)   NOT NULL,
    Contact_Person  NVARCHAR(100)   NULL,
    Phone           NVARCHAR(20)    NULL,
    Email           NVARCHAR(100)   NULL,
    Address         NVARCHAR(200)   NULL,
    City            NVARCHAR(50)    NULL
);
GO

-- PURCHASE: Purchase orders to suppliers (header)
CREATE TABLE dbo.PURCHASE (
    Purchase_No     NVARCHAR(20)    NOT NULL PRIMARY KEY,
    Supplier_ID     NVARCHAR(10)    NOT NULL,
    Purchase_Date   DATE            NOT NULL DEFAULT GETDATE(),
    Total_Amount    DECIMAL(10,2)   NOT NULL DEFAULT 0 CHECK (Total_Amount >= 0),
    Payment_Status  NVARCHAR(20)    NOT NULL DEFAULT 'Pending',
    Notes           NVARCHAR(500)   NULL,
    CONSTRAINT FK_PURCHASE_SUPPLIER FOREIGN KEY (Supplier_ID) REFERENCES dbo.SUPPLIER(Supplier_ID)
);
GO

-- PURCHASE_DETAIL: Line items for each purchase
CREATE TABLE dbo.PURCHASE_DETAIL (
    Purchase_No     NVARCHAR(20)    NOT NULL,
    Product_Code    NVARCHAR(20)    NOT NULL,
    Quantity        INT             NOT NULL CHECK (Quantity >= 0),
    Unit_Price      DECIMAL(10,2)   NOT NULL CHECK (Unit_Price >= 0),
    Line_Total      DECIMAL(10,2)   NOT NULL CHECK (Line_Total >= 0),
    CONSTRAINT PK_PURCHASE_DETAIL PRIMARY KEY (Purchase_No, Product_Code),
    CONSTRAINT FK_PURCHASEDETAIL_PURCHASE FOREIGN KEY (Purchase_No) REFERENCES dbo.PURCHASE(Purchase_No),
    CONSTRAINT FK_PURCHASEDETAIL_PRODUCT FOREIGN KEY (Product_Code) REFERENCES dbo.PRODUCT(Product_Code)
);
GO

-- EMPLOYEE: Store staff with login credentials
CREATE TABLE dbo.EMPLOYEE (
    Employee_ID     NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Employee_Name   NVARCHAR(100)   NOT NULL,
    Phone           NVARCHAR(20)    NULL,
    Email           NVARCHAR(100)   NULL,
    Position        NVARCHAR(50)    NULL,
    Hire_Date       DATE            NOT NULL DEFAULT GETDATE(),
    Salary          DECIMAL(10,2)   NULL CHECK (Salary IS NULL OR Salary >= 0),
    Username        NVARCHAR(50)    NULL,
    password_hash   NVARCHAR(200)   NULL,
    role            NVARCHAR(30)    NOT NULL DEFAULT 'Employee'
);
GO

-- CUSTOMER: Customers who purchase from store
CREATE TABLE dbo.CUSTOMER (
    Customer_ID         NVARCHAR(10)    NOT NULL PRIMARY KEY,
    Customer_Name       NVARCHAR(100)   NOT NULL,
    Phone               NVARCHAR(20)    NULL,
    Email               NVARCHAR(100)   NULL,
    Address             NVARCHAR(200)   NULL,
    City                NVARCHAR(50)    NULL,
    Registration_Date   DATE            NOT NULL DEFAULT GETDATE()
);
GO

-- SALE: Sales invoices (header)
CREATE TABLE dbo.SALE (
    Invoice_No      NVARCHAR(20)    NOT NULL PRIMARY KEY,
    Customer_ID     NVARCHAR(10)    NOT NULL,
    Employee_ID     NVARCHAR(10)    NOT NULL,
    Sale_Date       DATE            NOT NULL DEFAULT GETDATE(),
    Sale_Time       TIME            NOT NULL DEFAULT CONVERT(TIME, GETDATE()),
    Total_Amount    DECIMAL(10,2)   NOT NULL DEFAULT 0 CHECK (Total_Amount >= 0),
    Discount        DECIMAL(10,2)   NOT NULL DEFAULT 0 CHECK (Discount >= 0),
    Net_Amount      DECIMAL(10,2)   NOT NULL DEFAULT 0 CHECK (Net_Amount >= 0),
    CONSTRAINT FK_SALE_CUSTOMER FOREIGN KEY (Customer_ID) REFERENCES dbo.CUSTOMER(Customer_ID),
    CONSTRAINT FK_SALE_EMPLOYEE FOREIGN KEY (Employee_ID) REFERENCES dbo.EMPLOYEE(Employee_ID)
);
GO

-- SALE_DETAIL: Line items for each sale
CREATE TABLE dbo.SALE_DETAIL (
    Invoice_No      NVARCHAR(20)    NOT NULL,
    Product_Code    NVARCHAR(20)    NOT NULL,
    Quantity        INT             NOT NULL CHECK (Quantity >= 0),
    Unit_Price      DECIMAL(10,2)   NOT NULL CHECK (Unit_Price >= 0),
    Line_Total      DECIMAL(10,2)   NOT NULL CHECK (Line_Total >= 0),
    CONSTRAINT PK_SALE_DETAIL PRIMARY KEY (Invoice_No, Product_Code),
    CONSTRAINT FK_SALEDETAIL_SALE FOREIGN KEY (Invoice_No) REFERENCES dbo.SALE(Invoice_No),
    CONSTRAINT FK_SALEDETAIL_PRODUCT FOREIGN KEY (Product_Code) REFERENCES dbo.PRODUCT(Product_Code)
);
GO

-- PAYMENT: Payments for sales
CREATE TABLE dbo.PAYMENT (
    Payment_ID      NVARCHAR(20)    NOT NULL PRIMARY KEY,
    Invoice_No      NVARCHAR(20)    NOT NULL,
    Payment_Method  NVARCHAR(30)    NOT NULL,
    Amount_Paid     DECIMAL(10,2)   NOT NULL CHECK (Amount_Paid >= 0),
    Payment_Date    DATETIME        NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_PAYMENT_SALE FOREIGN KEY (Invoice_No) REFERENCES dbo.SALE(Invoice_No)
);
GO

-- ============================================================================
-- INDEXES (for query performance)
-- ============================================================================
CREATE NONCLUSTERED INDEX IX_PRODUCT_SubcatID ON dbo.PRODUCT(Subcat_ID);
CREATE NONCLUSTERED INDEX IX_INVENTORY_CurrentStock ON dbo.INVENTORY(Current_Stock);
CREATE NONCLUSTERED INDEX IX_SALE_SaleDate ON dbo.SALE(Sale_Date);
CREATE NONCLUSTERED INDEX IX_PURCHASE_SupplierID ON dbo.PURCHASE(Supplier_ID);
CREATE NONCLUSTERED INDEX IX_SALE_EmployeeID ON dbo.SALE(Employee_ID);
CREATE NONCLUSTERED INDEX IX_SALE_CustomerID ON dbo.SALE(Customer_ID);
GO

-- ============================================================================
-- TABLE-VALUED TYPES (for passing multiple items to procedures)
-- ============================================================================
CREATE TYPE dbo.PurchaseDetailType AS TABLE (
    Product_Code    NVARCHAR(20)    NOT NULL,
    Quantity        INT             NOT NULL,
    Unit_Price      DECIMAL(10,2)   NOT NULL
);
GO

CREATE TYPE dbo.SaleDetailType AS TABLE (
    Product_Code    NVARCHAR(20)    NOT NULL,
    Quantity        INT             NOT NULL,
    Unit_Price      DECIMAL(10,2)   NOT NULL
);
GO

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Categories
INSERT INTO dbo.CATEGORY VALUES ('CAT001', 'Phone Cases', 'Protective cases for mobile phones');
INSERT INTO dbo.CATEGORY VALUES ('CAT002', 'Chargers', 'Charging devices and adapters');
INSERT INTO dbo.CATEGORY VALUES ('CAT003', 'Cables', 'Charging and data cables');
INSERT INTO dbo.CATEGORY VALUES ('CAT004', 'Screen Protectors', 'Screen protection films and glass');
INSERT INTO dbo.CATEGORY VALUES ('CAT005', 'Audio', 'Earphones and speakers');
GO

-- Subcategories
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB001', 'CAT001', 'Silicone Cases', 'Soft silicone protective cases');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB002', 'CAT001', 'Hard Cases', 'Rigid plastic protective cases');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB003', 'CAT002', 'Wall Chargers', 'Wall plug chargers');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB004', 'CAT002', 'Car Chargers', 'Vehicle charging adapters');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB005', 'CAT003', 'USB-C Cables', 'USB Type-C cables');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB006', 'CAT003', 'Lightning Cables', 'Apple Lightning cables');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB007', 'CAT004', 'Tempered Glass', 'Glass screen protectors');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB008', 'CAT005', 'Wired Earphones', 'Wired audio earphones');
INSERT INTO dbo.SUBCATEGORY VALUES ('SUB009', 'CAT005', 'Wireless Earbuds', 'Bluetooth earbuds');
GO

-- Brands
INSERT INTO dbo.BRAND VALUES ('BRD001', 'Anker', 'Quality charging accessories');
INSERT INTO dbo.BRAND VALUES ('BRD002', 'Apple', 'Apple Inc. products');
INSERT INTO dbo.BRAND VALUES ('BRD003', 'Belkin', 'Mobile accessories');
INSERT INTO dbo.BRAND VALUES ('BRD004', 'Samsung', 'Samsung Electronics');
INSERT INTO dbo.BRAND VALUES ('BRD005', 'Spigen', 'Phone cases and protectors');
GO

-- Suppliers
INSERT INTO dbo.SUPPLIER VALUES ('SUP001', 'TechSupply Co.', 'John Smith', '555-0101', 'john@techsupply.com', '123 Tech Street', 'New York');
INSERT INTO dbo.SUPPLIER VALUES ('SUP002', 'Mobile Parts Ltd.', 'Jane Doe', '555-0102', 'jane@mobileparts.com', '456 Parts Avenue', 'Los Angeles');
INSERT INTO dbo.SUPPLIER VALUES ('SUP003', 'AccessoryWorld', 'Bob Wilson', '555-0103', 'bob@accworld.com', '789 Accessory Blvd', 'Chicago');
GO

-- Walk-in Customer (required for POS)
INSERT INTO dbo.CUSTOMER VALUES ('C000', 'Walk-in Customer', NULL, NULL, NULL, NULL, GETDATE());
GO

-- Default Admin Employee (password: admin123)
INSERT INTO dbo.EMPLOYEE VALUES (
    'EMP001', 'Admin User', '555-1000', 'admin@store.com', 'Manager',
    GETDATE(), 50000.00, 'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.yqwTqzZzZzZzZz', 'Admin'
);
GO

-- Sample Products
INSERT INTO dbo.PRODUCT VALUES ('PRD001', 'SUB001', 'iPhone 15 Silicone Case', 'Apple', 'Original silicone case', 15.00, 29.99, 10, GETDATE());
INSERT INTO dbo.PRODUCT VALUES ('PRD002', 'SUB003', '20W USB-C Charger', 'Anker', 'Fast charging adapter', 12.00, 24.99, 15, GETDATE());
INSERT INTO dbo.PRODUCT VALUES ('PRD003', 'SUB005', 'USB-C Cable 2m', 'Belkin', 'Premium braided cable', 8.00, 19.99, 20, GETDATE());
GO

-- Initialize Inventory for sample products
INSERT INTO dbo.INVENTORY VALUES ('PRD001', 25, GETDATE());
INSERT INTO dbo.INVENTORY VALUES ('PRD002', 30, GETDATE());
INSERT INTO dbo.INVENTORY VALUES ('PRD003', 50, GETDATE());
GO

PRINT '========================================';
PRINT 'Database schema created successfully!';
PRINT 'Now run stored_procedures.sql';
PRINT '========================================';
GO
