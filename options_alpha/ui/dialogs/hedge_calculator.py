"""
Hedge calculator dialog for Options Alpha Analyzer
Helps traders calculate appropriate hedge ratios for options positions
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QLabel, QDoubleSpinBox, QPushButton, QComboBox,
                           QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
                           QTabWidget, QWidget, QFrame, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class HedgeCalculatorDialog(QDialog):
    """Dialog for calculating option position hedges"""
    
    def __init__(self, parent=None):
        """Initialize the hedge calculator dialog
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Options Hedge Calculator")
        self.setMinimumSize(800, 600)  # Increased window size
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the hedge calculator UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)  # Add more spacing between elements
        
        # Title
        title_label = QLabel("Options Position Hedge Calculator")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Calculate optimal hedges for your options positions")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        main_layout.addSpacing(10)
        
        # Position Details Section - Always visible
        position_group = QGroupBox("Your Position")
        position_layout = QGridLayout()
        position_layout.setVerticalSpacing(10)  # Add more vertical spacing
        position_layout.setHorizontalSpacing(15)  # Add more horizontal spacing
        
        # Position type (Long/Short)
        position_layout.addWidget(QLabel("Position Type:"), 0, 0)
        self.position_type = QComboBox()
        self.position_type.addItems(["Long Call", "Long Put", "Short Call", "Short Put", "Long Stock", "Short Stock"])
        self.position_type.currentIndexChanged.connect(self.update_calculations)
        position_layout.addWidget(self.position_type, 0, 1)
        
        # Quantity
        position_layout.addWidget(QLabel("Quantity:"), 1, 0)
        self.quantity = QDoubleSpinBox()
        self.quantity.setRange(1, 10000)
        self.quantity.setValue(1)
        self.quantity.valueChanged.connect(self.update_calculations)
        position_layout.addWidget(self.quantity, 1, 1)
        
        # Delta
        position_layout.addWidget(QLabel("Delta (per contract):"), 0, 2)
        self.delta = QDoubleSpinBox()
        self.delta.setRange(-1, 1)
        self.delta.setDecimals(3)
        self.delta.setSingleStep(0.05)
        self.delta.setValue(0.5)
        self.delta.valueChanged.connect(self.update_calculations)
        position_layout.addWidget(self.delta, 0, 3)
        
        # Gamma
        position_layout.addWidget(QLabel("Gamma (per contract):"), 1, 2)
        self.gamma = QDoubleSpinBox()
        self.gamma.setRange(0, 0.5)
        self.gamma.setDecimals(4)
        self.gamma.setSingleStep(0.001)
        self.gamma.setValue(0.05)
        self.gamma.valueChanged.connect(self.update_calculations)
        position_layout.addWidget(self.gamma, 1, 3)
        
        # Current stock price
        position_layout.addWidget(QLabel("Stock Price:"), 2, 0)
        self.stock_price = QDoubleSpinBox()
        self.stock_price.setRange(1, 10000)
        self.stock_price.setValue(100)
        self.stock_price.valueChanged.connect(self.update_calculations)
        position_layout.addWidget(self.stock_price, 2, 1)
        
        # Expected move
        position_layout.addWidget(QLabel("Expected Move (%):"), 2, 2)
        self.price_move = QDoubleSpinBox()
        self.price_move.setRange(-50, 50)
        self.price_move.setValue(5)
        self.price_move.valueChanged.connect(self.update_calculations)
        position_layout.addWidget(self.price_move, 2, 3)
        
        position_group.setLayout(position_layout)
        main_layout.addWidget(position_group)
        
        # Position Risk Summary
        risk_summary = QFrame()
        risk_summary.setFrameShape(QFrame.StyledPanel)
        risk_layout = QHBoxLayout(risk_summary)
        risk_layout.setSpacing(20)  # Increase spacing between risk metrics
        
        # Delta exposure
        delta_box = QVBoxLayout()
        delta_box.addWidget(QLabel("Delta Exposure:"))
        self.delta_exposure = QLabel("0")
        self.delta_exposure.setFont(QFont("Arial", 16, QFont.Bold))
        self.delta_exposure.setAlignment(Qt.AlignCenter)
        delta_box.addWidget(self.delta_exposure)
        risk_layout.addLayout(delta_box)
        
        # Gamma exposure
        gamma_box = QVBoxLayout()
        gamma_box.addWidget(QLabel("Gamma Exposure:"))
        self.gamma_exposure = QLabel("0")
        self.gamma_exposure.setFont(QFont("Arial", 16, QFont.Bold))
        self.gamma_exposure.setAlignment(Qt.AlignCenter)
        gamma_box.addWidget(self.gamma_exposure)
        risk_layout.addLayout(gamma_box)
        
        # Expected P/L
        pl_box = QVBoxLayout()
        pl_box.addWidget(QLabel("Expected P/L:"))
        self.expected_pl = QLabel("$0")
        self.expected_pl.setFont(QFont("Arial", 16, QFont.Bold))
        self.expected_pl.setAlignment(Qt.AlignCenter)
        pl_box.addWidget(self.expected_pl)
        risk_layout.addLayout(pl_box)
        
        main_layout.addWidget(risk_summary)
        
        # Hedging Strategy Tabs
        hedge_tabs = QTabWidget()
        
        # ---- Simple Delta Hedge Tab ----
        delta_tab = QWidget()
        delta_layout = QVBoxLayout(delta_tab)
        delta_layout.setSpacing(15)  # Increase spacing
        
        delta_options = QGroupBox("Delta Hedging Options")
        delta_options_layout = QVBoxLayout()
        delta_options_layout.setSpacing(10)  # Increase spacing
        
        # Delta hedge types radio buttons
        delta_type_group = QButtonGroup(delta_tab)
        
        self.full_delta_hedge = QRadioButton("Full Delta Hedge")
        self.full_delta_hedge.setChecked(True)
        delta_type_group.addButton(self.full_delta_hedge)
        delta_options_layout.addWidget(self.full_delta_hedge)
        
        self.partial_delta_hedge = QRadioButton("Partial Delta Hedge (50%)")
        delta_type_group.addButton(self.partial_delta_hedge)
        delta_options_layout.addWidget(self.partial_delta_hedge)
        
        # Connect radio buttons
        self.full_delta_hedge.toggled.connect(self.update_calculations)
        self.partial_delta_hedge.toggled.connect(self.update_calculations)
        
        delta_options.setLayout(delta_options_layout)
        delta_layout.addWidget(delta_options)
        
        # Delta hedge result
        delta_result_group = QGroupBox("Hedge Result")
        delta_result_layout = QGridLayout()
        delta_result_layout.setSpacing(10)  # Increase spacing
        
        delta_result_layout.addWidget(QLabel("Required Stock Shares:"), 0, 0)
        self.delta_hedge_shares = QLabel("0")
        self.delta_hedge_shares.setFont(QFont("Arial", 12, QFont.Bold))
        self.delta_hedge_shares.setMinimumWidth(200)  # Ensure enough width for text
        delta_result_layout.addWidget(self.delta_hedge_shares, 0, 1)
        
        delta_result_layout.addWidget(QLabel("Delta Coverage:"), 1, 0)
        self.delta_coverage = QLabel("0%")
        self.delta_coverage.setMinimumWidth(200)  # Ensure enough width for text
        delta_result_layout.addWidget(self.delta_coverage, 1, 1)
        
        delta_result_group.setLayout(delta_result_layout)
        delta_layout.addWidget(delta_result_group)
        
        delta_layout.addStretch()
        hedge_tabs.addTab(delta_tab, "Delta Hedge")
        
        # ---- Delta-Gamma Neutral Tab ----
        delta_gamma_tab = QWidget()
        delta_gamma_layout = QVBoxLayout(delta_gamma_tab)
        delta_gamma_layout.setSpacing(15)  # Increase spacing
        
        # Instructions
        delta_gamma_instructions = QLabel(
            "Delta-Gamma neutral hedging uses a combination of stock and option contracts "
            "to neutralize both delta and gamma exposures, protecting against both "
            "directional moves and changes in the rate of price movement."
        )
        delta_gamma_instructions.setWordWrap(True)  # Enable word wrap
        delta_gamma_instructions.setMinimumHeight(50)  # Ensure enough height for wrapped text
        delta_gamma_layout.addWidget(delta_gamma_instructions)
        
        # Hedge option inputs
        hedge_option_group = QGroupBox("Hedge Option Characteristics")
        hedge_option_layout = QGridLayout()
        hedge_option_layout.setVerticalSpacing(10)  # Increase spacing
        hedge_option_layout.setHorizontalSpacing(15)  # Increase spacing
        
        hedge_option_layout.addWidget(QLabel("Hedge Option Delta:"), 0, 0)
        self.hedge_delta = QDoubleSpinBox()
        self.hedge_delta.setRange(-1, 1)
        self.hedge_delta.setDecimals(3)
        self.hedge_delta.setSingleStep(0.05)
        self.hedge_delta.setValue(-0.5)  # Default to opposite sign of typical position
        self.hedge_delta.valueChanged.connect(self.update_calculations)
        hedge_option_layout.addWidget(self.hedge_delta, 0, 1)
        
        hedge_option_layout.addWidget(QLabel("Hedge Option Gamma:"), 1, 0)
        self.hedge_gamma = QDoubleSpinBox()
        self.hedge_gamma.setRange(0, 0.5)
        self.hedge_gamma.setDecimals(4)
        self.hedge_gamma.setSingleStep(0.001)
        self.hedge_gamma.setValue(0.02)
        self.hedge_gamma.valueChanged.connect(self.update_calculations)
        hedge_option_layout.addWidget(self.hedge_gamma, 1, 1)
        
        # Quick options for hedge
        hedge_option_layout.addWidget(QLabel("Quick Preset:"), 2, 0)
        self.hedge_preset = QComboBox()
        self.hedge_preset.addItems([
            "Custom (Manual Entry)",
            "ATM Put (Delta -0.5, Gamma 0.05)",
            "ATM Call (Delta 0.5, Gamma 0.05)",
            "OTM Put (Delta -0.3, Gamma 0.04)",
            "OTM Call (Delta 0.3, Gamma 0.04)"
        ])
        self.hedge_preset.currentIndexChanged.connect(self.apply_hedge_preset)
        hedge_option_layout.addWidget(self.hedge_preset, 2, 1)
        
        hedge_option_group.setLayout(hedge_option_layout)
        delta_gamma_layout.addWidget(hedge_option_group)
        
        # Hedge result
        delta_gamma_result_group = QGroupBox("Delta-Gamma Neutral Hedge")
        delta_gamma_result_layout = QGridLayout()
        delta_gamma_result_layout.setSpacing(10)  # Increase spacing
        
        delta_gamma_result_layout.addWidget(QLabel("Stock Shares Required:"), 0, 0)
        self.delta_gamma_hedge_shares = QLabel("0")
        self.delta_gamma_hedge_shares.setFont(QFont("Arial", 12, QFont.Bold))
        self.delta_gamma_hedge_shares.setMinimumWidth(200)  # Ensure enough width for text
        delta_gamma_result_layout.addWidget(self.delta_gamma_hedge_shares, 0, 1)
        
        delta_gamma_result_layout.addWidget(QLabel("Option Contracts Required:"), 1, 0)
        self.delta_gamma_hedge_options = QLabel("0")
        self.delta_gamma_hedge_options.setFont(QFont("Arial", 12, QFont.Bold))
        self.delta_gamma_hedge_options.setMinimumWidth(200)  # Ensure enough width for text
        delta_gamma_result_layout.addWidget(self.delta_gamma_hedge_options, 1, 1)
        
        delta_gamma_result_layout.addWidget(QLabel("Coverage:"), 2, 0)
        self.delta_gamma_coverage = QLabel("Delta: 0%, Gamma: 0%")
        self.delta_gamma_coverage.setMinimumWidth(200)  # Ensure enough width for text
        delta_gamma_result_layout.addWidget(self.delta_gamma_coverage, 2, 1)
        
        delta_gamma_result_group.setLayout(delta_gamma_result_layout)
        delta_gamma_layout.addWidget(delta_gamma_result_group)
        
        delta_gamma_layout.addStretch()
        hedge_tabs.addTab(delta_gamma_tab, "Delta-Gamma Neutral")
        
        # ---- Advanced Options Tab ----
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(15)  # Increase spacing
        
        # Contract to stock ratio
        advanced_options_group = QGroupBox("Advanced Hedging Settings")
        advanced_options_layout = QGridLayout()
        advanced_options_layout.setSpacing(10)  # Increase spacing
        
        advanced_options_layout.addWidget(QLabel("Contracts per 100 Shares:"), 0, 0)
        self.hedge_ratio = QDoubleSpinBox()
        self.hedge_ratio.setRange(0.1, 100)
        self.hedge_ratio.setDecimals(2)
        self.hedge_ratio.setSingleStep(0.5)
        self.hedge_ratio.setValue(2)
        self.hedge_ratio.valueChanged.connect(self.update_calculations)
        advanced_options_layout.addWidget(self.hedge_ratio, 0, 1)
        
        advanced_options_group.setLayout(advanced_options_layout)
        advanced_layout.addWidget(advanced_options_group)
        
        # All hedge options table
        advanced_layout.addWidget(QLabel("All Available Hedge Strategies:"))
        self.hedge_table = QTableWidget()
        self.hedge_table.setColumnCount(4)
        self.hedge_table.setHorizontalHeaderLabels([
            "Hedge Type", "Quantity", "Delta Coverage", "Notes"
        ])
        self.hedge_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hedge_table.setMinimumHeight(200)  # Ensure table is tall enough
        advanced_layout.addWidget(self.hedge_table)
        
        hedge_tabs.addTab(advanced_tab, "Advanced Options")
        
        main_layout.addWidget(hedge_tabs)
        
        # Recommended Hedge
        recommendation = QFrame()
        recommendation.setFrameShape(QFrame.StyledPanel)
        recommendation_layout = QVBoxLayout(recommendation)
        recommendation_layout.setSpacing(10)  # Increase spacing
        
        rec_label = QLabel("Recommended Hedge Strategy:")
        rec_label.setFont(QFont("Arial", 10, QFont.Bold))
        recommendation_layout.addWidget(rec_label)
        
        self.recommended_hedge = QLabel("None")
        self.recommended_hedge.setWordWrap(True)  # Enable word wrap
        self.recommended_hedge.setMinimumHeight(50)  # Ensure enough height for wrapped text
        recommendation_layout.addWidget(self.recommended_hedge)
        
        main_layout.addWidget(recommendation)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # Increase spacing
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.update_calculations)
        self.calculate_btn.setMinimumWidth(120)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setMinimumWidth(120)
        
        button_layout.addStretch()
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        # Initial calculation
        self.update_calculations()
        
    def apply_hedge_preset(self):
        """Apply a preset for the hedge option"""
        preset_index = self.hedge_preset.currentIndex()
        
        # Skip if it's custom (manual entry)
        if preset_index == 0:
            return
            
        # Apply presets
        if preset_index == 1:  # ATM Put
            self.hedge_delta.setValue(-0.5)
            self.hedge_gamma.setValue(0.05)
        elif preset_index == 2:  # ATM Call
            self.hedge_delta.setValue(0.5)
            self.hedge_gamma.setValue(0.05)
        elif preset_index == 3:  # OTM Put
            self.hedge_delta.setValue(-0.3)
            self.hedge_gamma.setValue(0.04)
        elif preset_index == 4:  # OTM Call
            self.hedge_delta.setValue(0.3)
            self.hedge_gamma.setValue(0.04)
            
        # Update calculations with new values
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
        hedge_delta = self.hedge_delta.value()
        hedge_gamma = self.hedge_gamma.value()
        
        # Calculate total position delta
        position_delta_sign = 1
        if position_type in ["Short Call", "Short Put", "Short Stock"]:
            position_delta_sign = -1
            
        if position_type == "Long Stock":
            position_delta = position_delta_sign * quantity * 100  # Convert to share equivalent
            position_gamma = 0
        elif position_type == "Short Stock":
            position_delta = position_delta_sign * quantity * 100  # Convert to share equivalent
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
        
        # Update position risk summary
        self.delta_exposure.setText(f"{position_delta:.2f}")
        self.gamma_exposure.setText(f"{position_gamma:.2f}")
        self.expected_pl.setText(f"${total_pl:.2f}")
        
        # Update delta hedge tab
        if self.full_delta_hedge.isChecked():
            # Full delta hedge
            stock_qty = -int(position_delta)
            coverage = "100%"
        else:
            # Partial delta hedge (50%)
            stock_qty = -int(position_delta * 0.5)
            coverage = "50%"
            
        self.delta_hedge_shares.setText(f"{abs(stock_qty):,d} {'Short' if stock_qty < 0 else 'Long'}")
        self.delta_coverage.setText(coverage)
        
        # Update delta-gamma neutral hedge tab
        if position_delta != 0 and position_gamma != 0 and hedge_delta != 0 and hedge_gamma != 0:
            # We want to solve the following system of equations:
            # stock_shares * 1 + option_contracts * hedge_delta * 100 = -position_delta
            # stock_shares * 0 + option_contracts * hedge_gamma * 100 = -position_gamma
            
            # First, calculate the number of option contracts needed to neutralize gamma
            option_contracts = -position_gamma / (hedge_gamma * 100)
            
            # Then, calculate stock shares needed to neutralize the remaining delta
            remaining_delta = position_delta + (option_contracts * hedge_delta * 100)
            stock_shares = -remaining_delta
            
            # Round to practical quantities
            option_contracts = round(option_contracts)
            stock_shares = int(stock_shares)
            
            self.delta_gamma_hedge_shares.setText(f"{abs(stock_shares):,d} {'Short' if stock_shares < 0 else 'Long'}")
            self.delta_gamma_hedge_options.setText(f"{abs(option_contracts)} {'Short' if option_contracts < 0 else 'Long'}")
            self.delta_gamma_coverage.setText("Delta: ~100%, Gamma: ~100%")
        else:
            self.delta_gamma_hedge_shares.setText("N/A")
            self.delta_gamma_hedge_options.setText("N/A")
            self.delta_gamma_coverage.setText("Delta: 0%, Gamma: 0%")
        
        # Calculate hedge options for the advanced tab
        self.calculate_hedge_options(position_delta, position_gamma, stock_price, price_move_pct, hedge_ratio, hedge_delta, hedge_gamma)
    
    def calculate_hedge_options(self, position_delta, position_gamma, stock_price, price_move_pct, hedge_ratio, hedge_delta, hedge_gamma):
        """Calculate and display different hedge options
        
        Args:
            position_delta: Total position delta
            position_gamma: Total position gamma
            stock_price: Current stock price
            price_move_pct: Expected price move as a percentage
            hedge_ratio: Contract to shares ratio
            hedge_delta: Delta of the option to use for hedging
            hedge_gamma: Gamma of the option to use for hedging
        """
        # Clear the table
        self.hedge_table.setRowCount(0)
        
        hedges = []
        
        # Stock hedge
        if position_delta != 0:
            stock_qty = -int(position_delta)
            hedges.append({
                "type": "Stock Shares",
                "quantity": f"{abs(stock_qty):,d} {'Short' if stock_qty < 0 else 'Long'}",
                "coverage": "100% Delta",
                "notes": "Complete delta neutrality, no gamma offset"
            })
        
        # Options hedge based on hedge ratio
        if position_delta != 0:
            # Approximate using the hedge ratio
            option_qty = -int(position_delta / (hedge_ratio * 100))
            if option_qty != 0:
                hedges.append({
                    "type": "Options Only",
                    "quantity": f"{abs(option_qty)} {'Short' if option_qty < 0 else 'Long'} contracts",
                    "coverage": "~100% Delta",
                    "notes": f"Using {hedge_ratio} contracts per 100 shares ratio"
                })
        
        # Partial delta hedge (50%)
        if position_delta != 0:
            stock_qty = -int(position_delta * 0.5)
            hedges.append({
                "type": "Partial Stock Hedge",
                "quantity": f"{abs(stock_qty):,d} {'Short' if stock_qty < 0 else 'Long'} shares",
                "coverage": "50% Delta",
                "notes": "Allows for some directional exposure"
            })
            
        # Delta-Gamma neutral hedge (Combined stock and options)
        if position_delta != 0 and position_gamma != 0 and hedge_delta != 0 and hedge_gamma != 0:
            # We want to solve the following system of equations:
            # stock_shares * 1 + option_contracts * hedge_delta * 100 = -position_delta
            # stock_shares * 0 + option_contracts * hedge_gamma * 100 = -position_gamma
            
            # First, calculate the number of option contracts needed to neutralize gamma
            option_contracts = -position_gamma / (hedge_gamma * 100)
            
            # Then, calculate stock shares needed to neutralize the remaining delta
            remaining_delta = position_delta + (option_contracts * hedge_delta * 100)
            stock_shares = -remaining_delta
            
            # Round to practical quantities
            option_contracts = round(option_contracts)
            stock_shares = int(stock_shares)
            
            if option_contracts != 0 or stock_shares != 0:
                hedges.append({
                    "type": "Delta-Gamma Neutral",
                    "quantity": f"{abs(stock_shares):,d} {'Short' if stock_shares < 0 else 'Long'} shares + "
                               f"{abs(option_contracts)} {'Short' if option_contracts < 0 else 'Long'} contracts",
                    "coverage": "100% Delta, 100% Gamma",
                    "notes": "Complete first and second-order neutrality"
                })
        
        # Recommended hedge
        if abs(position_delta) > 100 and abs(position_gamma) > 50:
            self.recommended_hedge.setText(
                f"Delta-Gamma Neutral Hedge: {abs(stock_shares):,d} {'short' if stock_shares < 0 else 'long'} shares of stock + "
                f"{abs(option_contracts)} {'short' if option_contracts < 0 else 'long'} option contracts "
                f"for complete first and second-order risk protection."
            )
        elif abs(position_delta) > 100:
            self.recommended_hedge.setText(
                f"Delta Hedge: {abs(int(position_delta)):,d} shares of stock in the opposite direction, "
                f"which will neutralize your directional exposure."
            )
        elif position_delta > 0:
            self.recommended_hedge.setText(
                f"Delta Hedge: {abs(int(position_delta)):,d} short shares of stock to neutralize your bullish position."
            )
        elif position_delta < 0:
            self.recommended_hedge.setText(
                f"Delta Hedge: {abs(int(position_delta)):,d} long shares of stock to neutralize your bearish position."
            )
        else:
            self.recommended_hedge.setText("Position is already delta neutral")
        
        # Populate table
        self.hedge_table.setRowCount(len(hedges))
        
        for row, hedge in enumerate(hedges):
            # Hedge type
            item = QTableWidgetItem(hedge["type"])
            self.hedge_table.setItem(row, 0, item)
            
            # Quantity
            item = QTableWidgetItem(hedge["quantity"])
            self.hedge_table.setItem(row, 1, item)
            
            # Coverage
            item = QTableWidgetItem(hedge["coverage"])
            self.hedge_table.setItem(row, 2, item)
            
            # Notes
            item = QTableWidgetItem(hedge["notes"])
            self.hedge_table.setItem(row, 3, item)
            
    def set_position_data(self, position_type, quantity, delta, gamma, stock_price):
        """Set position data from external source
        
        Args:
            position_type: Type of position (e.g., "Long Call")
            quantity: Number of contracts
            delta: Delta value per contract
            gamma: Gamma value per contract
            stock_price: Current stock price
        """
        # Set the values in the UI
        index = self.position_type.findText(position_type)
        if index >= 0:
            self.position_type.setCurrentIndex(index)
            
        self.quantity.setValue(quantity)
        self.delta.setValue(abs(delta))  # Use absolute value, sign handled by position type
        self.gamma.setValue(gamma)
        self.stock_price.setValue(stock_price)
        
        # Reset hedge preset to custom
        self.hedge_preset.setCurrentIndex(0)
        
        # Update calculations
        self.update_calculations() 