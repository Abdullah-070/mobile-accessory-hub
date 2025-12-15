-- ============================================================================
-- MOBILE ACCESSORY INVENTORY SYSTEM - ALL STORED PROCEDURES
-- ============================================================================
-- This file contains ALL stored procedures for the system.
-- Run this file AFTER database_schema.sql
--
-- NAMING CONVENTION: usp_<Action><Entity>
--   - Add/Create = Insert new record
--   - Update     = Modify existing record
--   - Delete     = Remove record
--   - Get        = Retrieve single record
--   - List       = Retrieve multiple records
-- ============================================================================

USE MobileAccessoryInventory;
GO

-- ============================================================================
-- CATEGORY PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListCategories', 'P') IS NOT NULL DROP PROCEDURE usp_ListCategories;
GO
CREATE PROCEDURE usp_ListCategories
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Cat_ID, Cat_Name, Description
    FROM CATEGORY
    ORDER BY Cat_Name;
END;
GO

IF OBJECT_ID('usp_GetCategoryById', 'P') IS NOT NULL DROP PROCEDURE usp_GetCategoryById;
GO
CREATE PROCEDURE usp_GetCategoryById
    @CatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Cat_ID, Cat_Name, Description
    FROM CATEGORY
    WHERE Cat_ID = @CatId;
END;
GO

IF OBJECT_ID('usp_AddCategory', 'P') IS NOT NULL DROP PROCEDURE usp_AddCategory;
GO
CREATE PROCEDURE usp_AddCategory
    @CatId NVARCHAR(10),
    @CatName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO CATEGORY (Cat_ID, Cat_Name, Description)
    VALUES (@CatId, @CatName, @Description);
END;
GO

IF OBJECT_ID('usp_UpdateCategory', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateCategory;
GO
CREATE PROCEDURE usp_UpdateCategory
    @CatId NVARCHAR(10),
    @CatName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE CATEGORY
    SET Cat_Name = @CatName, Description = @Description
    WHERE Cat_ID = @CatId;
END;
GO

IF OBJECT_ID('usp_DeleteCategory', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteCategory;
GO
CREATE PROCEDURE usp_DeleteCategory
    @CatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM CATEGORY WHERE Cat_ID = @CatId;
END;
GO

IF OBJECT_ID('usp_GetNextCategoryId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextCategoryId;
GO
CREATE PROCEDURE usp_GetNextCategoryId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Cat_ID, 4, 10) AS INT)), 0) + 1
    FROM CATEGORY;
    SELECT 'CAT' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

-- ============================================================================
-- SUBCATEGORY PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListSubcategories', 'P') IS NOT NULL DROP PROCEDURE usp_ListSubcategories;
GO
CREATE PROCEDURE usp_ListSubcategories
    @CatId NVARCHAR(10) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Subcat_ID, s.Cat_ID, s.Subcat_Name, s.Description, c.Cat_Name
    FROM SUBCATEGORY s
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    WHERE (@CatId IS NULL OR s.Cat_ID = @CatId)
    ORDER BY c.Cat_Name, s.Subcat_Name;
END;
GO

IF OBJECT_ID('usp_GetSubcategoryById', 'P') IS NOT NULL DROP PROCEDURE usp_GetSubcategoryById;
GO
CREATE PROCEDURE usp_GetSubcategoryById
    @SubcatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Subcat_ID, s.Cat_ID, s.Subcat_Name, s.Description, c.Cat_Name
    FROM SUBCATEGORY s
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    WHERE s.Subcat_ID = @SubcatId;
END;
GO

IF OBJECT_ID('usp_GetSubcategoriesByCategory', 'P') IS NOT NULL DROP PROCEDURE usp_GetSubcategoriesByCategory;
GO
CREATE PROCEDURE usp_GetSubcategoriesByCategory
    @CatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Subcat_ID, s.Cat_ID, s.Subcat_Name, s.Description, c.Cat_Name
    FROM SUBCATEGORY s
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    WHERE s.Cat_ID = @CatId
    ORDER BY s.Subcat_Name;
END;
GO

IF OBJECT_ID('usp_AddSubcategory', 'P') IS NOT NULL DROP PROCEDURE usp_AddSubcategory;
GO
CREATE PROCEDURE usp_AddSubcategory
    @SubcatId NVARCHAR(10),
    @CatId NVARCHAR(10),
    @SubcatName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO SUBCATEGORY (Subcat_ID, Cat_ID, Subcat_Name, Description)
    VALUES (@SubcatId, @CatId, @SubcatName, @Description);
END;
GO

IF OBJECT_ID('usp_UpdateSubcategory', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateSubcategory;
GO
CREATE PROCEDURE usp_UpdateSubcategory
    @SubcatId NVARCHAR(10),
    @CatId NVARCHAR(10),
    @SubcatName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE SUBCATEGORY
    SET Cat_ID = @CatId, Subcat_Name = @SubcatName, Description = @Description
    WHERE Subcat_ID = @SubcatId;
END;
GO

IF OBJECT_ID('usp_DeleteSubcategory', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteSubcategory;
GO
CREATE PROCEDURE usp_DeleteSubcategory
    @SubcatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM SUBCATEGORY WHERE Subcat_ID = @SubcatId;
END;
GO

IF OBJECT_ID('usp_GetNextSubcategoryId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextSubcategoryId;
GO
CREATE PROCEDURE usp_GetNextSubcategoryId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Subcat_ID, 4, 10) AS INT)), 0) + 1
    FROM SUBCATEGORY;
    SELECT 'SUB' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

IF OBJECT_ID('usp_DeleteSubcategoriesByCategory', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteSubcategoriesByCategory;
GO
CREATE PROCEDURE usp_DeleteSubcategoriesByCategory
    @CatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM SUBCATEGORY WHERE Cat_ID = @CatId;
END;
GO

-- ============================================================================
-- BRAND PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListBrands', 'P') IS NOT NULL DROP PROCEDURE usp_ListBrands;
GO
CREATE PROCEDURE usp_ListBrands
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Brand_ID, Brand_Name, Description FROM BRAND ORDER BY Brand_Name;
END;
GO

IF OBJECT_ID('usp_GetBrandById', 'P') IS NOT NULL DROP PROCEDURE usp_GetBrandById;
GO
CREATE PROCEDURE usp_GetBrandById
    @BrandId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Brand_ID, Brand_Name, Description FROM BRAND WHERE Brand_ID = @BrandId;
END;
GO

IF OBJECT_ID('usp_GetBrandByName', 'P') IS NOT NULL DROP PROCEDURE usp_GetBrandByName;
GO
CREATE PROCEDURE usp_GetBrandByName
    @BrandName NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Brand_ID, Brand_Name, Description FROM BRAND WHERE Brand_Name = @BrandName;
END;
GO

IF OBJECT_ID('usp_AddBrand', 'P') IS NOT NULL DROP PROCEDURE usp_AddBrand;
GO
CREATE PROCEDURE usp_AddBrand
    @BrandId NVARCHAR(10),
    @BrandName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO BRAND (Brand_ID, Brand_Name, Description) VALUES (@BrandId, @BrandName, @Description);
END;
GO

IF OBJECT_ID('usp_UpdateBrand', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateBrand;
GO
CREATE PROCEDURE usp_UpdateBrand
    @BrandId NVARCHAR(10),
    @BrandName NVARCHAR(50),
    @Description NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE BRAND SET Brand_Name = @BrandName, Description = @Description WHERE Brand_ID = @BrandId;
END;
GO

IF OBJECT_ID('usp_DeleteBrand', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteBrand;
GO
CREATE PROCEDURE usp_DeleteBrand
    @BrandId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM BRAND WHERE Brand_ID = @BrandId;
END;
GO

IF OBJECT_ID('usp_GetNextBrandId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextBrandId;
GO
CREATE PROCEDURE usp_GetNextBrandId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Brand_ID, 4, 10) AS INT)), 0) + 1 FROM BRAND;
    SELECT 'BRD' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

