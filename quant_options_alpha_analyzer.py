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

# Import our custom modules
from options_alpha.ui.canvas import MplCanvas
from options_alpha.ui.tabs.simulation_tab import SimulationTab
from options_alpha.ui.tabs.analyzer_tab import AnalyzerTab
from options_alpha.ui.tabs.guide_tab import GuideTab
from options_alpha.ui.dialogs.license_dialog import LicenseDialog
from options_alpha.ui.dialogs.hedge_calculator import HedgeCalculatorDialog

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
        
        # Initialize shared data
        self.options_data = []
        
        # Create tab widgets
        self.analyzer_tab = AnalyzerTab(self)
        self.guide_tab = GuideTab(self)
        self.simulation_tab = SimulationTab(self)
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.analyzer_tab, "🔢 Analyzer")
        self.tabs.addTab(self.guide_tab, "📘 Formula Guide")
        self.tabs.addTab(self.simulation_tab, "🔁 Simulated Alpha Engine")
        
        self.main_layout.addWidget(self.tabs)
        
        # Create menu bar
        self.setup_menu_bar()
        
    def setup_menu_bar(self):
        """Setup the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        
        hedge_calculator_action = tools_menu.addAction("Hedge Calculator")
        hedge_calculator_action.triggered.connect(self.show_hedge_calculator)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        view_license_action = help_menu.addAction("View License Agreement")
        view_license_action.triggered.connect(self.show_license)
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def show_hedge_calculator(self):
        """Show the hedge calculator dialog"""
        hedge_dialog = HedgeCalculatorDialog(self)
        
        # Try to pre-populate with data from analyzer tab if it's the active tab
        if self.tabs.currentWidget() == self.analyzer_tab and hasattr(self, 'options_data') and self.options_data:
            # Check if any option is selected in the analyzer tab
            selected_option = self.analyzer_tab.get_selected_option()
            if selected_option:
                # Determine position type based on delta
                position_type = "Long Call"
                if selected_option['delta'] < 0:
                    position_type = "Long Put"
                
                # Set position data
                hedge_dialog.set_position_data(
                    position_type=position_type,
                    quantity=1,  # Assume 1 contract
                    delta=selected_option['delta'],
                    gamma=selected_option['gamma'],
                    stock_price=selected_option['underlying']
                )
        
        hedge_dialog.exec_()
        
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

def main():
    app = QApplication(sys.argv)
    window = OptionsAlphaAnalyzer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 