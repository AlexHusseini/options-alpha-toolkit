"""
Main analyzer tab for Options Alpha Analyzer
Contains the primary option analysis functionality
"""

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QComboBox, QPushButton, QTableWidget, 
                            QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox, 
                            QDoubleSpinBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from options_alpha.ui.canvas import MplCanvas
from options_alpha.ui.dialogs.hedge_calculator import HedgeCalculatorDialog


class AnalyzerTab(QWidget):
    """Main analysis tab for option contracts"""
    
    def __init__(self, parent=None):
        """Initialize the analyzer tab
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.parent_window = parent
        self.options_data = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the analyzer tab UI"""
        main_layout = QVBoxLayout(self)
        
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
        
        # Add hedge calculator button
        self.hedge_btn = QPushButton("Hedge Calculator")
        self.hedge_btn.clicked.connect(self.show_hedge_calculator)
        equation_layout.addWidget(self.hedge_btn)
        
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
    
    def setup_tooltips(self):
        """Setup tooltips for input fields"""
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
        """Calculate option metrics based on the selected equation
        
        Args:
            option_data: Dictionary containing option parameters
            
        Returns:
            tuple: (formula name, calculated result)
        """
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
        """Add current input values as a new option to analyze"""
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
        
        # If parent window exists, also update its options_data reference
        if hasattr(self.parent_window, 'options_data'):
            self.parent_window.options_data = self.options_data
    
    def update_results(self):
        """Update the results table with current options data"""
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
        """Clear all option data and reset the table"""
        self.options_data = []
        self.results_table.setRowCount(0)
        
        # If parent window exists, also update its options_data reference
        if hasattr(self.parent_window, 'options_data'):
            self.parent_window.options_data = self.options_data
    
    def import_csv(self):
        """Import options data from a CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Options Chain CSV", "", "CSV Files (*.csv)")
        
        if not file_path:
            return
        
        try:
            df = pd.read_csv(file_path)
            
            # Display column debug info in case of issues
            columns_info = ', '.join(df.columns)
            print(f"Detected columns: {columns_info}")
            
            # Try to map columns to our expected inputs
            mapping = {}
            header_map = {
                'strike': ['strike', 'strike price', 'strikeprice', 'Strike', 'Strike Price', 'StrikePrice'],
                'delta': ['delta', 'Delta'],
                'gamma': ['gamma', 'Gamma'],
                'theta': ['theta', 'Theta'],
                'vega': ['vega', 'Vega'],
                'bid': ['bid', 'bid price', 'Bid', 'Bid Price'],
                'ask': ['ask', 'ask price', 'Ask', 'Ask Price'],
                'iv': ['iv', 'implied volatility', 'impliedvolatility', 'IV', 'Implied Volatility', 'ImpliedVolatility']
            }
            
            # Check for exact matches first (case sensitive)
            for our_field, possible_names in header_map.items():
                if our_field in df.columns:
                    mapping[our_field] = our_field
                    continue
                
                # Then try case-insensitive matches
                for name in possible_names:
                    if name in df.columns:
                        mapping[our_field] = name
                        break
            
            # If we still don't have mappings, try lowercasing everything
            if len(mapping) < len(header_map):
                lowercase_columns = [col.lower() for col in df.columns]
                for our_field, possible_names in header_map.items():
                    if our_field in mapping:
                        continue
                    
                    lowercase_names = [name.lower() for name in possible_names]
                    for i, col in enumerate(lowercase_columns):
                        if col in lowercase_names:
                            mapping[our_field] = df.columns[i]  # Use original case
                            break
            
            # Check if we have the minimum required fields
            required_fields = ['strike', 'delta', 'gamma', 'theta']
            missing = [field for field in required_fields if field not in mapping]
            
            if missing:
                QMessageBox.warning(
                    self, "Missing Fields", 
                    f"The CSV is missing required fields: {', '.join(missing)}.\n\n"
                    f"The CSV columns are: {', '.join(df.columns)}\n\n"
                    f"Expected column names: strike, delta, gamma, theta, vega, bid, ask, iv\n"
                    f"(Column names are case-sensitive)")
                return
            
            # Get values for fields that apply to all options
            slippage = self.input_fields["slippage"].value()
            underlying = self.input_fields["underlying"].value()
            atr = self.input_fields["atr"].value()
            
            # Import the options
            successful_imports = 0
            for _, row in df.iterrows():
                try:
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
                    successful_imports += 1
                except Exception as e:
                    print(f"Error importing row: {str(e)}")
                    continue
            
            if successful_imports > 0:
                self.update_results()
                QMessageBox.information(
                    self, "Import Successful", 
                    f"Successfully imported {successful_imports} options from CSV.")
                
                # If parent window exists, also update its options_data reference
                if hasattr(self.parent_window, 'options_data'):
                    self.parent_window.options_data = self.options_data
            else:
                QMessageBox.critical(
                    self, "Import Error", 
                    "Could not import any options from the CSV. Please check the file format.")
                
        except Exception as e:
            QMessageBox.critical(
                self, "Import Error", 
                f"Error importing CSV: {str(e)}")
    
    def export_results(self):
        """Export options data to a CSV file"""
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
        """Plot the option curve on the given canvas using the selected score type
        
        Args:
            canvas: The MplCanvas to plot on
            score_index: Index of the selected score type
        """
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
        
        # Update the table display
        self.update_results()
        
        # If parent window exists, also update its options_data reference
        if hasattr(self.parent_window, 'options_data'):
            self.parent_window.options_data = self.options_data
        
        # Inform the user
        QMessageBox.information(self, "Example Contracts Loaded", 
                               f"Successfully loaded {len(example_options)} example option contracts.")
                               
    def download_csv_template(self):
        """Create and download a CSV template with the correct format for importing options"""
        # Define the headers needed for import - use lowercase to match import function expectations
        headers = ["strike", "delta", "gamma", "theta", "vega", "bid", "ask", "iv"]
        
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
                f"- strike: The option strike price\n"
                f"- delta: The option delta (0-1 for calls, -1-0 for puts)\n"
                f"- gamma: The option gamma\n"
                f"- theta: The option theta (usually negative)\n"
                f"- vega: The option vega\n"
                f"- bid: The current bid price\n"
                f"- ask: The current ask price\n"
                f"- iv: Implied volatility as a percentage (e.g., 30 for 30%)\n\n"
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
            
            # If parent window exists, also update its options_data reference
            if hasattr(self.parent_window, 'options_data'):
                self.parent_window.options_data = self.options_data
            
            # Inform the user
            QMessageBox.information(self, "Option Deleted", 
                                  f"Option with strike {strike} has been removed from analysis.")

    def get_selected_option(self):
        """Get the currently selected option data
        
        Returns:
            dict: Selected option data or None if no option is selected
        """
        selected_rows = self.results_table.selectionModel().selectedRows()
        if selected_rows and self.options_data:
            row = selected_rows[0].row()
            if 0 <= row < len(self.options_data):
                return self.options_data[row]
        return None
        
    def show_hedge_calculator(self):
        """Show the hedge calculator dialog"""
        # Get selected option data if available
        selected_option = self.get_selected_option()
        
        # Open hedge calculator dialog
        hedge_dialog = HedgeCalculatorDialog(self)
        
        # Pre-populate with selected option data if available
        if selected_option:
            # Determine position type based on delta
            position_type = "Long Call"
            if selected_option['delta'] < 0:
                position_type = "Long Put"
            
            # Set position data using the new method
            hedge_dialog.set_position_data(
                position_type=position_type,
                quantity=1,  # Assume 1 contract
                delta=selected_option['delta'],
                gamma=selected_option['gamma'],
                stock_price=selected_option['underlying']
            )
        
        hedge_dialog.exec_() 