IF OBJECT_ID('usp_CheckProductsExistForBrand', 'P') IS NOT NULL DROP PROCEDURE usp_CheckProductsExistForBrand;
GO
CREATE PROCEDURE usp_CheckProductsExistForBrand
    @BrandName NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check if any products exist with this brand name
    -- Also check inventory to see if any have stock
    SELECT 
        COUNT(*) AS ProductCount,
        ISNULL(SUM(CASE WHEN i.Current_Stock > 0 THEN 1 ELSE 0 END), 0) AS ProductsWithStock,
        ISNULL(SUM(i.Current_Stock), 0) AS TotalStockQty
    FROM PRODUCT p
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE p.Brand = @BrandName;
END;
GO

-- ============================================================================
-- SUPPLIER PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListSuppliers', 'P') IS NOT NULL DROP PROCEDURE usp_ListSuppliers;
GO
CREATE PROCEDURE usp_ListSuppliers
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Supplier_ID, Supplier_Name, Contact_Person, Phone, Email, Address, City
    FROM SUPPLIER
    ORDER BY Supplier_Name;
END;
GO

IF OBJECT_ID('usp_GetSupplierById', 'P') IS NOT NULL DROP PROCEDURE usp_GetSupplierById;
GO
CREATE PROCEDURE usp_GetSupplierById
    @SupplierId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Supplier_ID, Supplier_Name, Contact_Person, Phone, Email, Address, City
    FROM SUPPLIER
    WHERE Supplier_ID = @SupplierId;
END;
GO

IF OBJECT_ID('usp_AddSupplier', 'P') IS NOT NULL DROP PROCEDURE usp_AddSupplier;
GO
CREATE PROCEDURE usp_AddSupplier
    @SupplierId NVARCHAR(10),
    @SupplierName NVARCHAR(100),
    @ContactPerson NVARCHAR(100) = NULL,
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Address NVARCHAR(200) = NULL,
    @City NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO SUPPLIER (Supplier_ID, Supplier_Name, Contact_Person, Phone, Email, Address, City)
    VALUES (@SupplierId, @SupplierName, @ContactPerson, @Phone, @Email, @Address, @City);
END;
GO

IF OBJECT_ID('usp_UpdateSupplier', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateSupplier;
GO
CREATE PROCEDURE usp_UpdateSupplier
    @SupplierId NVARCHAR(10),
    @SupplierName NVARCHAR(100),
    @ContactPerson NVARCHAR(100) = NULL,
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Address NVARCHAR(200) = NULL,
    @City NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE SUPPLIER
    SET Supplier_Name = @SupplierName, Contact_Person = @ContactPerson,
        Phone = @Phone, Email = @Email, Address = @Address, City = @City
    WHERE Supplier_ID = @SupplierId;
END;
GO

IF OBJECT_ID('usp_DeleteSupplier', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteSupplier;
GO
CREATE PROCEDURE usp_DeleteSupplier
    @SupplierId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM SUPPLIER WHERE Supplier_ID = @SupplierId;
END;
GO

IF OBJECT_ID('usp_GetNextSupplierId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextSupplierId;
GO
CREATE PROCEDURE usp_GetNextSupplierId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Supplier_ID, 4, 10) AS INT)), 0) + 1
    FROM SUPPLIER;
    SELECT 'SUP' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

IF OBJECT_ID('usp_SearchSuppliers', 'P') IS NOT NULL DROP PROCEDURE usp_SearchSuppliers;
GO
CREATE PROCEDURE usp_SearchSuppliers
    @SearchTerm NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Pattern NVARCHAR(102) = '%' + @SearchTerm + '%';
    SELECT Supplier_ID, Supplier_Name, Contact_Person, Phone, Email, Address, City
    FROM SUPPLIER
    WHERE Supplier_Name LIKE @Pattern OR Contact_Person LIKE @Pattern OR City LIKE @Pattern
    ORDER BY Supplier_Name;
END;
GO

-- ============================================================================
-- CUSTOMER PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListCustomers', 'P') IS NOT NULL DROP PROCEDURE usp_ListCustomers;
GO
CREATE PROCEDURE usp_ListCustomers
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Customer_ID, Customer_Name, Phone, Email, Address, City, Registration_Date
    FROM CUSTOMER
    ORDER BY Customer_Name;
END;
GO

IF OBJECT_ID('usp_GetCustomerById', 'P') IS NOT NULL DROP PROCEDURE usp_GetCustomerById;
GO
CREATE PROCEDURE usp_GetCustomerById
    @CustomerId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Customer_ID, Customer_Name, Phone, Email, Address, City, Registration_Date
    FROM CUSTOMER
    WHERE Customer_ID = @CustomerId;
END;
GO

IF OBJECT_ID('usp_AddCustomer', 'P') IS NOT NULL DROP PROCEDURE usp_AddCustomer;
GO
CREATE PROCEDURE usp_AddCustomer
    @CustomerId NVARCHAR(10),
    @CustomerName NVARCHAR(100),
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Address NVARCHAR(200) = NULL,
    @City NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO CUSTOMER (Customer_ID, Customer_Name, Phone, Email, Address, City)
    VALUES (@CustomerId, @CustomerName, @Phone, @Email, @Address, @City);
END;
GO

