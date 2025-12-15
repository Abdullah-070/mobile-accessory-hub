"""
=============================================================================
Purchase View
=============================================================================
Displays all purchases with filtering, monthly totals, and details.

Features:
    - List all purchases with supplier, date, amount
    - Filter by date range (month/custom)
    - Show monthly purchase totals
    - View purchase details
    - Track payment status

=============================================================================
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QFrame, QHeaderView, QMessageBox,
    QDateEdit, QGroupBox, QGridLayout, QDialog, QTextEdit, QScrollArea,
    QCalendarWidget
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import List, Optional

from repositories.purchase_repository import PurchaseRepository, Purchase


class PurchaseDetailDialog(QDialog):
    """Dialog to show purchase details with action buttons."""
    
    # Signal emitted when purchase status changes
    purchase_updated = Signal()
    
    def __init__(self, purchase: Purchase, parent=None):
        super().__init__(parent)
        self.purchase = purchase
        self.setWindowTitle(f"Purchase Details - {purchase.purchase_no}")
        self.setMinimumSize(750, 650)
        self.resize(700, 600)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header info
        header_group = QGroupBox("Purchase Information")
        header_layout = QGridLayout(header_group)
        
        header_layout.addWidget(QLabel("Purchase No:"), 0, 0)
        header_layout.addWidget(QLabel(f"<b>{self.purchase.purchase_no}</b>"), 0, 1)
        
        header_layout.addWidget(QLabel("Supplier:"), 0, 2)
        header_layout.addWidget(QLabel(f"<b>{self.purchase.supplier_name or self.purchase.supplier_id}</b>"), 0, 3)
        
        header_layout.addWidget(QLabel("Date:"), 1, 0)
        header_layout.addWidget(QLabel(f"<b>{self.purchase.purchase_date}</b>"), 1, 1)
        
        header_layout.addWidget(QLabel("Status:"), 1, 2)
        self.status_label = QLabel(f"<b>{self.purchase.payment_status}</b>")
        if self.purchase.payment_status == "Received":
            self.status_label.setStyleSheet("color: green;")
        elif self.purchase.payment_status == "Pending":
            self.status_label.setStyleSheet("color: orange;")
        header_layout.addWidget(self.status_label, 1, 3)
        
        layout.addWidget(header_group)
        
        # Items table
        items_group = QGroupBox("Items Ordered")
        items_layout = QVBoxLayout(items_group)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Product Code", "Product Name", "Quantity", "Unit Price", "Line Total"
        ])
        self.items_table.setMinimumHeight(200)
        
        # Better column sizing
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.verticalHeader().setVisible(False)
        
        # Load details
        if self.purchase.details:
            self.items_table.setRowCount(len(self.purchase.details))
            for row, detail in enumerate(self.purchase.details):
                self.items_table.setItem(row, 0, QTableWidgetItem(detail.product_code))
                self.items_table.setItem(row, 1, QTableWidgetItem(detail.product_name or ""))
                self.items_table.setItem(row, 2, QTableWidgetItem(str(detail.quantity)))
                self.items_table.setItem(row, 3, QTableWidgetItem(f"Rs. {detail.unit_price:.2f}"))
                self.items_table.setItem(row, 4, QTableWidgetItem(f"Rs. {detail.line_total:.2f}"))
        
        items_layout.addWidget(self.items_table)
        layout.addWidget(items_group)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_label = QLabel(f"<h2>Total: Rs. {self.purchase.total_amount:.2f}</h2>")
        total_label.setStyleSheet("color: #2196F3;")
        total_layout.addWidget(total_label)
        layout.addLayout(total_layout)
        
        # Notes
        if self.purchase.notes:
            notes_group = QGroupBox("Notes")
            notes_layout = QVBoxLayout(notes_group)
            notes_text = QLabel(self.purchase.notes)
            notes_text.setWordWrap(True)
            notes_layout.addWidget(notes_text)
            layout.addWidget(notes_group)
        
        # =====================================================================
        # ACTION BUTTONS
        # =====================================================================
        actions_layout = QHBoxLayout()
        
        # Show action buttons only for pending orders
        if self.purchase.payment_status == "Pending":
            # Mark as Received button (Green)
            self.receive_btn = QPushButton("✓ Mark as Received")
            self.receive_btn.setMinimumHeight(45)
            self.receive_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.receive_btn.clicked.connect(self._mark_as_received)
            actions_layout.addWidget(self.receive_btn)
            
            # Cancel Order button (Red)
            self.cancel_btn = QPushButton("✗ Cancel Order")
            self.cancel_btn.setMinimumHeight(45)
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.cancel_btn.clicked.connect(self._cancel_order)
            actions_layout.addWidget(self.cancel_btn)
        else:
            # Show completed status message
            completed_label = QLabel("✓ This order has been received")
            completed_label.setStyleSheet("color: green; font-size: 14px; font-weight: bold;")
            actions_layout.addWidget(completed_label)
        
        actions_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        actions_layout.addWidget(close_btn)
        
        layout.addLayout(actions_layout)
    
    def _mark_as_received(self):
        """Mark the purchase as received and update inventory."""
        reply = QMessageBox.question(
            self,
            "Confirm Receipt",
            f"Mark this order as received?\n\n"
            f"This will add the ordered quantities to your inventory.\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = PurchaseRepository.mark_as_received(self.purchase.purchase_no)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.purchase_updated.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)
    
    def _cancel_order(self):
        """Cancel the pending purchase order."""
        reply = QMessageBox.question(
            self,
            "Confirm Cancellation",
            f"Are you sure you want to cancel this order?\n\n"
            f"Purchase No: {self.purchase.purchase_no}\n"
            f"Total: Rs. {self.purchase.total_amount:.2f}\n\n"
            f"This will delete the purchase record. This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = PurchaseRepository.cancel_purchase(self.purchase.purchase_no)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.purchase_updated.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)


class PurchaseView(QWidget):
    """
    Widget for viewing and managing purchases.
    
    Shows all purchases with monthly totals and filtering options.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.purchases: List[Purchase] = []
        self._setup_ui()
        self._load_purchases()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # =====================================================================
        # HEADER
        # =====================================================================
        header_layout = QHBoxLayout()
        
        title = QLabel("Purchase History")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMinimumHeight(35)
        refresh_btn.clicked.connect(self._load_purchases)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # =====================================================================
        # SUMMARY CARDS
        # =====================================================================
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # This Month's Purchases
        self.month_card = self._create_summary_card(
            "This Month's Purchases",
            "Rs. 0.00",
            "#2196F3"
        )
        summary_layout.addWidget(self.month_card)
        
        # Total Purchases (All Time)
        self.total_card = self._create_summary_card(
            "Total Purchases (All Time)",
            "Rs. 0.00",
            "#4CAF50"
        )
        summary_layout.addWidget(self.total_card)
        
        # Pending Payments
        self.pending_card = self._create_summary_card(
            "Pending Payments",
            "Rs. 0.00",
            "#FF9800"
        )
        summary_layout.addWidget(self.pending_card)
        
        # Purchase Count
        self.count_card = self._create_summary_card(
            "Total Orders",
            "0",
            "#9C27B0"
        )
        summary_layout.addWidget(self.count_card)
        
        main_layout.addLayout(summary_layout)
        
        # =====================================================================
        # FILTERS
        # =====================================================================
        filter_group = QGroupBox("Filter by Date")
        filter_layout = QHBoxLayout(filter_group)
        
        # Quick filters
        filter_layout.addWidget(QLabel("Quick Filter:"))
        self.quick_filter_combo = QComboBox()
        self.quick_filter_combo.addItems([
            "All Time",
            "This Month",
            "Last Month",
            "This Year",
            "Custom Range"
        ])
        self.quick_filter_combo.currentIndexChanged.connect(self._on_quick_filter_changed)
        filter_layout.addWidget(self.quick_filter_combo)
        
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(False)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setDisplayFormat("dd/MM/yyyy")
        self.from_date.setMinimumWidth(120)
        self.from_date.setMinimumHeight(35)
        filter_layout.addWidget(self.from_date)
        
        # Calendar button for from date
        self.from_cal_btn = QPushButton("📅")
        self.from_cal_btn.setFixedSize(38, 35)
        self.from_cal_btn.setCursor(Qt.PointingHandCursor)
        self.from_cal_btn.setToolTip("Open Calendar")
        self.from_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.from_cal_btn.clicked.connect(lambda: self._show_calendar(self.from_date))
        filter_layout.addWidget(self.from_cal_btn)
        
        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(False)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setDisplayFormat("dd/MM/yyyy")
        self.to_date.setMinimumWidth(120)
        self.to_date.setMinimumHeight(35)
        filter_layout.addWidget(self.to_date)
        
        # Calendar button for to date
        self.to_cal_btn = QPushButton("📅")
        self.to_cal_btn.setFixedSize(38, 35)
        self.to_cal_btn.setCursor(Qt.PointingHandCursor)
        self.to_cal_btn.setToolTip("Open Calendar")
        self.to_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        self.to_cal_btn.clicked.connect(lambda: self._show_calendar(self.to_date))
        filter_layout.addWidget(self.to_cal_btn)
        
        apply_btn = QPushButton("Apply Filter")
        apply_btn.clicked.connect(self._apply_filter)
        filter_layout.addWidget(apply_btn)
        
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_group)
        
        # =====================================================================
        # PURCHASES TABLE
        # =====================================================================
        self.purchase_table = QTableWidget()
        self.purchase_table.setColumnCount(7)
        self.purchase_table.setHorizontalHeaderLabels([
            "Purchase No", "Date", "Supplier", "Items", "Total Amount", "Status", "Actions"
        ])
        
        # Table settings
        header = self.purchase_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.resizeSection(6, 120)
        
        self.purchase_table.setAlternatingRowColors(True)
        self.purchase_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.purchase_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.purchase_table.verticalHeader().setDefaultSectionSize(50)
        
        main_layout.addWidget(self.purchase_table)
        
        # =====================================================================
        # STATUS BAR
        # =====================================================================
        self.status_label = QLabel("Loading purchases...")
        main_layout.addWidget(self.status_label)
    
    def _create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card widget."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        card.setMinimumHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card
    
    def _update_card_value(self, card: QFrame, value: str):
        """Update a summary card's value."""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def _on_quick_filter_changed(self, index: int):
        """Handle quick filter selection."""
        # Enable/disable custom date range
        is_custom = index == 4  # "Custom Range"
        self.from_date.setEnabled(is_custom)
        self.to_date.setEnabled(is_custom)
        
        if not is_custom:
            self._apply_filter()
    
    def _show_calendar(self, date_edit: QDateEdit):
        """Show calendar popup for the given date edit widget."""
        from PySide6.QtWidgets import QCalendarWidget
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date")
        dialog.setMinimumSize(400, 350)
        
        layout = QVBoxLayout(dialog)
        
        calendar = QCalendarWidget()
        calendar.setSelectedDate(date_edit.date())
        calendar.setGridVisible(True)
        calendar.setMinimumSize(380, 280)
        # Hide week numbers
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        layout.addWidget(calendar)
        
        btn_layout = QHBoxLayout()
        
        today_btn = QPushButton("Today")
        today_btn.setMinimumHeight(35)
        today_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; border: none; border-radius: 5px; font-weight: bold; padding: 8px 20px; } QPushButton:hover { background-color: #F57C00; }")
        today_btn.clicked.connect(lambda: calendar.setSelectedDate(QDate.currentDate()))
        btn_layout.addWidget(today_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setStyleSheet("QPushButton { background-color: #757575; color: white; border: none; border-radius: 5px; padding: 8px 20px; } QPushButton:hover { background-color: #616161; }")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Select")
        ok_btn.setMinimumHeight(35)
        ok_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-weight: bold; padding: 8px 20px; } QPushButton:hover { background-color: #388E3C; }")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        calendar.activated.connect(dialog.accept)
        
        if dialog.exec() == QDialog.Accepted:
            date_edit.setDate(calendar.selectedDate())
            self.quick_filter_combo.setCurrentText("Custom Range")

    def _apply_filter(self):
        """Apply the selected filter and reload data."""
        self._load_purchases()
    
    def _get_date_range(self) -> tuple:
        """Get the date range based on selected filter."""
        filter_index = self.quick_filter_combo.currentIndex()
        today = date.today()
        
        if filter_index == 0:  # All Time
            return None, None
        elif filter_index == 1:  # This Month
            start = today.replace(day=1)
            return start, today
        elif filter_index == 2:  # Last Month
            first_of_this_month = today.replace(day=1)
            last_month_end = first_of_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end
        elif filter_index == 3:  # This Year
            start = today.replace(month=1, day=1)
            return start, today
        elif filter_index == 4:  # Custom Range
            return self.from_date.date().toPython(), self.to_date.date().toPython()
        
        return None, None
    
    def _load_purchases(self):
        """Load purchases from database."""
        try:
            # Get all purchases with details
            all_purchases = PurchaseRepository.get_all()
            
            # Apply date filter
            start_date, end_date = self._get_date_range()
            
            if start_date and end_date:
                self.purchases = [
                    p for p in all_purchases
                    if start_date <= p.purchase_date <= end_date
                ]
            else:
                self.purchases = all_purchases
            
            # Update table
            self._populate_table()
            
            # Update summary cards
            self._update_summary(all_purchases)
            
            # Update status
            self.status_label.setText(f"Showing {len(self.purchases)} purchases")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load purchases: {str(e)}")
            self.status_label.setText("Error loading purchases")
    
    def _populate_table(self):
        """Populate the purchases table."""
        self.purchase_table.setRowCount(len(self.purchases))
        
        for row, purchase in enumerate(self.purchases):
            # Purchase No
            self.purchase_table.setItem(row, 0, QTableWidgetItem(purchase.purchase_no))
            
            # Date
            date_str = purchase.purchase_date.strftime("%Y-%m-%d") if purchase.purchase_date else ""
            self.purchase_table.setItem(row, 1, QTableWidgetItem(date_str))
            
            # Supplier
            supplier_name = purchase.supplier_name or purchase.supplier_id
            self.purchase_table.setItem(row, 2, QTableWidgetItem(supplier_name))
            
            # Item count
            item_count = len(purchase.details) if purchase.details else 0
            self.purchase_table.setItem(row, 3, QTableWidgetItem(str(item_count)))
            
            # Total Amount
            total_item = QTableWidgetItem(f"Rs. {purchase.total_amount:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setForeground(QColor("#2196F3"))
            self.purchase_table.setItem(row, 4, total_item)
            
            # Status
            status_item = QTableWidgetItem(purchase.payment_status)
            if purchase.payment_status == "Received":
                status_item.setForeground(QColor("green"))
            elif purchase.payment_status == "Pending":
                status_item.setForeground(QColor("orange"))
            self.purchase_table.setItem(row, 5, status_item)
            
            # Actions - View Details button
            self._add_action_button(row, purchase)
    
    def _add_action_button(self, row: int, purchase: Purchase):
        """Add action button to table row."""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 5, 5, 5)
        
        view_btn = QPushButton("View")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #2196F3;
                color: #2196F3;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)
        view_btn.clicked.connect(lambda: self._view_purchase_details(purchase))
        actions_layout.addWidget(view_btn)
        
        self.purchase_table.setCellWidget(row, 6, actions_widget)
    
    def _view_purchase_details(self, purchase: Purchase):
        """Show purchase details dialog."""
        # Load full details if not already loaded
        if not purchase.details:
            full_purchase = PurchaseRepository.get_by_id(purchase.purchase_no)
            if full_purchase:
                purchase = full_purchase
        
        dialog = PurchaseDetailDialog(purchase, self)
        # Connect signal to refresh list when purchase is updated
        dialog.purchase_updated.connect(self._load_purchases)
        dialog.exec()
    
    def _update_summary(self, all_purchases: List[Purchase]):
        """Update summary cards with totals."""
        today = date.today()
        
        # This month's purchases
        month_start = today.replace(day=1)
        month_total = sum(
            p.total_amount for p in all_purchases
            if p.purchase_date and p.purchase_date >= month_start
        )
        self._update_card_value(self.month_card, f"Rs. {month_total:,.2f}")
        
        # All time total
        all_time_total = sum(p.total_amount for p in all_purchases)
        self._update_card_value(self.total_card, f"Rs. {all_time_total:,.2f}")
        
        # Pending payments
        pending_total = sum(
            p.total_amount for p in all_purchases
            if p.payment_status == "Pending"
        )
        self._update_card_value(self.pending_card, f"Rs. {pending_total:,.2f}")
        
        # Order count
        self._update_card_value(self.count_card, str(len(all_purchases)))


# =============================================================================
# MODULE TEST
# =============================================================================

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = PurchaseView()
    window.setWindowTitle("Purchase View Test")
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
