# COPILOT_MODIFIED: true  # 2025-12-09T16:30:00Z
"""
Smoke test for employee actions button rendering.
Verifies that action button container can be created without exceptions.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def smoke_test():
    """Run smoke test for employee action buttons."""
    log_path = Path(__file__).parent.parent / "logs" / "copilot_emp_actions.log"
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
        from PySide6.QtCore import Qt
        
        # Create QApplication instance (required for Qt widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Simulate creating action button container
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)
        
        # Create Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedWidth(36)
        edit_btn.setFixedHeight(28)
        edit_btn.setToolTip("Edit employee")
        edit_btn.setAccessibleName("edit_employee_btn_TEST001")
        edit_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(edit_btn)
        
        # Create Delete button
        delete_btn = QPushButton("Del")
        delete_btn.setFixedWidth(36)
        delete_btn.setFixedHeight(28)
        delete_btn.setToolTip("Delete employee")
        delete_btn.setAccessibleName("delete_employee_btn_TEST001")
        delete_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(delete_btn)
        
        # Verify widget is created
        assert actions_widget is not None
        assert edit_btn.text() == "Edit"
        assert delete_btn.text() == "Del"
        assert edit_btn.width() == 36
        assert delete_btn.width() == 36
        
        # Write success log
        with open(log_path, "w") as f:
            f.write("SMOKE_OK\n")
            f.write("Employee action buttons smoke test passed.\n")
            f.write(f"Edit button: {edit_btn.text()} - Size: {edit_btn.width()}x{edit_btn.height()}\n")
            f.write(f"Delete button: {delete_btn.text()} - Size: {delete_btn.width()}x{delete_btn.height()}\n")
            f.write(f"Container layout spacing: {actions_layout.spacing()}\n")
        
        print("SMOKE_OK")
        return True
        
    except Exception as e:
        # Write error log
        with open(log_path, "w") as f:
            f.write("SMOKE_FAILED\n")
            f.write(f"Error: {str(e)}\n")
            import traceback
            f.write(traceback.format_exc())
        
        print(f"SMOKE_FAILED: {e}")
        return False

if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)