IF OBJECT_ID('usp_UpdateCustomer', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateCustomer;
GO
CREATE PROCEDURE usp_UpdateCustomer
    @CustomerId NVARCHAR(10),
    @CustomerName NVARCHAR(100),
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Address NVARCHAR(200) = NULL,
    @City NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE CUSTOMER
    SET Customer_Name = @CustomerName, Phone = @Phone, Email = @Email, 
        Address = @Address, City = @City
    WHERE Customer_ID = @CustomerId;
END;
GO

IF OBJECT_ID('usp_DeleteCustomer', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteCustomer;
GO
CREATE PROCEDURE usp_DeleteCustomer
    @CustomerId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM CUSTOMER WHERE Customer_ID = @CustomerId;
END;
GO

IF OBJECT_ID('usp_GetNextCustomerId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextCustomerId;
GO
CREATE PROCEDURE usp_GetNextCustomerId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Customer_ID, 2, 10) AS INT)), 0) + 1
    FROM CUSTOMER
    WHERE Customer_ID != 'C000';
    SELECT 'C' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

IF OBJECT_ID('usp_GetCustomerPurchaseHistory', 'P') IS NOT NULL DROP PROCEDURE usp_GetCustomerPurchaseHistory;
GO
CREATE PROCEDURE usp_GetCustomerPurchaseHistory
    @CustomerId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Invoice_No, s.Sale_Date, s.Total_Amount, s.Net_Amount, e.Employee_Name
    FROM SALE s
    LEFT JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    WHERE s.Customer_ID = @CustomerId
    ORDER BY s.Sale_Date DESC;
END;
GO

-- ============================================================================
-- EMPLOYEE PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListEmployees', 'P') IS NOT NULL DROP PROCEDURE usp_ListEmployees;
GO
CREATE PROCEDURE usp_ListEmployees
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Employee_ID, Employee_Name, Phone, Email, Position, Hire_Date, Salary, Username, role
    FROM EMPLOYEE
    ORDER BY Employee_Name;
END;
GO

IF OBJECT_ID('usp_GetEmployeeById', 'P') IS NOT NULL DROP PROCEDURE usp_GetEmployeeById;
GO
CREATE PROCEDURE usp_GetEmployeeById
    @EmployeeId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Employee_ID, Employee_Name, Phone, Email, Position, Hire_Date, Salary, Username, role
    FROM EMPLOYEE
    WHERE Employee_ID = @EmployeeId;
END;
GO

IF OBJECT_ID('usp_AddEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_AddEmployee;
GO
CREATE PROCEDURE usp_AddEmployee
    @EmployeeId NVARCHAR(10),
    @EmployeeName NVARCHAR(100),
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Position NVARCHAR(50) = NULL,
    @Salary DECIMAL(10,2) = NULL,
    @Username NVARCHAR(50) = NULL,
    @PasswordHash NVARCHAR(200) = NULL,
    @Role NVARCHAR(30) = 'Employee'
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO EMPLOYEE (Employee_ID, Employee_Name, Phone, Email, Position, Hire_Date, Salary, Username, password_hash, role)
    VALUES (@EmployeeId, @EmployeeName, @Phone, @Email, @Position, GETDATE(), @Salary, @Username, @PasswordHash, @Role);
END;
GO

IF OBJECT_ID('usp_UpdateEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateEmployee;
GO
CREATE PROCEDURE usp_UpdateEmployee
    @EmployeeId NVARCHAR(10),
    @EmployeeName NVARCHAR(100),
    @Phone NVARCHAR(20) = NULL,
    @Email NVARCHAR(100) = NULL,
    @Position NVARCHAR(50) = NULL,
    @Salary DECIMAL(10,2) = NULL,
    @Username NVARCHAR(50) = NULL,
    @Role NVARCHAR(30) = 'Employee'
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE EMPLOYEE
    SET Employee_Name = @EmployeeName, Phone = @Phone, Email = @Email,
        Position = @Position, Salary = @Salary, Username = @Username, role = @Role
    WHERE Employee_ID = @EmployeeId;
END;
GO

IF OBJECT_ID('usp_DeleteEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteEmployee;
GO
CREATE PROCEDURE usp_DeleteEmployee
    @EmployeeId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM EMPLOYEE WHERE Employee_ID = @EmployeeId;
END;
GO

IF OBJECT_ID('usp_GetNextEmployeeId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextEmployeeId;
GO
CREATE PROCEDURE usp_GetNextEmployeeId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Employee_ID, 4, 10) AS INT)), 0) + 1
    FROM EMPLOYEE;
    SELECT 'EMP' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

