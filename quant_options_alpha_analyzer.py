import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                            QComboBox, QTabWidget, QPushButton, QTableWidget, 
                            QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox, 
                            QDoubleSpinBox, QFileDialog, QMessageBox, QToolTip, 
                            QScrollArea, QDialog, QTextBrowser, QSizePolicy, 
                            QProgressDialog)
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer
from PyQt5.QtGui import QFont, QColor
import random

# Create a matplotlib canvas class for embedding plots
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Agreement")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # License text
        license_text = """# Quant Options Alpha Analyzer - Modified MIT License

Copyright (c) 2025, Alexander Husseini

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to use, copy, modify, and/or merge copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

2. **Non-Commercial Restriction**: The Software may not be sold, licensed, rented, leased or otherwise commercially redistributed without explicit written permission from the copyright holder.

3. **Attribution Requirement**: Any use, reproduction, or distribution of the Software must include proper attribution to Alexander Husseini as the original author.

4. **Financial Disclaimer**:
   a) This Software is provided for EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY and does not constitute financial, investment, or trading advice.
   b) The author is not registered as a securities broker-dealer, investment advisor, or financial advisor.
   c) Users are solely responsible for their trading decisions and any resulting financial gains or losses.
   d) Past performance of any model or calculation implemented in the Software does not guarantee future results.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, FINANCIAL LOSSES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

BY USING THE SOFTWARE, YOU ACKNOWLEDGE THAT YOU ASSUME ALL RISKS ASSOCIATED WITH THE USE OF THE SOFTWARE FOR FINANCIAL ANALYSIS OR TRADING PURPOSES."""
        
        text_browser = QTextBrowser()
        text_browser.setPlainText(license_text)
        layout.addWidget(text_browser)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.accept_button = QPushButton("I Accept")
        self.accept_button.clicked.connect(self.accept)
        
        self.decline_button = QPushButton("I Decline")
        self.decline_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.decline_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

class OptionsAlphaAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Check if license has been accepted
        settings = QSettings("AlexanderHusseini", "QuantOptionsAlphaAnalyzer")
        license_accepted = settings.value("license_accepted", False, type=bool)
        
        if not license_accepted:
            # Show license dialog
            license_dialog = LicenseDialog(self)
            result = license_dialog.exec_()
            
            if result == QDialog.Accepted:
                # User accepted the license
                settings.setValue("license_accepted", True)
            else:
                # User declined the license, exit the application
                sys.exit(0)
        
        self.setWindowTitle("Quant Options Alpha Analyzer")
        self.setMinimumSize(900, 700)
        
        # Create the central widget and tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.guide_tab = QWidget()
        self.simulation_tab = QWidget()  # New tab for Feature 2
        
        self.tabs.addTab(self.main_tab, "🔢 Analyzer")
        self.tabs.addTab(self.guide_tab, "📘 Formula Guide")
        self.tabs.addTab(self.simulation_tab, "🔁 Simulated Alpha Engine")  # Added new tab
        
        self.main_layout.addWidget(self.tabs)
        
        # Setup tabs
        self.setup_main_tab()
        self.setup_guide_tab()
        self.setup_simulation_tab()  # Setup for Feature 2
        
        # Data storage
        self.options_data = []
        
        # Add a view license menu in a simple menu bar
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        
        view_license_action = help_menu.addAction("View License Agreement")
        view_license_action.triggered.connect(self.show_license)
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        
    def show_license(self):
        license_dialog = LicenseDialog(self)
        license_dialog.accept_button.setVisible(False)
        license_dialog.decline_button.setText("Close")
        license_dialog.exec_()
        
    def show_about(self):
        QMessageBox.about(self, "About Quant Options Alpha Analyzer", 
                          "Quant Options Alpha Analyzer\n\n"
                          "© 2025 Alexander Husseini\n\n"
                          "A quantitative options analysis tool for evaluating "
                          "options trading opportunities based on alpha metrics.\n\n"
                          "Website: alexhusseini.com")
    
    def setup_main_tab(self):
        main_layout = QVBoxLayout(self.main_tab)
        
        # Equation Selection
        equation_group = QGroupBox("Equation Selection")
        equation_layout = QHBoxLayout()
        
        self.equation_selector = QComboBox()
        self.equation_selector.addItems([
            "SAS (Scalping Alpha Score)",
            "RA-SAS (Risk-Adjusted SAS)",
            "TAS (True Alpha Score)",
            "Expected Return (Full Quant Model)"
        ])
        self.equation_selector.currentIndexChanged.connect(self.update_results)
        
        equation_layout.addWidget(QLabel("Select Metric:"))
        equation_layout.addWidget(self.equation_selector)
        equation_layout.addStretch()
        
        equation_group.setLayout(equation_layout)
        main_layout.addWidget(equation_group)
        
        # Input Fields
        input_group = QGroupBox("Option Data Input")
        input_layout = QGridLayout()
        
        # Create input fields
        self.input_fields = {}
        
        # Basic option fields
        input_fields_data = [
            ("strike", "Strike Price:", 0, 0),
            ("delta", "Delta:", 0, 2),
            ("gamma", "Gamma:", 1, 0),
            ("theta", "Theta:", 1, 2),
            ("vega", "Vega:", 2, 0),
            ("bid", "Bid:", 2, 2),
            ("ask", "Ask:", 3, 0),
            ("slippage", "Slippage:", 3, 2),
            ("underlying", "Underlying Price:", 4, 0),
            ("atr", "ATR:", 4, 2),
            ("iv", "IV (%):", 5, 0)
        ]
        
        # Create input fields with tooltips
        for field_name, label_text, row, col in input_fields_data:
            label = QLabel(label_text)
            self.input_fields[field_name] = QDoubleSpinBox()
            self.input_fields[field_name].setDecimals(4)
            self.input_fields[field_name].setRange(0, 100000)
            
            if field_name == "slippage":
                self.input_fields[field_name].setValue(0.02)
            
            self.input_fields[field_name].valueChanged.connect(self.update_results)
            
            input_layout.addWidget(label, row, col)
            input_layout.addWidget(self.input_fields[field_name], row, col + 1)
        
        # Add tooltips
        self.setup_tooltips()
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Action Buttons - Organize in two rows to prevent text cutting off
        buttons_group = QGroupBox("Actions")
        buttons_layout = QGridLayout()
        
        self.calculate_btn = QPushButton("Add to Analysis")
        self.calculate_btn.clicked.connect(self.add_option)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_data)
        
        self.delete_selected_btn = QPushButton("Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_option)
        
        self.csv_import_btn = QPushButton("Import CSV")
        self.csv_import_btn.clicked.connect(self.import_csv)
        
        self.template_btn = QPushButton("CSV Template")
        self.template_btn.clicked.connect(self.download_csv_template)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        
        self.visualize_btn = QPushButton("Visualize Curve")
        self.visualize_btn.clicked.connect(self.visualize_curve)
        
        self.load_examples_btn = QPushButton("Load Examples")
        self.load_examples_btn.clicked.connect(self.load_example_contracts)
        
        # First row
        buttons_layout.addWidget(self.calculate_btn, 0, 0)
        buttons_layout.addWidget(self.delete_selected_btn, 0, 1)
        buttons_layout.addWidget(self.clear_btn, 0, 2)
        buttons_layout.addWidget(self.load_examples_btn, 0, 3)
        
        # Second row
        buttons_layout.addWidget(self.csv_import_btn, 1, 0)
        buttons_layout.addWidget(self.template_btn, 1, 1)
        buttons_layout.addWidget(self.export_btn, 1, 2)
        buttons_layout.addWidget(self.visualize_btn, 1, 3)
        
        buttons_group.setLayout(buttons_layout)
        main_layout.addWidget(buttons_group)
        
        # Auto Rank Checkbox
        rank_layout = QHBoxLayout()
        self.auto_rank_checkbox = QCheckBox("Auto-rank by selected metric")
        self.auto_rank_checkbox.setChecked(True)
        self.auto_rank_checkbox.toggled.connect(self.update_results)
        rank_layout.addWidget(self.auto_rank_checkbox)
        rank_layout.addStretch()
        main_layout.addLayout(rank_layout)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(13)
        self.results_table.setHorizontalHeaderLabels([
            "Strike", "Delta", "Gamma", "Theta", "Vega", 
            "Bid", "Ask", "Underlying", "ATR", "IV", "RV", 
            "Metric", "Result"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Enable sorting for the results table
        self.results_table.setSortingEnabled(True)
        
        # Make the results table allow row selection
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.results_table)
    
    def setup_guide_tab(self):
        guide_layout = QVBoxLayout(self.guide_tab)
        
        # Create a scroll area for the guide content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Formula explanations
        formulas = [
            ("SAS (Scalping Alpha Score)", 
             "SAS = (Delta * Gamma) / |Theta|", 
             "Used for rapid scalping opportunities. Measures the ratio of directional edge (Delta*Gamma) "
             "to time decay cost (Theta).",
             "Thresholds: SAS > 0.02 = Strong Alpha, SAS > 0.03 = Excellent Alpha"),
             
            ("RA-SAS (Risk-Adjusted SAS)", 
             "RA-SAS = (Delta * Gamma) / (|Theta| + Spread + Slippage)", 
             "Enhanced version of SAS that factors in execution costs (spread + slippage).",
             "Thresholds: RA-SAS > 0.015 = Strong Alpha, RA-SAS > 0.025 = Excellent Alpha"),
             
            ("TAS (True Alpha Score)", 
             "TAS = (Delta * Gamma) / |Theta| + (RV - IV) * Vega", 
             "Combines SAS with volatility edge. Best for swing trading positions. "
             "RV (Realized Volatility) = (ATR / Underlying Price) * sqrt(252)",
             "Thresholds: TAS > 0.03 = Strong Edge, TAS > 0.05 = Excellent Edge"),
             
            ("Expected Return",
             "Expected Return = RA-SAS + (RV - IV) * Vega",
             "Full quantitative model combining execution costs and volatility edge. "
             "Best for comprehensive analysis and position sizing.",
             "Thresholds: ER > 0.02 = Good Return, ER > 0.04 = Excellent Return")
        ]
        
        for title, formula, description, threshold in formulas:
            group = QGroupBox(title)
            group_layout = QVBoxLayout()
            
            formula_label = QLabel(f"<b>Formula:</b> {formula}")
            formula_label.setTextFormat(Qt.RichText)
            
            desc_label = QLabel(f"<b>Description:</b> {description}")
            desc_label.setTextFormat(Qt.RichText)
            desc_label.setWordWrap(True)
            
            threshold_label = QLabel(f"<b>Usage Guidance:</b> {threshold}")
            threshold_label.setTextFormat(Qt.RichText)
            threshold_label.setWordWrap(True)
            
            group_layout.addWidget(formula_label)
            group_layout.addWidget(desc_label)
            group_layout.addWidget(threshold_label)
            
            group.setLayout(group_layout)
            scroll_layout.addWidget(group)
        
        # Definitions section
        definitions_group = QGroupBox("Option Greeks & Terminology")
        definitions_layout = QVBoxLayout()
        
        definitions = [
            ("Delta", "Rate of change of option price with respect to underlying price. Range: 0 to 1 (calls) or -1 to 0 (puts)."),
            ("Gamma", "Rate of change of Delta with respect to underlying price. Higher Gamma means faster Delta changes."),
            ("Theta", "Rate of time decay. Negative value representing daily premium loss from passage of time."),
            ("Vega", "Option sensitivity to volatility changes. Represents premium change per 1% move in IV."),
            ("IV", "Implied Volatility - market's forecast of likely movement in underlying price."),
            ("RV", "Realized Volatility - actual historical volatility of the underlying."),
            ("ATR", "Average True Range - Volatility indicator measuring price range over a period (typically 14 days)."),
            ("Slippage", "Execution cost beyond the spread. Default 0.02 (2 cents per contract)."),
        ]
        
        for term, definition in definitions:
            term_layout = QHBoxLayout()
            
            term_label = QLabel(f"<b>{term}:</b>")
            term_label.setTextFormat(Qt.RichText)
            term_label.setFixedWidth(60)
            
            def_label = QLabel(definition)
            def_label.setWordWrap(True)
            
            term_layout.addWidget(term_label)
            term_layout.addWidget(def_label, 1)
            
            definitions_layout.addLayout(term_layout)
        
        definitions_group.setLayout(definitions_layout)
        scroll_layout.addWidget(definitions_group)
        
        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        
        guide_layout.addWidget(scroll_area)
    
    def setup_tooltips(self):
        tooltips = {
            "strike": "Option strike price",
            "delta": "Rate of change of option price with respect to underlying price (0-1 for calls, -1-0 for puts)",
            "gamma": "Rate of change of delta with respect to underlying price",
            "theta": "Rate of option price decay per day (usually negative)",
            "vega": "Option price sensitivity to volatility changes",
            "bid": "Current bid price",
            "ask": "Current ask price",
            "slippage": "Additional execution cost beyond the spread (default: 0.02)",
            "underlying": "Current price of the underlying asset",
            "atr": "Average True Range - volatility measure for the underlying",
            "iv": "Implied Volatility in percent (e.g., 30 for 30%)"
        }
        
        for field, tooltip in tooltips.items():
            self.input_fields[field].setToolTip(tooltip)
    
    def calculate_results(self, option_data):
        # Extract values from input
        delta = option_data["delta"]
        gamma = option_data["gamma"]
        theta = abs(option_data["theta"])  # Use absolute value for Theta
        vega = option_data["vega"]
        bid = option_data["bid"]
        ask = option_data["ask"]
        slippage = option_data["slippage"]
        underlying = option_data["underlying"]
        atr = option_data["atr"]
        iv = option_data["iv"] / 100  # Convert percentage to decimal
        
        # Calculate spread
        spread = ask - bid
        
        # Calculate RV (Realized Volatility)
        rv = (atr / underlying) * np.sqrt(252) if underlying > 0 else 0
        
        # Store RV for display
        option_data["rv"] = rv * 100  # Store as percentage
        
        # Calculate metrics based on selected equation
        index = self.equation_selector.currentIndex()
        
        if index == 0:  # SAS
            if theta > 0:
                result = (delta * gamma) / theta
            else:
                result = 0
            formula = "SAS"
            
        elif index == 1:  # RA-SAS
            denominator = theta + spread + slippage
            if denominator > 0:
                result = (delta * gamma) / denominator
            else:
                result = 0
            formula = "RA-SAS"
            
        elif index == 2:  # TAS
            if theta > 0:
                sas = (delta * gamma) / theta
            else:
                sas = 0
            vol_edge = (rv - iv) * vega
            result = sas + vol_edge
            formula = "TAS"
            
        else:  # Expected Return
            denominator = theta + spread + slippage
            if denominator > 0:
                ra_sas = (delta * gamma) / denominator
            else:
                ra_sas = 0
            vol_edge = (rv - iv) * vega
            result = ra_sas + vol_edge
            formula = "Expected Return"
        
        return formula, result
    
    def add_option(self):
        # Gather input values
        option_data = {}
        for field, input_widget in self.input_fields.items():
            option_data[field] = input_widget.value()
        
        # Calculate the selected metric
        formula, result = self.calculate_results(option_data)
        
        # Add the calculated result
        option_data["formula"] = formula
        option_data["result"] = result
        
        # Add to data storage
        self.options_data.append(option_data)
        
        # Update the table display
        self.update_results()
    
    def update_results(self):
        # Store current sorting state
        header = self.results_table.horizontalHeader()
        sort_column = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()
        
        # Temporarily disable sorting while updating
        self.results_table.setSortingEnabled(False)
        
        # Clear the table
        self.results_table.setRowCount(0)
        
        if not self.options_data:
            # Re-enable sorting before returning
            self.results_table.setSortingEnabled(True)
            return
        
        # Get base options data (sort if auto-rank is checked)
        options_to_display = self.options_data.copy()
        if self.auto_rank_checkbox.isChecked() and sort_column == 0:  # Only apply auto-rank if not custom sorted
            options_to_display.sort(key=lambda x: x["result"], reverse=True)
        
        # Find best result for highlighting
        best_result = max(option["result"] for option in options_to_display)
        
        # Populate table
        self.results_table.setRowCount(len(options_to_display))
        
        for row, option in enumerate(options_to_display):
            # Set values - use QTableWidgetItem for text and custom items for numerics to ensure proper sorting
            
            # Handle numeric columns with proper sorting
            strike_item = QTableWidgetItem()
            strike_item.setData(Qt.DisplayRole, float(option['strike']))
            self.results_table.setItem(row, 0, strike_item)
            
            delta_item = QTableWidgetItem()
            delta_item.setData(Qt.DisplayRole, float(option['delta']))
            delta_item.setData(Qt.DisplayRole, option['delta'])
            self.results_table.setItem(row, 1, delta_item)
            
            gamma_item = QTableWidgetItem()
            gamma_item.setData(Qt.DisplayRole, float(option['gamma']))
            self.results_table.setItem(row, 2, gamma_item)
            
            theta_item = QTableWidgetItem()
            theta_item.setData(Qt.DisplayRole, float(option['theta']))
            self.results_table.setItem(row, 3, theta_item)
            
            vega_item = QTableWidgetItem()
            vega_item.setData(Qt.DisplayRole, float(option['vega']))
            self.results_table.setItem(row, 4, vega_item)
            
            bid_item = QTableWidgetItem()
            bid_item.setData(Qt.DisplayRole, float(option['bid']))
            self.results_table.setItem(row, 5, bid_item)
            
            ask_item = QTableWidgetItem()
            ask_item.setData(Qt.DisplayRole, float(option['ask']))
            self.results_table.setItem(row, 6, ask_item)
            
            underlying_item = QTableWidgetItem()
            underlying_item.setData(Qt.DisplayRole, float(option['underlying']))
            self.results_table.setItem(row, 7, underlying_item)
            
            atr_item = QTableWidgetItem()
            atr_item.setData(Qt.DisplayRole, float(option['atr']))
            self.results_table.setItem(row, 8, atr_item)
            
            # Special format for percentage values
            iv_item = QTableWidgetItem()
            iv_item.setData(Qt.DisplayRole, float(option['iv']))
            iv_item.setText(f"{option['iv']:.2f}%")
            self.results_table.setItem(row, 9, iv_item)
            
            rv_item = QTableWidgetItem()
            rv_item.setData(Qt.DisplayRole, float(option['rv']))
            rv_item.setText(f"{option['rv']:.2f}%")
            self.results_table.setItem(row, 10, rv_item)
            
            # Text items
            metric_item = QTableWidgetItem(option["formula"])
            self.results_table.setItem(row, 11, metric_item)
            
            # Result with numeric sorting
            result_item = QTableWidgetItem()
            result_item.setData(Qt.DisplayRole, float(option['result']))
            result_item.setText(f"{option['result']:.4f}")
            self.results_table.setItem(row, 12, result_item)
            
            # Highlight best results with darker gold/yellow color
            if option["result"] >= best_result * 0.9:  # Within 10% of the best
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    # Use a darker gold/yellow shade
                    item.setBackground(QColor(240, 195, 80))  # Darker gold/yellow
                
            # Make second best (70-90% of best) a medium shade
            elif option["result"] >= best_result * 0.7:  # Within 30% of the best
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    item.setBackground(QColor(250, 220, 120))  # Medium gold/yellow
        
        # Re-enable sorting and restore previous sort
        self.results_table.setSortingEnabled(True)
        self.results_table.horizontalHeader().setSortIndicator(sort_column, sort_order)
    
    def clear_data(self):
        self.options_data = []
        self.results_table.setRowCount(0)
    
    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Options Chain CSV", "", "CSV Files (*.csv)")
        
        if not file_path:
            return
        
        try:
            df = pd.read_csv(file_path)
            
            # Try to map columns to our expected inputs
            mapping = {}
            header_map = {
                'strike': ['strike', 'strike price', 'strikeprice'],
                'delta': ['delta'],
                'gamma': ['gamma'],
                'theta': ['theta'],
                'vega': ['vega'],
                'bid': ['bid', 'bid price'],
                'ask': ['ask', 'ask price'],
                'iv': ['iv', 'implied volatility', 'impliedvolatility']
            }
            
            columns = [col.lower() for col in df.columns]
            
            for our_field, possible_names in header_map.items():
                for name in possible_names:
                    if name in columns:
                        mapping[our_field] = name
                        break
            
            # Check if we have the minimum required fields
            required_fields = ['strike', 'delta', 'gamma', 'theta']
            missing = [field for field in required_fields if field not in mapping]
            
            if missing:
                QMessageBox.warning(
                    self, "Missing Fields", 
                    f"The CSV is missing required fields: {', '.join(missing)}. "
                    f"The CSV columns are: {', '.join(df.columns)}")
                return
            
            # Get values for fields that apply to all options
            slippage = self.input_fields["slippage"].value()
            underlying = self.input_fields["underlying"].value()
            atr = self.input_fields["atr"].value()
            
            # Import the options
            for _, row in df.iterrows():
                option_data = {
                    'slippage': slippage,
                    'underlying': underlying,
                    'atr': atr
                }
                
                # Map CSV values to our fields
                for our_field, csv_field in mapping.items():
                    option_data[our_field] = float(row[csv_field])
                
                # Fill in any missing fields with defaults
                for field in self.input_fields:
                    if field not in option_data:
                        option_data[field] = 0.0
                
                # Calculate and add the option
                formula, result = self.calculate_results(option_data)
                option_data["formula"] = formula
                option_data["result"] = result
                self.options_data.append(option_data)
            
            self.update_results()
            QMessageBox.information(
                self, "Import Successful", 
                f"Successfully imported {len(df)} options from CSV.")
                
        except Exception as e:
            QMessageBox.critical(
                self, "Import Error", 
                f"Error importing CSV: {str(e)}")
    
    def export_results(self):
        if not self.options_data:
            QMessageBox.warning(
                self, "No Data", 
                "No data to export. Please add options first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv)")
        
        if not file_path:
            return
            
        try:
            df = pd.DataFrame(self.options_data)
            df.to_csv(file_path, index=False)
            QMessageBox.information(
                self, "Export Successful", 
                f"Results exported successfully to {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", 
                f"Error exporting results: {str(e)}")

    # Feature 1: Visualization methods
    def visualize_curve(self):
        """Visualize the options curve based on the current data"""
        if not self.options_data:
            QMessageBox.warning(self, "No Data", 
                               "No options data to visualize. Please add options first or load example contracts.")
            return
        
        # Create dialog to display the visualization
        dialog = QDialog(self)
        dialog.setWindowTitle("Option Contract Curve Visualization")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Controls for visualization
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Metric to Plot:"))
        
        # Dropdown to select score type
        score_selector = QComboBox()
        score_selector.addItems([
            "SAS (Scalping Alpha Score)",
            "RA-SAS (Risk-Adjusted SAS)",
            "TAS (True Alpha Score)",
            "Expected Return (Full Quant Model)"
        ])
        score_selector.setCurrentIndex(self.equation_selector.currentIndex())
        controls_layout.addWidget(score_selector)
        
        plot_btn = QPushButton("Update Plot")
        controls_layout.addWidget(plot_btn)
        
        layout.addLayout(controls_layout)
        
        # Create the matplotlib canvas
        canvas = MplCanvas(dialog, width=7, height=5, dpi=100)
        layout.addWidget(canvas)
        
        # Initial plot
        self._plot_curve(canvas, score_selector.currentIndex())
        
        # Connect signals
        plot_btn.clicked.connect(lambda: self._plot_curve(canvas, score_selector.currentIndex()))
        score_selector.currentIndexChanged.connect(lambda idx: self._plot_curve(canvas, idx))
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def _plot_curve(self, canvas, score_index):
        """Plot the option curve on the given canvas using the selected score type"""
        # Store current equation selection
        current_idx = self.equation_selector.currentIndex()
        
        # Temporarily set equation to the selected one for plotting
        self.equation_selector.setCurrentIndex(score_index)
        
        # Recalculate all options with the selected metric
        for option in self.options_data:
            formula, result = self.calculate_results(option)
            option["formula"] = formula
            option["result"] = result
        
        # Extract data for plotting
        strikes = [option["strike"] for option in self.options_data]
        results = [option["result"] for option in self.options_data]
        
        # Find the best option
        best_idx = results.index(max(results))
        
        # Clear the axes and plot the data
        canvas.axes.clear()
        canvas.axes.plot(strikes, results, 'o-', color='blue')
        canvas.axes.plot(strikes[best_idx], results[best_idx], 'o', color='green', markersize=10)
        
        # Add labels and title
        canvas.axes.set_xlabel('Strike Price')
        canvas.axes.set_ylabel(f'{self.equation_selector.currentText()} Value')
        canvas.axes.set_title(f'Option Contract Curve: {self.equation_selector.currentText()}')
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add text annotation for the best contract
        canvas.axes.annotate(f'Best: {strikes[best_idx]:.2f}', 
                             (strikes[best_idx], results[best_idx]),
                             xytext=(10, 10), textcoords='offset points',
                             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8))
        
        # Draw the plot
        canvas.fig.tight_layout()
        canvas.draw()
        
        # Restore original equation selection
        self.equation_selector.setCurrentIndex(current_idx)
    
    def load_example_contracts(self):
        """Load example contracts for demonstration"""
        # Ask for confirmation if there's existing data
        if self.options_data:
            reply = QMessageBox.question(self, 'Confirm Load Examples', 
                                     'This will clear existing data. Continue?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        
        # Clear existing data
        self.options_data = []
        
        # Example underlying price and ATR
        underlying_price = 100.0
        atr = 2.5
        
        # Set values in the UI
        self.input_fields["underlying"].setValue(underlying_price)
        self.input_fields["atr"].setValue(atr)
        
        # Example options data (realistic values for a range of strikes)
        example_options = [
            # Strike, Delta, Gamma, Theta, Vega, Bid, Ask, IV
            {"strike": 90.0, "delta": 0.82, "gamma": 0.031, "theta": -0.045, "vega": 0.052, "bid": 12.20, "ask": 12.40, "iv": 28.5},
            {"strike": 95.0, "delta": 0.65, "gamma": 0.048, "theta": -0.062, "vega": 0.078, "bid": 7.80, "ask": 8.00, "iv": 30.2},
            {"strike": 100.0, "delta": 0.50, "gamma": 0.052, "theta": -0.070, "vega": 0.085, "bid": 4.90, "ask": 5.10, "iv": 31.0},
            {"strike": 105.0, "delta": 0.35, "gamma": 0.047, "theta": -0.065, "vega": 0.082, "bid": 2.80, "ask": 3.00, "iv": 32.5},
            {"strike": 110.0, "delta": 0.22, "gamma": 0.038, "theta": -0.055, "vega": 0.068, "bid": 1.40, "ask": 1.60, "iv": 33.8},
            {"strike": 115.0, "delta": 0.12, "gamma": 0.025, "theta": -0.040, "vega": 0.048, "bid": 0.65, "ask": 0.75, "iv": 35.0}
        ]
        
        # Add each example option to the data
        for option in example_options:
            # Add common fields
            option["slippage"] = 0.02
            option["underlying"] = underlying_price
            option["atr"] = atr
            
            # Calculate and add the result
            formula, result = self.calculate_results(option)
            option["formula"] = formula
            option["result"] = result
            
            # Add to data storage
            self.options_data.append(option)
        
        # Update the table display (will use the new subtle coloring)
        self.update_results()
        
        # Inform the user
        QMessageBox.information(self, "Example Contracts Loaded", 
                               f"Successfully loaded {len(example_options)} example option contracts.")
        
    def setup_simulation_tab(self):
        """Setup the simulation tab for Feature 2: Simulated Alpha Engine"""
        sim_layout = QVBoxLayout(self.simulation_tab)
        
        # Title and introduction
        title_label = QLabel("Simulated Alpha Engine (Backtesting)")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        intro_label = QLabel("Simulate option price changes based on underlying price movements to estimate performance.")
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignCenter)
        
        sim_layout.addWidget(title_label)
        sim_layout.addWidget(intro_label)
        sim_layout.addSpacing(10)
        
        # Parameters section
        param_group = QGroupBox("Simulation Parameters")
        param_layout = QGridLayout()
        
        # Number of simulated trades
        param_layout.addWidget(QLabel("Number of Simulations:"), 0, 0)
        self.sim_trades = QDoubleSpinBox()
        self.sim_trades.setDecimals(0)
        self.sim_trades.setRange(1, 1000)
        self.sim_trades.setValue(10)
        param_layout.addWidget(self.sim_trades, 0, 1)
        
        # Starting stock price
        param_layout.addWidget(QLabel("Starting Stock Price:"), 1, 0)
        self.sim_price = QDoubleSpinBox()
        self.sim_price.setRange(1, 10000)
        self.sim_price.setValue(100)
        param_layout.addWidget(self.sim_price, 1, 1)
        
        # Assumed volatility
        param_layout.addWidget(QLabel("Assumed Volatility (%):"), 2, 0)
        self.sim_vol = QDoubleSpinBox()
        self.sim_vol.setRange(1, 200)
        self.sim_vol.setValue(30)
        param_layout.addWidget(self.sim_vol, 2, 1)
        
        # Holding period
        param_layout.addWidget(QLabel("Holding Period (days):"), 3, 0)
        self.sim_holding = QDoubleSpinBox()
        self.sim_holding.setDecimals(0)
        self.sim_holding.setRange(1, 5)
        self.sim_holding.setValue(1)
        param_layout.addWidget(self.sim_holding, 3, 1)
        
        # Use realistic execution checkbox
        self.sim_realistic = QCheckBox("Use Realistic Execution (include slippage/spread)")
        self.sim_realistic.setChecked(True)
        param_layout.addWidget(self.sim_realistic, 4, 0, 1, 2)
        
        param_group.setLayout(param_layout)
        sim_layout.addWidget(param_group)
        
        # Run simulation button
        button_layout = QHBoxLayout()
        self.run_sim_btn = QPushButton("Run Simulation")
        self.run_sim_btn.clicked.connect(self.run_simulation)
        
        # Add the visualize results button
        self.visualize_sim_btn = QPushButton("Visualize Results")
        self.visualize_sim_btn.clicked.connect(self.visualize_simulation_results)
        self.visualize_sim_btn.setEnabled(False)  # Initially disabled until we have results
        
        button_layout.addStretch()
        button_layout.addWidget(self.run_sim_btn)
        button_layout.addWidget(self.visualize_sim_btn)
        button_layout.addStretch()
        sim_layout.addLayout(button_layout)
        
        # Results table
        sim_layout.addWidget(QLabel("Simulation Results:"))
        self.sim_results_table = QTableWidget()
        self.sim_results_table.setColumnCount(7)
        self.sim_results_table.setHorizontalHeaderLabels([
            "Strike", "Initial Score", "Avg. Return ($)", "Avg. Return (%)", 
            "Win Rate", "Best Case", "Primary Edge Factor"
        ])
        self.sim_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Enable sorting for the simulation results table
        self.sim_results_table.setSortingEnabled(True)
        
        sim_layout.addWidget(self.sim_results_table)
        
        # Store simulation detailed results for visualization
        self.simulation_detailed_results = {}
    
    def run_simulation(self):
        """Run the options simulation based on user parameters"""
        if not self.options_data:
            QMessageBox.warning(self, "No Data", 
                               "No options data to simulate. Please add options first or load example contracts.")
            return
        
        # Get simulation parameters
        num_sims = int(self.sim_trades.value())
        stock_price = self.sim_price.value()
        volatility = self.sim_vol.value() / 100  # Convert from percentage
        holding_period = int(self.sim_holding.value())
        use_realistic = self.sim_realistic.isChecked()
        
        # Create a more responsive progress dialog
        progress = QProgressDialog("Running simulations...", "Cancel", 0, len(self.options_data) * num_sims, self)
        progress.setWindowTitle("Simulation Progress")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        # Will store simulation results for each option
        sim_results = []
        # Clear detailed results storage
        self.simulation_detailed_results = {}
        
        # Counter for progress updates
        sim_counter = 0
        
        # Run simulation for each option
        for option_idx, option in enumerate(self.options_data):
            # Update progress dialog description
            progress.setLabelText(f"Simulating option {option_idx+1} of {len(self.options_data)}\nStrike price: {option['strike']}")
            
            # Extract option parameters
            strike = option["strike"]
            delta = option["delta"]
            gamma = option["gamma"]
            theta = option["theta"]
            vega = option["vega"]
            iv = option["iv"] / 100  # Convert from percentage
            bid = option["bid"]
            ask = option["ask"]
            
            # Initial option value (mid-price)
            initial_value = (bid + ask) / 2
            
            # Storage for simulation results
            returns = []
            win_count = 0
            best_case = -float('inf')  # Initialize to negative infinity
            
            # Factor contribution trackers
            delta_contrib = 0
            gamma_contrib = 0
            theta_contrib = 0
            vega_contrib = 0
            
            # Detailed information for visualization
            detailed_data = {
                'returns': [],
                'delta_contributions': [],
                'gamma_contributions': [],
                'theta_contributions': [],
                'vega_contributions': []
            }
            
            # Run multiple simulations
            for sim_idx in range(num_sims):
                # Check if the user canceled
                if progress.wasCanceled():
                    QMessageBox.information(self, "Simulation Canceled", "Simulation was canceled by user.")
                    return
                    
                # Copy initial values
                current_price = stock_price
                option_value = initial_value
                
                # This sim's factor contributions
                this_delta_contrib = 0
                this_gamma_contrib = 0
                this_theta_contrib = 0
                this_vega_contrib = 0
                
                # Price path for the holding period
                for day in range(holding_period):
                    # Daily volatility
                    daily_vol = volatility / np.sqrt(252)
                    
                    # Generate random price move (random walk)
                    price_change = current_price * daily_vol * np.random.normal()
                    new_price = current_price + price_change
                    
                    # Option value change components
                    delta_change = delta * price_change
                    gamma_change = 0.5 * gamma * price_change**2
                    theta_change = theta / 252  # Daily theta
                    
                    # IV change (random but correlated with price move)
                    iv_change = 0.01 * np.random.normal() - 0.005 * np.sign(price_change)
                    vega_change = vega * iv_change * 100  # Vega per 1% change
                    
                    # Track factor contributions
                    delta_contrib += abs(delta_change)
                    gamma_contrib += abs(gamma_change)
                    theta_contrib += abs(theta_change)
                    vega_contrib += abs(vega_change)
                    
                    # For this individual simulation
                    this_delta_contrib += delta_change
                    this_gamma_contrib += gamma_change
                    this_theta_contrib += theta_change
                    this_vega_contrib += vega_change
                    
                    # Update option value
                    option_value += delta_change + gamma_change + theta_change + vega_change
                    
                    # Update price for next iteration
                    current_price = new_price
                
                # Apply realistic execution costs if selected
                if use_realistic:
                    # Apply slippage and spread to exit
                    exit_cost = option["slippage"]
                    if option_value > initial_value:  # Selling
                        exit_price = option_value - exit_cost
                    else:  # Buying back
                        exit_price = option_value + exit_cost
                else:
                    exit_price = option_value
                
                # Calculate return for this simulation
                sim_return = exit_price - initial_value
                returns.append(sim_return)
                
                # Store detailed information for this simulation
                detailed_data['returns'].append(sim_return)
                detailed_data['delta_contributions'].append(this_delta_contrib)
                detailed_data['gamma_contributions'].append(this_gamma_contrib)
                detailed_data['theta_contributions'].append(this_theta_contrib)
                detailed_data['vega_contributions'].append(this_vega_contrib)
                
                # Track win count and best case
                if sim_return > 0:
                    win_count += 1
                best_case = max(best_case, sim_return)
                
                # Update progress
                sim_counter += 1
                progress.setValue(sim_counter)
                
                # Process UI events to keep the application responsive
                QApplication.processEvents()
            
            # Calculate average return
            avg_return = sum(returns) / num_sims
            
            # Calculate win rate
            win_rate = (win_count / num_sims) * 100
            
            # Determine primary edge factor
            factors = {
                "Delta": delta_contrib,
                "Gamma": gamma_contrib,
                "Theta": theta_contrib,
                "Vega": vega_contrib
            }
            primary_factor = max(factors, key=factors.get)
            
            # Initial score for reference
            formula, score = self.calculate_results(option)
            
            # Ensure best_case has a valid value (handle case where all returns are negative)
            if best_case == -float('inf'):
                best_case = max(returns) if returns else 0.0
            
            # Add to results
            sim_results.append({
                "strike": strike,
                "initial_score": score,
                "avg_return": avg_return,
                "avg_return_pct": (avg_return / initial_value) * 100 if initial_value > 0 else 0,
                "win_rate": win_rate,
                "best_case": best_case,
                "primary_factor": primary_factor,
                "factor_contributions": {
                    "Delta": delta_contrib,
                    "Gamma": gamma_contrib,
                    "Theta": theta_contrib,
                    "Vega": vega_contrib
                }
            })
            
            # Store detailed results for visualization
            self.simulation_detailed_results[strike] = detailed_data
            
            # Process UI events to keep the application responsive
            QApplication.processEvents()
        
        # Close progress dialog
        progress.close()
        
        # If all simulations were canceled, return
        if not sim_results:
            return
        
        # Sort results by average return (descending)
        sim_results.sort(key=lambda x: x["avg_return"], reverse=True)
        
        # Store the results for visualization use
        self.sim_results = sim_results
        
        # Enable the visualization button now that we have results
        self.visualize_sim_btn.setEnabled(True)
        
        # Display results in the table
        self.sim_results_table.setRowCount(len(sim_results))
        
        for row, result in enumerate(sim_results):
            # Set values with proper sorting
            
            # Strike - numeric
            strike_item = QTableWidgetItem()
            strike_item.setData(Qt.DisplayRole, float(result['strike']))
            self.sim_results_table.setItem(row, 0, strike_item)
            
            # Initial score - numeric
            score_item = QTableWidgetItem()
            score_item.setData(Qt.DisplayRole, float(result['initial_score']))
            score_item.setText(f"{result['initial_score']:.4f}")
            self.sim_results_table.setItem(row, 1, score_item)
            
            # Average return ($) - numeric with color
            return_item = QTableWidgetItem()
            return_item.setData(Qt.DisplayRole, float(result['avg_return']))
            return_item.setText(f"${result['avg_return']:.2f}")
            
            if result['avg_return'] > 0:
                # Use a darker green for profits
                return_item.setBackground(QColor(75, 145, 75))  # Darker green
                return_item.setForeground(QColor(255, 255, 255))  # White text
            else:
                # Use a darker red for losses
                return_item.setBackground(QColor(145, 75, 75))  # Darker red
                return_item.setForeground(QColor(255, 255, 255))  # White text
            self.sim_results_table.setItem(row, 2, return_item)
            
            # Percent return - numeric with color
            pct_item = QTableWidgetItem()
            pct_item.setData(Qt.DisplayRole, float(result['avg_return_pct']))
            pct_item.setText(f"{result['avg_return_pct']:.2f}%")
            
            if result['avg_return_pct'] > 0:
                # Use a darker green for profits
                pct_item.setBackground(QColor(75, 145, 75))  # Darker green
                pct_item.setForeground(QColor(255, 255, 255))  # White text
            else:
                # Use a darker red for losses
                pct_item.setBackground(QColor(145, 75, 75))  # Darker red
                pct_item.setForeground(QColor(255, 255, 255))  # White text
            self.sim_results_table.setItem(row, 3, pct_item)
            
            # Win rate - numeric with percent
            win_item = QTableWidgetItem()
            win_item.setData(Qt.DisplayRole, float(result['win_rate']))
            win_item.setText(f"{result['win_rate']:.1f}%")
            self.sim_results_table.setItem(row, 4, win_item)
            
            # Best case - numeric with dollar - with safeguard
            best_item = QTableWidgetItem()
            try:
                best_case_value = float(result['best_case'])
                # Handle invalid values
                if not np.isfinite(best_case_value):
                    best_case_value = 0.0
                best_item.setData(Qt.DisplayRole, best_case_value)
                best_item.setText(f"${best_case_value:.2f}")
            except (ValueError, TypeError):
                # Fallback for any unexpected errors
                best_item.setData(Qt.DisplayRole, 0.0)
                best_item.setText("$0.00")
            self.sim_results_table.setItem(row, 5, best_item)
            
            # Primary factor - text
            factor_item = QTableWidgetItem(result['primary_factor'])
            # Color code by factor
            if result['primary_factor'] == "Delta":
                factor_item.setBackground(QColor(200, 200, 255))  # Blue
            elif result['primary_factor'] == "Gamma":
                factor_item.setBackground(QColor(255, 200, 255))  # Purple
            elif result['primary_factor'] == "Theta":
                factor_item.setBackground(QColor(255, 255, 200))  # Yellow
            elif result['primary_factor'] == "Vega":
                factor_item.setBackground(QColor(200, 255, 255))  # Cyan
            self.sim_results_table.setItem(row, 6, factor_item)
        
        # Re-enable sorting
        self.sim_results_table.setSortingEnabled(True)
        
        # Display summary message only if we have results
        if sim_results:
            QMessageBox.information(self, "Simulation Complete", 
                                  f"Completed {num_sims} simulations over {holding_period} days.\n\n"
                                  f"Best performing option: Strike ${sim_results[0]['strike']:.2f}\n"
                                  f"Average return: ${sim_results[0]['avg_return']:.2f} ({sim_results[0]['avg_return_pct']:.2f}%)\n"
                                  f"Primary edge factor: {sim_results[0]['primary_factor']}")

    def visualize_simulation_results(self):
        """Visualize the simulation results with multiple charts"""
        if not hasattr(self, 'sim_results') or not self.sim_results:
            QMessageBox.warning(self, "No Results", 
                               "No simulation results to visualize. Please run a simulation first.")
            return
        
        # Create dialog for visualizations
        dialog = QDialog(self)
        dialog.setWindowTitle("Simulation Results Visualization")
        dialog.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Tab widget for different visualizations
        tab_widget = QTabWidget()
        
        # Tab 1: Return Distributions
        distribution_tab = QWidget()
        dist_layout = QVBoxLayout(distribution_tab)
        
        # Controls for distribution
        dist_controls = QHBoxLayout()
        dist_controls.addWidget(QLabel("Select Strike:"))
        
        strike_selector = QComboBox()
        strikes = [str(result['strike']) for result in self.sim_results]
        strike_selector.addItems(strikes)
        dist_controls.addWidget(strike_selector)
        
        dist_layout.addLayout(dist_controls)
        
        # Canvas for distribution plot
        dist_canvas = MplCanvas(distribution_tab, width=8, height=5)
        dist_layout.addWidget(dist_canvas)
        
        # Tab 2: Comparison Chart
        comparison_tab = QWidget()
        comp_layout = QVBoxLayout(comparison_tab)
        
        # Controls for comparison
        comp_controls = QHBoxLayout()
        comp_controls.addWidget(QLabel("Metric to Compare:"))
        
        metric_selector = QComboBox()
        metric_selector.addItems(["Average Return ($)", "Average Return (%)", "Win Rate", "Primary Edge Factor"])
        comp_controls.addWidget(metric_selector)
        
        comp_layout.addLayout(comp_controls)
        
        # Canvas for comparison plot
        comp_canvas = MplCanvas(comparison_tab, width=8, height=5)
        comp_layout.addWidget(comp_canvas)
        
        # Tab 3: Greek Contributions
        greek_tab = QWidget()
        greek_layout = QVBoxLayout(greek_tab)
        
        # Canvas for greek contribution
        greek_canvas = MplCanvas(greek_tab, width=8, height=5)
        greek_layout.addWidget(greek_canvas)
        
        # Tab 4: Return vs Strike
        return_vs_strike_tab = QWidget()
        rvs_layout = QVBoxLayout(return_vs_strike_tab)
        
        # Canvas for return vs strike
        rvs_canvas = MplCanvas(return_vs_strike_tab, width=8, height=5)
        rvs_layout.addWidget(rvs_canvas)
        
        # Add all tabs
        tab_widget.addTab(distribution_tab, "Return Distribution")
        tab_widget.addTab(comparison_tab, "Strike Comparison")
        tab_widget.addTab(greek_tab, "Greek Contributions")
        tab_widget.addTab(return_vs_strike_tab, "Return vs Strike")
        
        layout.addWidget(tab_widget)
        
        # Function to plot distribution
        def plot_distribution():
            strike = float(strike_selector.currentText())
            detailed_data = self.simulation_detailed_results.get(strike)
            
            if not detailed_data:
                return
            
            returns = detailed_data['returns']
            
            dist_canvas.axes.clear()
            dist_canvas.axes.hist(returns, bins=20, alpha=0.7, color='blue')
            dist_canvas.axes.axvline(x=0, color='red', linestyle='--')
            
            # Calculate and show some stats
            mean_return = np.mean(returns)
            median_return = np.median(returns)
            std_return = np.std(returns)
            win_rate = sum(1 for r in returns if r > 0) / len(returns) * 100
            
            dist_canvas.axes.set_title(f'Return Distribution for Strike ${strike}')
            dist_canvas.axes.set_xlabel('Return ($)')
            dist_canvas.axes.set_ylabel('Frequency')
            
            # Add stats to the plot
            stats_text = (f'Mean: ${mean_return:.2f}\n'
                         f'Median: ${median_return:.2f}\n'
                         f'Std Dev: ${std_return:.2f}\n'
                         f'Win Rate: {win_rate:.1f}%')
            
            # Place the text box in the upper right
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            dist_canvas.axes.text(0.95, 0.95, stats_text, transform=dist_canvas.axes.transAxes, 
                                 fontsize=10, verticalalignment='top', horizontalalignment='right',
                                 bbox=props)
            
            dist_canvas.draw()
        
        # Function to plot comparison
        def plot_comparison():
            metric = metric_selector.currentIndex()
            
            strikes = [result['strike'] for result in self.sim_results]
            
            if metric == 0:  # Average Return ($)
                values = [result['avg_return'] for result in self.sim_results]
                title = 'Average Return ($) by Strike'
                ylabel = 'Return ($)'
                formatter = '${:.2f}'
                colors = ['green' if v > 0 else 'red' for v in values]
            elif metric == 1:  # Average Return (%)
                values = [result['avg_return_pct'] for result in self.sim_results]
                title = 'Average Return (%) by Strike'
                ylabel = 'Return (%)'
                formatter = '{:.1f}%'
                colors = ['green' if v > 0 else 'red' for v in values]
            elif metric == 2:  # Win Rate
                values = [result['win_rate'] for result in self.sim_results]
                title = 'Win Rate by Strike'
                ylabel = 'Win Rate (%)'
                formatter = '{:.1f}%'
                colors = ['blue' for _ in values]
            else:  # Primary Edge Factor
                # For this one, we'll do a stacked bar chart of all factors
                strikes = [result['strike'] for result in self.sim_results]
                delta_values = [result['factor_contributions']['Delta'] for result in self.sim_results]
                gamma_values = [result['factor_contributions']['Gamma'] for result in self.sim_results]
                theta_values = [result['factor_contributions']['Theta'] for result in self.sim_results]
                vega_values = [result['factor_contributions']['Vega'] for result in self.sim_results]
                
                # Normalize to percentages
                totals = [d+g+t+v for d,g,t,v in zip(delta_values, gamma_values, theta_values, vega_values)]
                delta_pct = [d/t*100 if t > 0 else 0 for d,t in zip(delta_values, totals)]
                gamma_pct = [g/t*100 if t > 0 else 0 for g,t in zip(gamma_values, totals)]
                theta_pct = [th/t*100 if t > 0 else 0 for th,t in zip(theta_values, totals)]
                vega_pct = [v/t*100 if t > 0 else 0 for v,t in zip(vega_values, totals)]
                
                comp_canvas.axes.clear()
                bar_width = 0.8
                x = np.arange(len(strikes))
                
                bottom = np.zeros(len(strikes))
                
                # Plot stacked bars
                p1 = comp_canvas.axes.bar(x, delta_pct, bar_width, bottom=bottom, label='Delta', color='royalblue')
                bottom += delta_pct
                p2 = comp_canvas.axes.bar(x, gamma_pct, bar_width, bottom=bottom, label='Gamma', color='violet')
                bottom += gamma_pct
                p3 = comp_canvas.axes.bar(x, theta_pct, bar_width, bottom=bottom, label='Theta', color='gold')
                bottom += theta_pct
                p4 = comp_canvas.axes.bar(x, vega_pct, bar_width, bottom=bottom, label='Vega', color='cyan')
                
                comp_canvas.axes.set_title('Greek Contribution by Strike')
                comp_canvas.axes.set_xlabel('Strike Price')
                comp_canvas.axes.set_ylabel('Contribution %')
                comp_canvas.axes.set_xticks(x)
                comp_canvas.axes.set_xticklabels([f'${s:.2f}' for s in strikes])
                comp_canvas.axes.legend()
                
                comp_canvas.draw()
                return
            
            comp_canvas.axes.clear()
            bars = comp_canvas.axes.bar(strikes, values, color=colors)
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                comp_canvas.axes.text(bar.get_x() + bar.get_width()/2., height,
                                     formatter.format(value),
                                     ha='center', va='bottom', rotation=0)
            
            comp_canvas.axes.set_title(title)
            comp_canvas.axes.set_xlabel('Strike Price')
            comp_canvas.axes.set_ylabel(ylabel)
            comp_canvas.axes.set_xticklabels([f'${s:.2f}' for s in strikes])
            
            comp_canvas.draw()
        
        # Function to plot Greek contributions for each strike
        def plot_greek_contributions():
            strikes = [result['strike'] for result in self.sim_results]
            
            # Extract absolute factor contributions
            delta_values = [result['factor_contributions']['Delta'] for result in self.sim_results]
            gamma_values = [result['factor_contributions']['Gamma'] for result in self.sim_results]
            theta_values = [result['factor_contributions']['Theta'] for result in self.sim_results]
            vega_values = [result['factor_contributions']['Vega'] for result in self.sim_results]
            
            # Set up the figure
            greek_canvas.axes.clear()
            
            x = np.arange(len(strikes))
            width = 0.2
            
            # Plot grouped bars
            greek_canvas.axes.bar(x - width*1.5, delta_values, width, label='Delta', color='royalblue')
            greek_canvas.axes.bar(x - width/2, gamma_values, width, label='Gamma', color='violet')
            greek_canvas.axes.bar(x + width/2, theta_values, width, label='Theta', color='gold')
            greek_canvas.axes.bar(x + width*1.5, vega_values, width, label='Vega', color='cyan')
            
            greek_canvas.axes.set_title('Absolute Greek Contributions by Strike')
            greek_canvas.axes.set_xlabel('Strike Price')
            greek_canvas.axes.set_ylabel('Absolute Contribution')
            greek_canvas.axes.set_xticks(x)
            greek_canvas.axes.set_xticklabels([f'${s:.2f}' for s in strikes])
            greek_canvas.axes.legend()
            
            greek_canvas.draw()
        
        # Function to plot return vs strike with win rate
        def plot_return_vs_strike():
            # Get the data and make sure it's sorted by strike price
            data = [(result['strike'], result['avg_return'], result['win_rate']) 
                    for result in self.sim_results]
            # Sort by strike price to ensure a clean line
            data.sort(key=lambda x: x[0])
            
            # Unpack the sorted data
            strikes = [item[0] for item in data]
            returns = [item[1] for item in data]
            win_rates = [item[2] for item in data]
            
            # Start with a clean slate
            rvs_canvas.fig.clear()
            rvs_canvas.axes = rvs_canvas.fig.add_subplot(111)
            
            # Create the second axis
            ax2 = rvs_canvas.axes.twinx()
            
            # Plot returns (blue line with markers)
            rvs_canvas.axes.plot(strikes, returns, '-', color='blue', linewidth=2.5, alpha=0.7)
            
            # Add return data points
            for i, ret in enumerate(returns):
                if ret > 0:
                    rvs_canvas.axes.plot(strikes[i], ret, 'o', color='green', markersize=8)
                else:
                    rvs_canvas.axes.plot(strikes[i], ret, 'o', color='red', markersize=8)
            
            # Plot win rate (orange line with square markers)
            ax2.plot(strikes, win_rates, '-', color='orange', linewidth=2.5, alpha=0.7)
            ax2.plot(strikes, win_rates, 's', color='orange', markersize=7)
            
            # Reference lines
            rvs_canvas.axes.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
            ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.3)
            
            # Labels and styling
            rvs_canvas.axes.set_xlabel('Strike Price', fontsize=10)
            rvs_canvas.axes.set_ylabel('Average Return ($)', color='blue', fontsize=10)
            ax2.set_ylabel('Win Rate (%)', color='orange', fontsize=10)
            rvs_canvas.axes.set_title('Return and Win Rate vs Strike Price')
            
            # Set y-axis colors
            rvs_canvas.axes.tick_params(axis='y', colors='blue')
            ax2.tick_params(axis='y', colors='orange')
            
            # Add strike price labels only at actual data points
            rvs_canvas.axes.set_xticks(strikes)
            rvs_canvas.axes.set_xticklabels([f'${s:.2f}' for s in strikes])
            
            # Sensible y-axis limits
            min_return = min(returns)
            max_return = max(returns)
            padding = (max_return - min_return) * 0.15 if max_return > min_return else 1.0
            rvs_canvas.axes.set_ylim(min_return - padding, max_return + padding)
            ax2.set_ylim(0, max(100, max(win_rates) * 1.1))
            
            # Add a legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='blue', marker='o', markersize=8, label='Avg Return ($)',
                       markerfacecolor='blue', linewidth=2),
                Line2D([0], [0], color='orange', marker='s', markersize=8, label='Win Rate (%)',
                       markerfacecolor='orange', linewidth=2)
            ]
            rvs_canvas.axes.legend(handles=legend_elements, loc='best')
            
            # Clean grid
            rvs_canvas.axes.grid(True, axis='x', linestyle='--', alpha=0.3)
            
            # Make sure everything fits
            rvs_canvas.fig.tight_layout()
            
            # Update the canvas
            rvs_canvas.draw()
        
        # Initial plots
        plot_distribution()
        plot_comparison()
        plot_greek_contributions()
        plot_return_vs_strike()
        
        # Connect signals
        strike_selector.currentIndexChanged.connect(plot_distribution)
        metric_selector.currentIndexChanged.connect(plot_comparison)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def download_csv_template(self):
        """Create and download a CSV template with the correct format for importing options"""
        # Define the headers needed for import
        headers = ["Strike", "Delta", "Gamma", "Theta", "Vega", "Bid", "Ask", "IV"]
        
        # Create example data rows (use realistic option chain values)
        example_data = [
            # Strike, Delta, Gamma, Theta, Vega, Bid, Ask, IV
            [100.0, 0.50, 0.0500, -0.0500, 0.0900, 4.90, 5.10, 30.0],
            [105.0, 0.35, 0.0450, -0.0450, 0.0850, 2.80, 3.00, 32.0],
            [110.0, 0.20, 0.0350, -0.0350, 0.0700, 1.40, 1.60, 34.0]
        ]
        
        # Create a DataFrame
        df = pd.DataFrame(example_data, columns=headers)
        
        # Get file save location from user
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV Template", "options_template.csv", "CSV Files (*.csv)")
        
        if not file_path:
            return
        
        try:
            # Save the template
            df.to_csv(file_path, index=False)
            
            # Show info message with explanation
            QMessageBox.information(
                self, "CSV Template Created", 
                f"CSV template has been saved to:\n{file_path}\n\n"
                f"This template includes the following required columns:\n"
                f"- Strike: The option strike price\n"
                f"- Delta: The option delta (0-1 for calls, -1-0 for puts)\n"
                f"- Gamma: The option gamma\n"
                f"- Theta: The option theta (usually negative)\n"
                f"- Vega: The option vega\n"
                f"- Bid: The current bid price\n"
                f"- Ask: The current ask price\n"
                f"- IV: Implied volatility as a percentage (e.g., 30 for 30%)\n\n"
                f"Fill in your data and use Import CSV to analyze your options chain."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Template Creation Error", 
                f"Error creating CSV template: {str(e)}")

    def delete_selected_option(self):
        """Delete the selected option from the results table"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select an option to delete by clicking on its row.")
            return
        
        # Get the row index of the selected option
        row = selected_rows[0].row()
        
        # Make sure we have a valid row
        if row < 0 or row >= len(self.options_data):
            QMessageBox.warning(self, "Selection Error", "Invalid selection. Please try again.")
            return
        
        # Confirm deletion
        strike = self.options_data[row]["strike"]
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                 f'Are you sure you want to delete the option with strike {strike}?',
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Remove from data list
            self.options_data.pop(row)
            
            # Update the table display
            self.update_results()
            
            # Inform the user
            QMessageBox.information(self, "Option Deleted", 
                                  f"Option with strike {strike} has been removed from analysis.")

def main():
    app = QApplication(sys.argv)
    window = OptionsAlphaAnalyzer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 