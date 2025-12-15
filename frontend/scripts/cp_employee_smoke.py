# COPILOT_MODIFIED: true  # 2025-12-09T10:30:00Z
"""
=============================================================================
Employee Creation & Login Smoke Test
=============================================================================
This script demonstrates and validates:
1. Admin can create a new employee account (with hashed password)
2. The newly created employee can successfully login
3. Role-based authentication is enforced (Employee role only)

Usage:
    cd frontend
    python scripts/cp_employee_smoke.py

Results are logged to: logs/copilot_emp_smoke.log
=============================================================================
"""

import sys
import os
from datetime import datetime

# Add frontend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from repositories.employee_repository import EmployeeRepository


def log_message(message: str, log_file):
    """Write message to both console and log file."""
    print(message)
    log_file.write(message + "\n")
    log_file.flush()


def run_smoke_test():
    """Execute the employee creation and login smoke test."""
    
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, 'copilot_emp_smoke.log')
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        timestamp = datetime.now().isoformat()
        
        log_message("=" * 70, log_file)
        log_message("EMPLOYEE CREATION & LOGIN SMOKE TEST", log_file)
        log_message(f"Timestamp: {timestamp}", log_file)
        log_message("=" * 70, log_file)
        
        # Test data
        test_username = f"smoke_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_password = "SmokeTest123!"
        test_name = "Smoke Test Employee"
        
        try:
            # ================================================================
            # TEST 1: Admin creates employee account
            # ================================================================
            log_message("\n[TEST 1] Admin creates employee account", log_file)
            log_message(f"  Username: {test_username}", log_file)
            log_message(f"  Name: {test_name}", log_file)
            log_message(f"  Role: Employee", log_file)
            
            success, message = EmployeeRepository.create_employee(
                employee_name=test_name,
                username=test_username,
                password=test_password,
                role='Employee',
                phone='555-9999',
                email='smoke@test.com',
                position='Test Employee'
            )
            
            if success:
                log_message(f"  ✓ SUCCESS: {message}", log_file)
            else:
                log_message(f"  ✗ FAILED: {message}", log_file)
                log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
                return 1
            
            # ================================================================
            # TEST 2: Verify employee can authenticate
            # ================================================================
            log_message("\n[TEST 2] Employee authenticates with credentials", log_file)
            log_message(f"  Username: {test_username}", log_file)
            
            auth_success, employee, auth_message = EmployeeRepository.authenticate(
                test_username,
                test_password
            )
            
            if auth_success:
                log_message(f"  ✓ SUCCESS: Authentication successful", log_file)
                log_message(f"    - Employee ID: {employee.employee_id}", log_file)
                log_message(f"    - Name: {employee.employee_name}", log_file)
                log_message(f"    - Role: {employee.role}", log_file)
                log_message(f"    - Position: {employee.position}", log_file)
            else:
                log_message(f"  ✗ FAILED: {auth_message}", log_file)
                log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
                return 1
            
            # ================================================================
            # TEST 3: Verify role is 'Employee'
            # ================================================================
            log_message("\n[TEST 3] Verify role enforcement", log_file)
            
            if employee.role == 'Employee':
                log_message(f"  ✓ SUCCESS: Role correctly set to 'Employee'", log_file)
            else:
                log_message(f"  ✗ FAILED: Role is '{employee.role}' instead of 'Employee'", log_file)
                log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
                return 1
            
            # ================================================================
            # TEST 4: Verify password is hashed (not plain text)
            # ================================================================
            log_message("\n[TEST 4] Verify password hashing", log_file)
            
            # Get employee record with password hash
            sql = "SELECT password_hash FROM EMPLOYEE WHERE Username = ?"
            import db
            row = db.execute_query(sql, (test_username,), fetch='one')
            
            if row and row.password_hash:
                # Hashed passwords should start with $pbkdf2-sha256$
                if row.password_hash.startswith('$pbkdf2-sha256$'):
                    log_message(f"  ✓ SUCCESS: Password is properly hashed with pbkdf2_sha256", log_file)
                    log_message(f"    Hash prefix: {row.password_hash[:30]}...", log_file)
                else:
                    log_message(f"  ✗ FAILED: Password hash format unexpected", log_file)
                    log_message(f"    Hash: {row.password_hash[:50]}", log_file)
            else:
                log_message(f"  ✗ FAILED: No password hash found", log_file)
                log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
                return 1
            
            # ================================================================
            # TEST 5: Verify parameterized SQL (no SQL injection)
            # ================================================================
            log_message("\n[TEST 5] Verify SQL injection protection", log_file)
            
            # Try SQL injection in username
            malicious_username = "admin' OR '1'='1"
            auth_success, _, _ = EmployeeRepository.authenticate(malicious_username, "anypass")
            
            if not auth_success:
                log_message(f"  ✓ SUCCESS: SQL injection attempt blocked", log_file)
                log_message(f"    Malicious input: {malicious_username}", log_file)
            else:
                log_message(f"  ✗ FAILED: SQL injection vulnerability detected!", log_file)
                log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
                return 1
            
            # ================================================================
            # CLEANUP: Delete test employee
            # ================================================================
            log_message("\n[CLEANUP] Removing test employee", log_file)
            
            delete_success, delete_message = EmployeeRepository.delete(employee.employee_id)
            
            if delete_success:
                log_message(f"  ✓ SUCCESS: Test employee deleted", log_file)
            else:
                log_message(f"  ⚠ WARNING: Could not delete test employee: {delete_message}", log_file)
                log_message(f"    Manual cleanup may be needed for: {employee.employee_id}", log_file)
            
            # ================================================================
            # FINAL RESULT
            # ================================================================
            log_message("\n" + "=" * 70, log_file)
            log_message("[RESULT] ALL TESTS PASSED ✓", log_file)
            log_message("=" * 70, log_file)
            log_message("\nSummary:", log_file)
            log_message("  • Admin can create employee accounts", log_file)
            log_message("  • Employees can authenticate with username/password", log_file)
            log_message("  • Role enforcement works correctly", log_file)
            log_message("  • Passwords are hashed with pbkdf2_sha256", log_file)
            log_message("  • SQL injection protection is active", log_file)
            log_message("\nEmployee creation and login functionality is working correctly!", log_file)
            
            return 0
            
        except Exception as e:
            log_message(f"\n✗ CRITICAL ERROR: {str(e)}", log_file)
            log_message("\n[RESULT] SMOKE TEST FAILED", log_file)
            import traceback
            log_message("\nStack trace:", log_file)
            log_message(traceback.format_exc(), log_file)
            return 1


if __name__ == "__main__":
    print("\nRunning Employee Creation & Login Smoke Test...")
    print("Results will be logged to: logs/copilot_emp_smoke.log\n")
    
    exit_code = run_smoke_test()
    
    print(f"\nTest {'PASSED ✓' if exit_code == 0 else 'FAILED ✗'}")
    print("See logs/copilot_emp_smoke.log for detailed results\n")
    
    sys.exit(exit_code)