IF OBJECT_ID('usp_AuthenticateEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_AuthenticateEmployee;
GO
CREATE PROCEDURE usp_AuthenticateEmployee
    @Username NVARCHAR(50),
    @PasswordHash NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Employee_ID, Employee_Name, Phone, Email, Position, Username, role
    FROM EMPLOYEE
    WHERE Username = @Username AND password_hash = @PasswordHash;
END;
GO

IF OBJECT_ID('usp_ChangeEmployeePassword', 'P') IS NOT NULL DROP PROCEDURE usp_ChangeEmployeePassword;
GO
CREATE PROCEDURE usp_ChangeEmployeePassword
    @EmployeeId NVARCHAR(10),
    @NewPasswordHash NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE EMPLOYEE SET password_hash = @NewPasswordHash WHERE Employee_ID = @EmployeeId;
END;
GO

IF OBJECT_ID('usp_GetEmployeeByUsername', 'P') IS NOT NULL DROP PROCEDURE usp_GetEmployeeByUsername;
GO
CREATE PROCEDURE usp_GetEmployeeByUsername
    @Username NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Employee_ID, Employee_Name, Phone, Email, Position, Hire_Date, Salary, Username, password_hash, role
    FROM EMPLOYEE WHERE Username = @Username;
END;
GO

IF OBJECT_ID('usp_GetEmployeeWithPassword', 'P') IS NOT NULL DROP PROCEDURE usp_GetEmployeeWithPassword;
GO
CREATE PROCEDURE usp_GetEmployeeWithPassword
    @Username NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Employee_ID, Employee_Name, Phone, Email, Position, Hire_Date, Salary, Username, password_hash, role
    FROM EMPLOYEE WHERE Username = @Username;
END;
GO

IF OBJECT_ID('usp_CheckSalesExistForEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_CheckSalesExistForEmployee;
GO
CREATE PROCEDURE usp_CheckSalesExistForEmployee
    @EmployeeId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT COUNT(*) AS SaleCount FROM SALE WHERE Employee_ID = @EmployeeId;
END;
GO

-- ============================================================================
-- PRODUCT PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListProducts', 'P') IS NOT NULL DROP PROCEDURE usp_ListProducts;
GO
CREATE PROCEDURE usp_ListProducts
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_ID, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetProductByCode', 'P') IS NOT NULL DROP PROCEDURE usp_GetProductByCode;
GO
CREATE PROCEDURE usp_GetProductByCode
    @ProductCode NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_ID, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE p.Product_Code = @ProductCode;
END;
GO

IF OBJECT_ID('usp_GetProductsByCategory', 'P') IS NOT NULL DROP PROCEDURE usp_GetProductsByCategory;
GO
CREATE PROCEDURE usp_GetProductsByCategory
    @CatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE c.Cat_ID = @CatId
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetProductsBySubcategory', 'P') IS NOT NULL DROP PROCEDURE usp_GetProductsBySubcategory;
GO
CREATE PROCEDURE usp_GetProductsBySubcategory
    @SubcatId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE p.Subcat_ID = @SubcatId
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_SearchProducts', 'P') IS NOT NULL DROP PROCEDURE usp_SearchProducts;
GO
CREATE PROCEDURE usp_SearchProducts
    @SearchTerm NVARCHAR(100) = NULL,
    @CatId NVARCHAR(10) = NULL,
    @SubcatId NVARCHAR(10) = NULL,
    @LowStockOnly BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE (@SearchTerm IS NULL OR 
           p.Product_Code LIKE '%' + @SearchTerm + '%' OR
           p.Product_Name LIKE '%' + @SearchTerm + '%' OR
           p.Brand LIKE '%' + @SearchTerm + '%')
      AND (@CatId IS NULL OR c.Cat_ID = @CatId)
      AND (@SubcatId IS NULL OR p.Subcat_ID = @SubcatId)
      AND (@LowStockOnly = 0 OR ISNULL(i.Current_Stock, 0) <= p.Min_Stock_Level)
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetLowStockProducts', 'P') IS NOT NULL DROP PROCEDURE usp_GetLowStockProducts;
GO
CREATE PROCEDURE usp_GetLowStockProducts
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        p.Product_Code, p.Subcat_ID, p.Product_Name, p.Brand, 
        p.Description, p.Cost_Price, p.Retail_Price, 
        p.Min_Stock_Level, p.Date_Added,
        s.Subcat_Name, c.Cat_Name,
        ISNULL(i.Current_Stock, 0) AS Current_Stock,
        i.Last_Updated
    FROM PRODUCT p
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE ISNULL(i.Current_Stock, 0) <= p.Min_Stock_Level
    ORDER BY (p.Min_Stock_Level - ISNULL(i.Current_Stock, 0)) DESC;
END;
GO

IF OBJECT_ID('usp_AddProduct', 'P') IS NOT NULL DROP PROCEDURE usp_AddProduct;
GO
CREATE PROCEDURE usp_AddProduct
    @ProductCode NVARCHAR(20),
    @SubcatId NVARCHAR(10),
    @ProductName NVARCHAR(100),
    @Brand NVARCHAR(50) = NULL,
    @Description NVARCHAR(300) = NULL,
    @CostPrice DECIMAL(10,2),
    @RetailPrice DECIMAL(10,2),
    @MinStockLevel INT = 5,
    @InitialStock INT = 0
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        INSERT INTO PRODUCT (Product_Code, Subcat_ID, Product_Name, Brand, Description, 
                             Cost_Price, Retail_Price, Min_Stock_Level, Date_Added)
        VALUES (@ProductCode, @SubcatId, @ProductName, @Brand, @Description,
                @CostPrice, @RetailPrice, @MinStockLevel, GETDATE());
        
        INSERT INTO INVENTORY (Product_Code, Current_Stock, Last_Updated)
        VALUES (@ProductCode, @InitialStock, GETDATE());
        
        COMMIT TRANSACTION;
        SELECT 1 AS Success;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

IF OBJECT_ID('usp_UpdateProduct', 'P') IS NOT NULL DROP PROCEDURE usp_UpdateProduct;
GO
CREATE PROCEDURE usp_UpdateProduct
    @ProductCode NVARCHAR(20),
    @SubcatId NVARCHAR(10),
    @ProductName NVARCHAR(100),
    @Brand NVARCHAR(50) = NULL,
    @Description NVARCHAR(300) = NULL,
    @CostPrice DECIMAL(10,2),
    @RetailPrice DECIMAL(10,2),
    @MinStockLevel INT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE PRODUCT
    SET Subcat_ID = @SubcatId, Product_Name = @ProductName, Brand = @Brand,
        Description = @Description, Cost_Price = @CostPrice, 
        Retail_Price = @RetailPrice, Min_Stock_Level = @MinStockLevel
    WHERE Product_Code = @ProductCode;
END;
GO

IF OBJECT_ID('usp_DeleteProduct', 'P') IS NOT NULL DROP PROCEDURE usp_DeleteProduct;
GO
CREATE PROCEDURE usp_DeleteProduct
    @ProductCode NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        DELETE FROM INVENTORY WHERE Product_Code = @ProductCode;
        DELETE FROM PRODUCT WHERE Product_Code = @ProductCode;
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

IF OBJECT_ID('usp_GetNextProductCode', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextProductCode;
GO
CREATE PROCEDURE usp_GetNextProductCode
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Product_Code, 4, 10) AS INT)), 0) + 1
    FROM PRODUCT;
    SELECT 'PRD' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextCode;
END;
GO

-- ============================================================================
-- INVENTORY PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListInventory', 'P') IS NOT NULL DROP PROCEDURE usp_ListInventory;
GO
CREATE PROCEDURE usp_ListInventory
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        i.Product_Code, i.Current_Stock, i.Last_Updated,
        p.Product_Name, p.Brand, p.Min_Stock_Level, 
        p.Retail_Price, p.Cost_Price,
        s.Subcat_Name, c.Cat_Name
    FROM INVENTORY i
    INNER JOIN PRODUCT p ON i.Product_Code = p.Product_Code
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetInventoryByProduct', 'P') IS NOT NULL DROP PROCEDURE usp_GetInventoryByProduct;
GO
CREATE PROCEDURE usp_GetInventoryByProduct
    @ProductCode NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        i.Product_Code, i.Current_Stock, i.Last_Updated,
        p.Product_Name, p.Brand, p.Min_Stock_Level, 
        p.Retail_Price, p.Cost_Price,
        s.Subcat_Name, c.Cat_Name
    FROM INVENTORY i
    INNER JOIN PRODUCT p ON i.Product_Code = p.Product_Code
    INNER JOIN SUBCATEGORY s ON p.Subcat_ID = s.Subcat_ID
    INNER JOIN CATEGORY c ON s.Cat_ID = c.Cat_ID
    WHERE i.Product_Code = @ProductCode;
END;
GO

IF OBJECT_ID('usp_AdjustInventory', 'P') IS NOT NULL DROP PROCEDURE usp_AdjustInventory;
GO
CREATE PROCEDURE usp_AdjustInventory
    @ProductCode NVARCHAR(20),
    @Adjustment INT,
    @Reason NVARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE INVENTORY
    SET Current_Stock = Current_Stock + @Adjustment,
        Last_Updated = GETDATE()
    WHERE Product_Code = @ProductCode
      AND (Current_Stock + @Adjustment) >= 0;
    
    IF @@ROWCOUNT = 0
        RAISERROR('Adjustment would result in negative stock or product not found', 16, 1);
END;
GO

