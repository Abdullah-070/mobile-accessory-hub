# COPILOT_MODIFIED: true  # 2025-12-09T10:30:00Z
"""
=============================================================================
Role Selection View
=============================================================================
Initial screen showing Admin and Employee role choices.
- Admin: Login + Sign Up (requires ADMIN_SETUP_CODE)
- Employee: Login ONLY (no self-signup; Admin creates employee accounts)
Modified to enforce admin-only employee creation policy.
=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class RoleTile(QFrame):
    """Tile widget for role selection with Login/SignUp buttons."""
    
    login_clicked = Signal()
    signup_clicked = Signal()
    
    def __init__(self, icon: str, title: str, description: str, color: str, show_signup: bool = True, parent=None):
        super().__init__(parent)
        self.color = color
        self.show_signup = show_signup
        self._setup_ui(icon, title, description)
    
    def _setup_ui(self, icon: str, title: str, description: str):
        self.setFixedSize(280, 320)
        self.setStyleSheet(f"""
            RoleTile {{
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 12px;
            }}
            RoleTile:hover {{
                border-color: {self.color};
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 30, 25, 25)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 48pt;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #757575; font-size: 10pt;")
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Login button
        self.login_btn = QPushButton("🔐 Login")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {self.color}DD; }}
        """)
        self.login_btn.clicked.connect(self.login_clicked.emit)
        layout.addWidget(self.login_btn)
        
        # Sign Up button (conditional)
        if self.show_signup:
            self.signup_btn = QPushButton("📝 Sign Up")
            self.signup_btn.setMinimumHeight(45)
            self.signup_btn.setCursor(Qt.PointingHandCursor)
            self.signup_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.color};
                    border: 2px solid {self.color};
                    border-radius: 6px;
                    font-size: 11pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {self.color}15; }}
            """)
            self.signup_btn.clicked.connect(self.signup_clicked.emit)
            layout.addWidget(self.signup_btn)


class RoleSelectionView(QWidget):
    """
    Initial role selection screen.
    
    Signals:
        admin_login_requested: User wants to login as Admin
        admin_signup_requested: User wants to signup as Admin
        employee_login_requested: User wants to login as Employee
    
    Note: Employee signup removed - only admins can create employee accounts
    """
    
    admin_login_requested = Signal()
    admin_signup_requested = Signal()
    employee_login_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setWindowTitle("Mobile Accessory Inventory - Select Role")
        self.setMinimumSize(700, 550)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Top stretch
        main_layout.addStretch(1)
        
        # Header
        header = QLabel("📱 Mobile Accessory Inventory")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(22)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #1976D2;")
        main_layout.addWidget(header)
        
        subtitle = QLabel("Select your role to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #757575; font-size: 12pt;")
        main_layout.addWidget(subtitle)
        
        main_layout.addSpacing(40)
        
        # Tiles container
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(40)
        tiles_layout.setAlignment(Qt.AlignCenter)
        
        # Admin tile
        admin_tile = RoleTile(
            "👨‍💼", "Admin",
            "Full system access\nManage employees & reports",
            "#1976D2",
            show_signup=True
        )
        admin_tile.login_clicked.connect(self.admin_login_requested.emit)
        admin_tile.signup_clicked.connect(self.admin_signup_requested.emit)
        tiles_layout.addWidget(admin_tile)
        
        # Employee tile (Login only - no signup)
        employee_tile = RoleTile(
            "👤", "Employee",
            "POS & inventory access\nContact admin for account",
            "#4CAF50",
            show_signup=False
        )
        employee_tile.login_clicked.connect(self.employee_login_requested.emit)
        tiles_layout.addWidget(employee_tile)
        
        main_layout.addLayout(tiles_layout)
        
        # Bottom stretch
        main_layout.addStretch(1)
        
        # Footer
        footer = QLabel("© 2024 Mobile Accessory Inventory System")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #9E9E9E; font-size: 9pt;")
        main_layout.addWidget(footer)
