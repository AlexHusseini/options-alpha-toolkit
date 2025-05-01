import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                            QComboBox, QTabWidget, QPushButton, QTableWidget, 
                            QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox, 
                            QDoubleSpinBox, QFileDialog, QMessageBox, QToolTip, 
                            QScrollArea)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

class OptionsAlphaAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quant Options Alpha Analyzer")
        self.setMinimumSize(900, 700)
        
        # Create the central widget and tab layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.guide_tab = QWidget()
        
        self.tabs.addTab(self.main_tab, "🔢 Analyzer")
        self.tabs.addTab(self.guide_tab, "📘 Formula Guide")
        
        self.main_layout.addWidget(self.tabs)
        
        # Setup tabs
        self.setup_main_tab()
        self.setup_guide_tab()
        
        # Data storage
        self.options_data = []
        
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
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("Add to Analysis")
        self.calculate_btn.clicked.connect(self.add_option)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_data)
        
        self.csv_import_btn = QPushButton("Import CSV")
        self.csv_import_btn.clicked.connect(self.import_csv)
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.clicked.connect(self.export_results)
        
        button_layout.addWidget(self.calculate_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.csv_import_btn)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
        
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
            "Calculation", "Result"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        # Clear the table
        self.results_table.setRowCount(0)
        
        if not self.options_data:
            return
        
        # Recalculate results based on current equation selection
        for i, option in enumerate(self.options_data):
            formula, result = self.calculate_results(option)
            option["formula"] = formula
            option["result"] = result
        
        # Sort data if auto-rank is checked
        if self.auto_rank_checkbox.isChecked():
            self.options_data.sort(key=lambda x: x["result"], reverse=True)
        
        # Find best result for highlighting
        best_result = max(option["result"] for option in self.options_data)
        
        # Populate table
        self.results_table.setRowCount(len(self.options_data))
        
        for row, option in enumerate(self.options_data):
            # Set values
            self.results_table.setItem(row, 0, QTableWidgetItem(f"{option['strike']:.2f}"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{option['delta']:.4f}"))
            self.results_table.setItem(row, 2, QTableWidgetItem(f"{option['gamma']:.6f}"))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{option['theta']:.4f}"))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{option['vega']:.4f}"))
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{option['bid']:.2f}"))
            self.results_table.setItem(row, 6, QTableWidgetItem(f"{option['ask']:.2f}"))
            self.results_table.setItem(row, 7, QTableWidgetItem(f"{option['underlying']:.2f}"))
            self.results_table.setItem(row, 8, QTableWidgetItem(f"{option['atr']:.2f}"))
            self.results_table.setItem(row, 9, QTableWidgetItem(f"{option['iv']:.2f}%"))
            self.results_table.setItem(row, 10, QTableWidgetItem(f"{option['rv']:.2f}%"))
            self.results_table.setItem(row, 11, QTableWidgetItem(option["formula"]))
            
            result_item = QTableWidgetItem(f"{option['result']:.4f}")
            self.results_table.setItem(row, 12, result_item)
            
            # Highlight best results
            if option["result"] >= best_result * 0.9:  # Within 10% of the best
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    item.setBackground(QColor(200, 255, 200))  # Light green
    
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

def main():
    app = QApplication(sys.argv)
    window = OptionsAlphaAnalyzer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 