IF OBJECT_ID('usp_GetInventorySummary', 'P') IS NOT NULL DROP PROCEDURE usp_GetInventorySummary;
GO
CREATE PROCEDURE usp_GetInventorySummary
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        COUNT(*) AS Total_Products,
        SUM(i.Current_Stock) AS Total_Units,
        SUM(CASE WHEN i.Current_Stock <= p.Min_Stock_Level THEN 1 ELSE 0 END) AS Low_Stock_Count,
        SUM(i.Current_Stock * p.Cost_Price) AS Cost_Value,
        SUM(i.Current_Stock * p.Retail_Price) AS Retail_Value
    FROM INVENTORY i
    INNER JOIN PRODUCT p ON i.Product_Code = p.Product_Code;
END;
GO

-- ============================================================================
-- PURCHASE PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListPurchases', 'P') IS NOT NULL DROP PROCEDURE usp_ListPurchases;
GO
CREATE PROCEDURE usp_ListPurchases
AS
BEGIN
    SET NOCOUNT ON;
    SELECT p.Purchase_No, p.Supplier_ID, p.Purchase_Date, 
           p.Total_Amount, p.Payment_Status, p.Notes,
           s.Supplier_Name
    FROM PURCHASE p
    INNER JOIN SUPPLIER s ON p.Supplier_ID = s.Supplier_ID
    ORDER BY p.Purchase_Date DESC, p.Purchase_No DESC;
END;
GO

IF OBJECT_ID('usp_GetPurchaseById', 'P') IS NOT NULL DROP PROCEDURE usp_GetPurchaseById;
GO
CREATE PROCEDURE usp_GetPurchaseById
    @PurchaseNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT p.Purchase_No, p.Supplier_ID, p.Purchase_Date, 
           p.Total_Amount, p.Payment_Status, p.Notes,
           s.Supplier_Name
    FROM PURCHASE p
    INNER JOIN SUPPLIER s ON p.Supplier_ID = s.Supplier_ID
    WHERE p.Purchase_No = @PurchaseNo;
END;
GO

IF OBJECT_ID('usp_GetPurchaseDetails', 'P') IS NOT NULL DROP PROCEDURE usp_GetPurchaseDetails;
GO
CREATE PROCEDURE usp_GetPurchaseDetails
    @PurchaseNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT pd.Purchase_No, pd.Product_Code, pd.Quantity, 
           pd.Unit_Price, pd.Line_Total, pr.Product_Name
    FROM PURCHASE_DETAIL pd
    INNER JOIN PRODUCT pr ON pd.Product_Code = pr.Product_Code
    WHERE pd.Purchase_No = @PurchaseNo
    ORDER BY pr.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetPurchasesBySupplier', 'P') IS NOT NULL DROP PROCEDURE usp_GetPurchasesBySupplier;
GO
CREATE PROCEDURE usp_GetPurchasesBySupplier
    @SupplierId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT p.Purchase_No, p.Supplier_ID, p.Purchase_Date, 
           p.Total_Amount, p.Payment_Status, p.Notes,
           s.Supplier_Name
    FROM PURCHASE p
    INNER JOIN SUPPLIER s ON p.Supplier_ID = s.Supplier_ID
    WHERE p.Supplier_ID = @SupplierId
    ORDER BY p.Purchase_Date DESC;
END;
GO

IF OBJECT_ID('usp_GetPurchasesByDateRange', 'P') IS NOT NULL DROP PROCEDURE usp_GetPurchasesByDateRange;
GO
CREATE PROCEDURE usp_GetPurchasesByDateRange
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT p.Purchase_No, p.Supplier_ID, p.Purchase_Date, 
           p.Total_Amount, p.Payment_Status, p.Notes,
           s.Supplier_Name
    FROM PURCHASE p
    INNER JOIN SUPPLIER s ON p.Supplier_ID = s.Supplier_ID
    WHERE p.Purchase_Date BETWEEN @StartDate AND @EndDate
    ORDER BY p.Purchase_Date DESC;
END;
GO

IF OBJECT_ID('usp_GetNextPurchaseNo', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextPurchaseNo;
GO
CREATE PROCEDURE usp_GetNextPurchaseNo
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Purchase_No, 4, 10) AS INT)), 0) + 1
    FROM PURCHASE;
    SELECT 'PUR' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextNo;
END;
GO

-- Create Purchase Order (Pending - does NOT update inventory)
IF OBJECT_ID('usp_CreatePurchaseOrder', 'P') IS NOT NULL DROP PROCEDURE usp_CreatePurchaseOrder;
GO
CREATE PROCEDURE usp_CreatePurchaseOrder
    @PurchaseNo NVARCHAR(20),
    @SupplierID NVARCHAR(10),
    @ProductCode NVARCHAR(20),
    @Quantity INT,
    @UnitPrice DECIMAL(10,2),
    @Notes NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        DECLARE @LineTotal DECIMAL(10,2) = @Quantity * @UnitPrice;
        
        INSERT INTO PURCHASE (Purchase_No, Supplier_ID, Purchase_Date, Total_Amount, Payment_Status, Notes)
        VALUES (@PurchaseNo, @SupplierID, GETDATE(), @LineTotal, 'Pending', @Notes);
        
        INSERT INTO PURCHASE_DETAIL (Purchase_No, Product_Code, Quantity, Unit_Price, Line_Total)
        VALUES (@PurchaseNo, @ProductCode, @Quantity, @UnitPrice, @LineTotal);
        
        COMMIT TRANSACTION;
        SELECT 1 AS Success, @PurchaseNo AS PurchaseNo;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Create Purchase with Table-Valued Parameter (for multiple items)
IF OBJECT_ID('usp_CreatePurchase', 'P') IS NOT NULL DROP PROCEDURE usp_CreatePurchase;
GO
CREATE PROCEDURE usp_CreatePurchase
    @PurchaseNo NVARCHAR(20),
    @SupplierID NVARCHAR(10),
    @Notes NVARCHAR(500) = NULL,
    @Details dbo.PurchaseDetailType READONLY,
    @CreatedKey NVARCHAR(20) OUTPUT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @CreatedKey = NULL;
    SET @ErrorMessage = NULL;
    
    DECLARE @TotalAmount DECIMAL(10,2);
    
    IF NOT EXISTS (SELECT 1 FROM SUPPLIER WHERE Supplier_ID = @SupplierID)
    BEGIN
        SET @ErrorMessage = 'Supplier not found: ' + @SupplierID;
        RETURN;
    END
    
    IF NOT EXISTS (SELECT 1 FROM @Details)
    BEGIN
        SET @ErrorMessage = 'No purchase details provided';
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        SELECT @TotalAmount = SUM(Quantity * Unit_Price) FROM @Details;
        
        INSERT INTO PURCHASE (Purchase_No, Supplier_ID, Purchase_Date, Total_Amount, Payment_Status, Notes)
        VALUES (@PurchaseNo, @SupplierID, GETDATE(), @TotalAmount, 'Pending', @Notes);
        
        INSERT INTO PURCHASE_DETAIL (Purchase_No, Product_Code, Quantity, Unit_Price, Line_Total)
        SELECT @PurchaseNo, Product_Code, Quantity, Unit_Price, Quantity * Unit_Price
        FROM @Details;
        
        COMMIT TRANSACTION;
        SET @Success = 1;
        SET @CreatedKey = @PurchaseNo;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        SET @ErrorMessage = ERROR_MESSAGE();
    END CATCH
