"""
Hedge calculator dialog for Options Alpha Analyzer
Helps traders calculate appropriate hedge ratios for options positions
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QLabel, QDoubleSpinBox, QPushButton, QComboBox,
                           QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class HedgeCalculatorDialog(QDialog):
    """Dialog for calculating option position hedges"""
    
    def __init__(self, parent=None):
        """Initialize the hedge calculator dialog
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Options Hedge Calculator")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the hedge calculator UI"""
        main_layout = QVBoxLayout(self)
        
        # Input Section
        input_group = QGroupBox("Position Details")
        input_layout = QGridLayout()
        
        # Primary Position
        input_layout.addWidget(QLabel("<b>Primary Position:</b>"), 0, 0, 1, 2)
        
        # Position type (Long/Short)
        input_layout.addWidget(QLabel("Position Type:"), 1, 0)
        self.position_type = QComboBox()
        self.position_type.addItems(["Long Call", "Long Put", "Short Call", "Short Put", "Long Stock", "Short Stock"])
        self.position_type.currentIndexChanged.connect(self.update_calculations)
        input_layout.addWidget(self.position_type, 1, 1)
        
        # Quantity
        input_layout.addWidget(QLabel("Quantity:"), 2, 0)
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(1, 10000)
        self.quantity.setValue(1)
        self.quantity.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.quantity, 2, 1)
        
        # Delta
        input_layout.addWidget(QLabel("Delta (per contract):"), 3, 0)
        self.delta = QDoubleSpinBox()
        self.delta.setRange(-1, 1)
        self.delta.setDecimals(3)
        self.delta.setSingleStep(0.05)
        self.delta.setValue(0.5)
        self.delta.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.delta, 3, 1)
        
        # Gamma
        input_layout.addWidget(QLabel("Gamma (per contract):"), 4, 0)
        self.gamma = QDoubleSpinBox()
        self.gamma.setRange(0, 0.5)
        self.gamma.setDecimals(4)
        self.gamma.setSingleStep(0.001)
        self.gamma.setValue(0.05)
        self.gamma.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.gamma, 4, 1)
        
        # Current stock price
        input_layout.addWidget(QLabel("Stock Price:"), 5, 0)
        self.stock_price = QDoubleSpinBox()
        self.stock_price.setRange(1, 10000)
        self.stock_price.setValue(100)
        self.stock_price.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.stock_price, 5, 1)
        
        # Expected move
        input_layout.addWidget(QLabel("Expected Price Move (%):"), 6, 0)
        self.price_move = QDoubleSpinBox()
        self.price_move.setRange(-50, 50)
        self.price_move.setValue(5)
        self.price_move.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.price_move, 6, 1)
        
        # Stock hedge in contracts
        input_layout.addWidget(QLabel("Contracts per 100 Shares:"), 7, 0)
        self.hedge_ratio = QDoubleSpinBox()
        self.hedge_ratio.setRange(0, 100)
        self.hedge_ratio.setDecimals(2)
        self.hedge_ratio.setValue(2)
        self.hedge_ratio.valueChanged.connect(self.update_calculations)
        input_layout.addWidget(self.hedge_ratio, 7, 1)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Results Section
        results_group = QGroupBox("Hedge Calculations")
        results_layout = QVBoxLayout()
        
        # Table of hedge options
        self.hedge_table = QTableWidget()
        self.hedge_table.setColumnCount(4)
        self.hedge_table.setHorizontalHeaderLabels([
            "Hedge Type", "Quantity", "Delta Coverage", "Notes"
        ])
        self.hedge_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        results_layout.addWidget(self.hedge_table)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
        # Dynamic risk graph section
        risk_group = QGroupBox("Position Risk Analysis")
        risk_layout = QGridLayout()
        
        # Static text for this example (in a real app, this would be a plot)
        risk_layout.addWidget(QLabel("Delta Exposure:"), 0, 0)
        self.delta_exposure = QLabel("0")
        risk_layout.addWidget(self.delta_exposure, 0, 1)
        
        risk_layout.addWidget(QLabel("Gamma Exposure:"), 1, 0)
        self.gamma_exposure = QLabel("0")
        risk_layout.addWidget(self.gamma_exposure, 1, 1)
        
        risk_layout.addWidget(QLabel("Expected P/L from Price Move:"), 2, 0)
        self.expected_pl = QLabel("$0")
        risk_layout.addWidget(self.expected_pl, 2, 1)
        
        risk_layout.addWidget(QLabel("Recommended Hedge:"), 3, 0)
        self.recommended_hedge = QLabel("None")
        risk_layout.addWidget(self.recommended_hedge, 3, 1)
        
        risk_group.setLayout(risk_layout)
        main_layout.addWidget(risk_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("Calculate Hedge Options")
        self.calculate_btn.clicked.connect(self.update_calculations)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        # Initial calculation
        self.update_calculations()
    
    def update_calculations(self):
        """Update all hedge calculations based on current inputs"""
        # Get input values
        position_type = self.position_type.currentText()
        quantity = self.quantity.value()
        delta = self.delta.value()
        gamma = self.gamma.value()
        stock_price = self.stock_price.value()
        price_move_pct = self.price_move.value() / 100
        hedge_ratio = self.hedge_ratio.value()
        
        # Calculate total position delta
        position_delta_sign = 1
        if position_type in ["Short Call", "Short Put", "Short Stock"]:
            position_delta_sign = -1
            
        if position_type == "Long Stock":
            position_delta = position_delta_sign * quantity
            position_gamma = 0
        elif position_type == "Short Stock":
            position_delta = position_delta_sign * quantity
            position_gamma = 0
        else:
            # For options
            # Adjust delta sign based on put/call
            contract_delta = delta
            if position_type in ["Long Put", "Short Put"]:
                contract_delta = -delta
                
            position_delta = position_delta_sign * contract_delta * quantity * 100
            position_gamma = position_delta_sign * gamma * quantity * 100
        
        # Calculate expected price move
        price_move = stock_price * price_move_pct
        new_price = stock_price + price_move
        
        # Calculate delta P&L
        delta_pl = position_delta * price_move
        
        # Calculate gamma P&L (approximation)
        gamma_pl = 0.5 * position_gamma * price_move * price_move
        
        # Total expected P&L
        total_pl = delta_pl + gamma_pl
        
        # Update results
        self.delta_exposure.setText(f"{position_delta:.2f}")
        self.gamma_exposure.setText(f"{position_gamma:.2f}")
        self.expected_pl.setText(f"${total_pl:.2f}")
        
        # Calculate hedge options
        self.calculate_hedge_options(position_delta, position_gamma, stock_price, price_move_pct, hedge_ratio)
    
    def calculate_hedge_options(self, position_delta, position_gamma, stock_price, price_move_pct, hedge_ratio):
        """Calculate and display different hedge options
        
        Args:
            position_delta: Total position delta
            position_gamma: Total position gamma
            stock_price: Current stock price
            price_move_pct: Expected price move as a percentage
            hedge_ratio: Contract to shares ratio
        """
        # Clear the table
        self.hedge_table.setRowCount(0)
        
        hedges = []
        
        # Stock hedge
        if position_delta != 0:
            stock_qty = -int(position_delta)
            hedges.append({
                "type": "Stock Shares",
                "quantity": stock_qty,
                "coverage": "100% Delta",
                "notes": "Complete delta neutrality, no gamma offset"
            })
        
        # Options hedge based on hedge ratio
        if position_delta != 0:
            # Approximate using the hedge ratio
            option_qty = -int(position_delta / (hedge_ratio * 100))
            if option_qty != 0:
                hedges.append({
                    "type": "Options Contracts",
                    "quantity": option_qty,
                    "coverage": "~100% Delta",
                    "notes": f"Using {hedge_ratio} contracts per 100 shares ratio"
                })
        
        # Partial delta hedge (50%)
        if position_delta != 0:
            stock_qty = -int(position_delta * 0.5)
            hedges.append({
                "type": "Partial Stock Hedge",
                "quantity": stock_qty,
                "coverage": "50% Delta",
                "notes": "Allows for some directional exposure"
            })
        
        # Recommended hedge
        if abs(position_delta) > 100:
            self.recommended_hedge.setText(f"Hedge with {abs(int(position_delta))} shares of stock in the opposite direction")
        elif position_delta > 0:
            self.recommended_hedge.setText(f"Hedge with {abs(int(position_delta))} shares of stock (short)")
        elif position_delta < 0:
            self.recommended_hedge.setText(f"Hedge with {abs(int(position_delta))} shares of stock (long)")
        else:
            self.recommended_hedge.setText("Position is already delta neutral")
        
        # Populate table
        self.hedge_table.setRowCount(len(hedges))
        
        for row, hedge in enumerate(hedges):
            # Hedge type
            item = QTableWidgetItem(hedge["type"])
            self.hedge_table.setItem(row, 0, item)
            
            # Quantity
            item = QTableWidgetItem(str(hedge["quantity"]))
            self.hedge_table.setItem(row, 1, item)
            
            # Coverage
            item = QTableWidgetItem(hedge["coverage"])
            self.hedge_table.setItem(row, 2, item)
            
            # Notes
            item = QTableWidgetItem(hedge["notes"])
            self.hedge_table.setItem(row, 3, item) 