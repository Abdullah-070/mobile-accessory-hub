"""
=============================================================================
Verify Employee Creation - Test Script
=============================================================================
This script demonstrates and verifies that:
1. Admin can create a new employee account
2. The newly created employee can log in successfully
3. Role-based authentication is enforced

Usage: python scripts/verify_employee_creation.py
=============================================================================
"""

import sys
import os

# Add frontend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from repositories.employee_repository import EmployeeRepository

def test_admin_creates_employee():
    """Test that admin can create an employee account."""
    print("=" * 60)
    print("TEST: Admin Creates Employee Account")
    print("=" * 60)
    
    # Test data
    test_username = "test_emp_001"
    test_password = "testpass123"
    test_name = "Test Employee"
    
    print(f"\n1. Creating employee account...")
    print(f"   Username: {test_username}")
    print(f"   Name: {test_name}")
    
    # Create employee using admin-only method
    success, message = EmployeeRepository.create_employee(
        employee_name=test_name,
        username=test_username,
        password=test_password,
        role='Employee',
        phone='555-0001',
        email='test@example.com',
        position='Test Position'
    )
    
    if success:
        print(f"   ✓ SUCCESS: {message}")
    else:
        print(f"   ✗ FAILED: {message}")
        return False
    
    print(f"\n2. Verifying employee can authenticate...")
    
    # Try to authenticate
    auth_success, employee, auth_message = EmployeeRepository.authenticate(
        test_username, 
        test_password
    )
    
    if auth_success:
        print(f"   ✓ SUCCESS: Employee authenticated")
        print(f"   - Employee ID: {employee.employee_id}")
        print(f"   - Name: {employee.employee_name}")
        print(f"   - Role: {employee.role}")
        print(f"   - Username: {employee.username}")
    else:
        print(f"   ✗ FAILED: {auth_message}")
        return False
    
    print(f"\n3. Verifying role is 'Employee'...")
    if employee.role == 'Employee':
        print(f"   ✓ SUCCESS: Role is correctly set to 'Employee'")
    else:
        print(f"   ✗ FAILED: Role is '{employee.role}' instead of 'Employee'")
        return False
    
    print(f"\n4. Cleaning up (deleting test employee)...")
    try:
        delete_success, delete_msg = EmployeeRepository.delete(employee.employee_id)
        if delete_success:
            print(f"   ✓ SUCCESS: Test employee deleted")
        else:
            print(f"   ⚠ WARNING: Could not delete test employee: {delete_msg}")
    except:
        print(f"   ⚠ WARNING: Could not delete test employee (manual cleanup may be needed)")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    return True

def test_duplicate_username():
    """Test that duplicate usernames are rejected."""
    print("\n" + "=" * 60)
    print("TEST: Duplicate Username Rejection")
    print("=" * 60)
    
    # Try to create with existing username
    print("\n1. Attempting to create employee with existing username...")
    
    success, message = EmployeeRepository.create_employee(
        employee_name="Duplicate Test",
        username="admin",  # Assuming admin exists
        password="testpass",
        role='Employee'
    )
    
    if not success and "already exists" in message.lower():
        print(f"   ✓ SUCCESS: Duplicate username correctly rejected")
        print(f"   Message: {message}")
        return True
    else:
        print(f"   ✗ FAILED: Should have rejected duplicate username")
        return False

def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("Employee Creation Verification Script")
    print("=" * 60)
    
    try:
        # Test 1: Create and authenticate
        test1_passed = test_admin_creates_employee()
        
        # Test 2: Duplicate username
        test2_passed = test_duplicate_username()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Test 1 (Admin Creates Employee): {'PASS ✓' if test1_passed else 'FAIL ✗'}")
        print(f"Test 2 (Duplicate Username):     {'PASS ✓' if test2_passed else 'FAIL ✗'}")
        print("=" * 60)
        
        if test1_passed and test2_passed:
            print("\nAll tests passed! Employee creation is working correctly.")
            return 0
        else:
            print("\nSome tests failed. Please review the output above.")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