END;
GO

-- Mark purchase as received (updates inventory)
IF OBJECT_ID('usp_MarkPurchaseReceived', 'P') IS NOT NULL DROP PROCEDURE usp_MarkPurchaseReceived;
GO
CREATE PROCEDURE usp_MarkPurchaseReceived
    @PurchaseNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        IF EXISTS (SELECT 1 FROM PURCHASE WHERE Purchase_No = @PurchaseNo AND Payment_Status = 'Received')
        BEGIN
            RAISERROR('Purchase already marked as received', 16, 1);
            RETURN;
        END
        
        -- Update inventory for each item
        UPDATE i
        SET i.Current_Stock = i.Current_Stock + pd.Quantity,
            i.Last_Updated = GETDATE()
        FROM INVENTORY i
        INNER JOIN PURCHASE_DETAIL pd ON i.Product_Code = pd.Product_Code
        WHERE pd.Purchase_No = @PurchaseNo;
        
        UPDATE PURCHASE SET Payment_Status = 'Received' WHERE Purchase_No = @PurchaseNo;
        
        COMMIT TRANSACTION;
        SELECT 1 AS Success;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Cancel purchase
IF OBJECT_ID('usp_CancelPurchase', 'P') IS NOT NULL DROP PROCEDURE usp_CancelPurchase;
GO
CREATE PROCEDURE usp_CancelPurchase
    @PurchaseNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        IF EXISTS (SELECT 1 FROM PURCHASE WHERE Purchase_No = @PurchaseNo AND Payment_Status = 'Received')
        BEGIN
            RAISERROR('Cannot cancel a received purchase', 16, 1);
            RETURN;
        END
        
        DELETE FROM PURCHASE_DETAIL WHERE Purchase_No = @PurchaseNo;
        DELETE FROM PURCHASE WHERE Purchase_No = @PurchaseNo;
        
        COMMIT TRANSACTION;
        SELECT 1 AS Success;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Get last purchase info for a product
IF OBJECT_ID('usp_GetLastPurchaseForProduct', 'P') IS NOT NULL DROP PROCEDURE usp_GetLastPurchaseForProduct;
GO
CREATE PROCEDURE usp_GetLastPurchaseForProduct
    @ProductCode NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP 1
        p.Supplier_ID,
        s.Supplier_Name,
        pd.Unit_Price AS Last_Cost_Price,
        pd.Quantity AS Last_Quantity,
        p.Purchase_Date AS Last_Purchase_Date,
        p.Purchase_No
    FROM PURCHASE p
    INNER JOIN PURCHASE_DETAIL pd ON p.Purchase_No = pd.Purchase_No
    INNER JOIN SUPPLIER s ON p.Supplier_ID = s.Supplier_ID
    WHERE pd.Product_Code = @ProductCode
      AND p.Payment_Status = 'Received'
    ORDER BY p.Purchase_Date DESC, p.Purchase_No DESC;
END;
GO

-- ============================================================================
-- SALE PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListSales', 'P') IS NOT NULL DROP PROCEDURE usp_ListSales;
GO
CREATE PROCEDURE usp_ListSales
    @Limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@Limit) 
        s.Invoice_No, s.Customer_ID, s.Employee_ID, 
        s.Sale_Date, s.Sale_Time, s.Total_Amount, s.Discount, s.Net_Amount,
        c.Customer_Name, e.Employee_Name
    FROM SALE s
    INNER JOIN CUSTOMER c ON s.Customer_ID = c.Customer_ID
    INNER JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    ORDER BY s.Sale_Date DESC, s.Sale_Time DESC;
END;
GO

IF OBJECT_ID('usp_GetSaleById', 'P') IS NOT NULL DROP PROCEDURE usp_GetSaleById;
GO
CREATE PROCEDURE usp_GetSaleById
    @InvoiceNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Invoice_No, s.Customer_ID, s.Employee_ID, 
           s.Sale_Date, s.Sale_Time, s.Total_Amount, s.Discount, s.Net_Amount,
           c.Customer_Name, e.Employee_Name
    FROM SALE s
    INNER JOIN CUSTOMER c ON s.Customer_ID = c.Customer_ID
    INNER JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    WHERE s.Invoice_No = @InvoiceNo;
END;
GO

IF OBJECT_ID('usp_GetSaleDetails', 'P') IS NOT NULL DROP PROCEDURE usp_GetSaleDetails;
GO
CREATE PROCEDURE usp_GetSaleDetails
    @InvoiceNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT sd.Invoice_No, sd.Product_Code, sd.Quantity, 
           sd.Unit_Price, sd.Line_Total, p.Product_Name
    FROM SALE_DETAIL sd
    INNER JOIN PRODUCT p ON sd.Product_Code = p.Product_Code
    WHERE sd.Invoice_No = @InvoiceNo
    ORDER BY p.Product_Name;
END;
GO

IF OBJECT_ID('usp_GetSalesByCustomer', 'P') IS NOT NULL DROP PROCEDURE usp_GetSalesByCustomer;
GO
CREATE PROCEDURE usp_GetSalesByCustomer
    @CustomerId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Invoice_No, s.Customer_ID, s.Employee_ID, 
           s.Sale_Date, s.Sale_Time, s.Total_Amount, s.Discount, s.Net_Amount,
           c.Customer_Name, e.Employee_Name
    FROM SALE s
    INNER JOIN CUSTOMER c ON s.Customer_ID = c.Customer_ID
    INNER JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    WHERE s.Customer_ID = @CustomerId
    ORDER BY s.Sale_Date DESC;
END;
GO

IF OBJECT_ID('usp_GetSalesByEmployee', 'P') IS NOT NULL DROP PROCEDURE usp_GetSalesByEmployee;
GO
CREATE PROCEDURE usp_GetSalesByEmployee
    @EmployeeId NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Invoice_No, s.Customer_ID, s.Employee_ID, 
           s.Sale_Date, s.Sale_Time, s.Total_Amount, s.Discount, s.Net_Amount,
           c.Customer_Name, e.Employee_Name
    FROM SALE s
    INNER JOIN CUSTOMER c ON s.Customer_ID = c.Customer_ID
    INNER JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    WHERE s.Employee_ID = @EmployeeId
    ORDER BY s.Sale_Date DESC;
END;
GO

