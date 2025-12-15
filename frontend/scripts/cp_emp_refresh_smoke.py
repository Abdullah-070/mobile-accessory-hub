# COPILOT_MODIFIED: true  # 2025-12-09T14:45:00Z
"""
Employee Refresh Smoke Test
Verifies get_all_employees() method works correctly.
"""

import sys
import os
from datetime import datetime

# Add frontend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_smoke_test():
    """Test get_all_employees method."""
    try:
        from repositories.employee_repository import EmployeeRepository
        
        employees = EmployeeRepository.get_all_employees()
        
        result = f"""
=============================================================================
Employee Refresh Smoke Test
Timestamp: {datetime.now().isoformat()}
=============================================================================

get_all_employees() returned {len(employees)} employees

Sample data (first 3):
"""
        for i, emp in enumerate(employees[:3]):
            result += f"\n{i+1}. ID: {emp.get('employee_id')}, Name: {emp.get('employee_name')}, Role: {emp.get('role')}"
        
        result += "\n\n✓ TEST PASSED: get_all_employees() works correctly\n"
        
        return result
        
    except Exception as e:
        return f"""
=============================================================================
Employee Refresh Smoke Test
Timestamp: {datetime.now().isoformat()}
=============================================================================

✗ TEST FAILED: {str(e)}

"""

if __name__ == "__main__":
    result = run_smoke_test()
    print(result)
    
    # Write to log file
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, 'copilot_emp_refresh.log')
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\nLog written to: {log_path}")