IF OBJECT_ID('usp_GetSalesByDateRange', 'P') IS NOT NULL DROP PROCEDURE usp_GetSalesByDateRange;
GO
CREATE PROCEDURE usp_GetSalesByDateRange
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT s.Invoice_No, s.Customer_ID, s.Employee_ID, 
           s.Sale_Date, s.Sale_Time, s.Total_Amount, s.Discount, s.Net_Amount,
           c.Customer_Name, e.Employee_Name
    FROM SALE s
    INNER JOIN CUSTOMER c ON s.Customer_ID = c.Customer_ID
    INNER JOIN EMPLOYEE e ON s.Employee_ID = e.Employee_ID
    WHERE s.Sale_Date BETWEEN @StartDate AND @EndDate
    ORDER BY s.Sale_Date DESC, s.Sale_Time DESC;
END;
GO

IF OBJECT_ID('usp_GetNextInvoiceNo', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextInvoiceNo;
GO
CREATE PROCEDURE usp_GetNextInvoiceNo
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Invoice_No, 4, 10) AS INT)), 0) + 1
    FROM SALE;
    SELECT 'INV' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextNo;
END;
GO

-- Create Sale with Table-Valued Parameter
IF OBJECT_ID('usp_CreateSale', 'P') IS NOT NULL DROP PROCEDURE usp_CreateSale;
GO
CREATE PROCEDURE usp_CreateSale
    @InvoiceNo NVARCHAR(20),
    @CustomerID NVARCHAR(10),
    @EmployeeID NVARCHAR(10),
    @Discount DECIMAL(10,2) = 0,
    @Details dbo.SaleDetailType READONLY,
    @CreatedKey NVARCHAR(20) OUTPUT,
    @Success BIT OUTPUT,
    @ErrorMessage NVARCHAR(500) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET @Success = 0;
    SET @CreatedKey = NULL;
    SET @ErrorMessage = NULL;
    
    DECLARE @TotalAmount DECIMAL(10,2);
    DECLARE @NetAmount DECIMAL(10,2);
    
    -- Validate customer
    IF NOT EXISTS (SELECT 1 FROM CUSTOMER WHERE Customer_ID = @CustomerID)
    BEGIN
        SET @ErrorMessage = 'Customer not found: ' + @CustomerID;
        RETURN;
    END
    
    -- Validate employee
    IF NOT EXISTS (SELECT 1 FROM EMPLOYEE WHERE Employee_ID = @EmployeeID)
    BEGIN
        SET @ErrorMessage = 'Employee not found: ' + @EmployeeID;
        RETURN;
    END
    
    -- Check details provided
    IF NOT EXISTS (SELECT 1 FROM @Details)
    BEGIN
        SET @ErrorMessage = 'No sale details provided';
        RETURN;
    END
    
    -- Check stock availability
    DECLARE @InsufficientStock TABLE (Product_Code NVARCHAR(20), Requested INT, Available INT);
    
    INSERT INTO @InsufficientStock (Product_Code, Requested, Available)
    SELECT d.Product_Code, d.Quantity, ISNULL(i.Current_Stock, 0)
    FROM @Details d
    LEFT JOIN INVENTORY i ON d.Product_Code = i.Product_Code
    WHERE ISNULL(i.Current_Stock, 0) < d.Quantity;
    
    IF EXISTS (SELECT 1 FROM @InsufficientStock)
    BEGIN
        SELECT TOP 1 @ErrorMessage = 'Insufficient stock for ' + Product_Code + 
               '. Requested: ' + CAST(Requested AS VARCHAR) + 
               ', Available: ' + CAST(Available AS VARCHAR)
        FROM @InsufficientStock;
        RETURN;
    END
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        SELECT @TotalAmount = SUM(Quantity * Unit_Price) FROM @Details;
        SET @NetAmount = @TotalAmount - @Discount;
        IF @NetAmount < 0 SET @NetAmount = 0;
        
        INSERT INTO SALE (Invoice_No, Customer_ID, Employee_ID, Sale_Date, Sale_Time, Total_Amount, Discount, Net_Amount)
        VALUES (@InvoiceNo, @CustomerID, @EmployeeID, CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME), @TotalAmount, @Discount, @NetAmount);
        
        INSERT INTO SALE_DETAIL (Invoice_No, Product_Code, Quantity, Unit_Price, Line_Total)
        SELECT @InvoiceNo, Product_Code, Quantity, Unit_Price, Quantity * Unit_Price
        FROM @Details;
        
        -- Update inventory
        UPDATE i
        SET i.Current_Stock = i.Current_Stock - d.Quantity,
            i.Last_Updated = GETDATE()
        FROM INVENTORY i
        INNER JOIN @Details d ON i.Product_Code = d.Product_Code;
        
        COMMIT TRANSACTION;
        SET @Success = 1;
        SET @CreatedKey = @InvoiceNo;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        SET @ErrorMessage = ERROR_MESSAGE();
    END CATCH
END;
GO

IF OBJECT_ID('usp_GetDailySalesSummary', 'P') IS NOT NULL DROP PROCEDURE usp_GetDailySalesSummary;
GO
CREATE PROCEDURE usp_GetDailySalesSummary
    @TargetDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @TargetDate IS NULL SET @TargetDate = CAST(GETDATE() AS DATE);
    
    SELECT 
        COUNT(*) AS Total_Sales,
        ISNULL(SUM(Total_Amount), 0) AS Gross_Revenue,
        ISNULL(SUM(Discount), 0) AS Total_Discount,
        ISNULL(SUM(Net_Amount), 0) AS Net_Revenue
    FROM SALE
    WHERE Sale_Date = @TargetDate;
END;
GO

IF OBJECT_ID('usp_GetTopSellingProducts', 'P') IS NOT NULL DROP PROCEDURE usp_GetTopSellingProducts;
GO
CREATE PROCEDURE usp_GetTopSellingProducts
    @Limit INT = 10,
    @StartDate DATE = NULL,
    @EndDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@Limit)
        p.Product_Code, p.Product_Name, p.Brand,
        SUM(sd.Quantity) AS Total_Quantity,
        SUM(sd.Line_Total) AS Total_Revenue
    FROM SALE_DETAIL sd
    INNER JOIN PRODUCT p ON sd.Product_Code = p.Product_Code
    INNER JOIN SALE s ON sd.Invoice_No = s.Invoice_No
    WHERE (@StartDate IS NULL OR s.Sale_Date >= @StartDate)
      AND (@EndDate IS NULL OR s.Sale_Date <= @EndDate)
    GROUP BY p.Product_Code, p.Product_Name, p.Brand
    ORDER BY Total_Quantity DESC;
END;
GO

IF OBJECT_ID('usp_GetSalesByCategory', 'P') IS NOT NULL DROP PROCEDURE usp_GetSalesByCategory;
GO
CREATE PROCEDURE usp_GetSalesByCategory
    @StartDate DATE = NULL,
    @EndDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        c.Cat_ID, c.Cat_Name,
        COUNT(DISTINCT s.Invoice_No) AS Sale_Count,
        ISNULL(SUM(sd.Quantity), 0) AS Total_Quantity,
        ISNULL(SUM(sd.Line_Total), 0) AS Total_Revenue
    FROM CATEGORY c
    LEFT JOIN SUBCATEGORY sub ON c.Cat_ID = sub.Cat_ID
    LEFT JOIN PRODUCT p ON sub.Subcat_ID = p.Subcat_ID
    LEFT JOIN SALE_DETAIL sd ON p.Product_Code = sd.Product_Code
    LEFT JOIN SALE s ON sd.Invoice_No = s.Invoice_No
    WHERE (@StartDate IS NULL OR CAST(s.Sale_Date AS DATE) >= @StartDate)
      AND (@EndDate IS NULL OR CAST(s.Sale_Date AS DATE) <= @EndDate)
    GROUP BY c.Cat_ID, c.Cat_Name
    ORDER BY Total_Revenue DESC;
END;
GO

-- ============================================================================
-- PAYMENT PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_ListPayments', 'P') IS NOT NULL DROP PROCEDURE usp_ListPayments;
GO
CREATE PROCEDURE usp_ListPayments
    @Limit INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@Limit) Payment_ID, Invoice_No, Payment_Method, Amount_Paid, Payment_Date
    FROM PAYMENT
    ORDER BY Payment_Date DESC;
END;
GO

IF OBJECT_ID('usp_GetPaymentById', 'P') IS NOT NULL DROP PROCEDURE usp_GetPaymentById;
GO
CREATE PROCEDURE usp_GetPaymentById
    @PaymentId NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Payment_ID, Invoice_No, Payment_Method, Amount_Paid, Payment_Date
    FROM PAYMENT
    WHERE Payment_ID = @PaymentId;
END;
GO

IF OBJECT_ID('usp_GetPaymentsBySale', 'P') IS NOT NULL DROP PROCEDURE usp_GetPaymentsBySale;
GO
CREATE PROCEDURE usp_GetPaymentsBySale
    @InvoiceNo NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT Payment_ID, Invoice_No, Payment_Method, Amount_Paid, Payment_Date
    FROM PAYMENT
    WHERE Invoice_No = @InvoiceNo
    ORDER BY Payment_Date;
END;
GO

IF OBJECT_ID('usp_AddPayment', 'P') IS NOT NULL DROP PROCEDURE usp_AddPayment;
GO
CREATE PROCEDURE usp_AddPayment
    @PaymentId NVARCHAR(20),
    @InvoiceNo NVARCHAR(20),
    @PaymentMethod NVARCHAR(30),
    @AmountPaid DECIMAL(10,2),
    @PaymentDate DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @PaymentDate IS NULL SET @PaymentDate = GETDATE();
    
    INSERT INTO PAYMENT (Payment_ID, Invoice_No, Payment_Method, Amount_Paid, Payment_Date)
    VALUES (@PaymentId, @InvoiceNo, @PaymentMethod, @AmountPaid, @PaymentDate);
END;
GO

IF OBJECT_ID('usp_GetNextPaymentId', 'P') IS NOT NULL DROP PROCEDURE usp_GetNextPaymentId;
GO
CREATE PROCEDURE usp_GetNextPaymentId
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @NextNum INT;
    SELECT @NextNum = ISNULL(MAX(CAST(SUBSTRING(Payment_ID, 4, 10) AS INT)), 0) + 1
    FROM PAYMENT;
    SELECT 'PAY' + RIGHT('000' + CAST(@NextNum AS VARCHAR), 3) AS NextId;
END;
GO

-- ============================================================================
-- DASHBOARD / REPORTING PROCEDURES
-- ============================================================================

IF OBJECT_ID('usp_GetDashboardStats', 'P') IS NOT NULL DROP PROCEDURE usp_GetDashboardStats;
GO
CREATE PROCEDURE usp_GetDashboardStats
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Today's sales
    DECLARE @TodaySales DECIMAL(10,2), @TodayCount INT;
    SELECT @TodaySales = ISNULL(SUM(Net_Amount), 0), @TodayCount = COUNT(*)
    FROM SALE WHERE Sale_Date = CAST(GETDATE() AS DATE);
    
    -- Total products and low stock
    DECLARE @TotalProducts INT, @LowStock INT;
    SELECT @TotalProducts = COUNT(*) FROM PRODUCT;
    SELECT @LowStock = COUNT(*)
    FROM PRODUCT p
    LEFT JOIN INVENTORY i ON p.Product_Code = i.Product_Code
    WHERE ISNULL(i.Current_Stock, 0) <= p.Min_Stock_Level;
    
    -- Pending purchases
    DECLARE @PendingPurchases INT;
    SELECT @PendingPurchases = COUNT(*) FROM PURCHASE WHERE Payment_Status = 'Pending';
    
    -- Inventory value
    DECLARE @InventoryValue DECIMAL(12,2);
    SELECT @InventoryValue = ISNULL(SUM(i.Current_Stock * p.Cost_Price), 0)
    FROM INVENTORY i
    INNER JOIN PRODUCT p ON i.Product_Code = p.Product_Code;
    
    SELECT 
        @TodaySales AS TodaySales,
        @TodayCount AS TodaySaleCount,
        @TotalProducts AS TotalProducts,
        @LowStock AS LowStockCount,
        @PendingPurchases AS PendingPurchases,
        @InventoryValue AS InventoryValue;
END;
GO

-- ============================================================================
-- SALES REPORT PROCEDURE (with Profit Calculation)
-- ============================================================================

IF OBJECT_ID('usp_GetSalesReport', 'P') IS NOT NULL DROP PROCEDURE usp_GetSalesReport;
GO
CREATE PROCEDURE usp_GetSalesReport
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Summary totals with profit calculation
    -- Profit = Total Revenue - Total Cost (Cost_Price from PRODUCT table)
    SELECT 
        COUNT(DISTINCT s.Invoice_No) AS Total_Sales,
        ISNULL(SUM(sd.Quantity), 0) AS Total_Units_Sold,
        ISNULL(SUM(s.Net_Amount), 0) AS Total_Revenue,
        ISNULL(SUM(sd.Quantity * p.Cost_Price), 0) AS Total_Cost,
        ISNULL(SUM(s.Net_Amount), 0) - ISNULL(SUM(sd.Quantity * p.Cost_Price), 0) AS Gross_Profit
    FROM SALE s
    LEFT JOIN SALE_DETAIL sd ON s.Invoice_No = sd.Invoice_No
    LEFT JOIN PRODUCT p ON sd.Product_Code = p.Product_Code
    WHERE CAST(s.Sale_Date AS DATE) BETWEEN @StartDate AND @EndDate;
END;
GO

-- ============================================================================
PRINT '========================================';
PRINT 'All stored procedures created successfully!';
PRINT '========================================';
GO
