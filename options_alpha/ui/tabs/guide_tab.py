"""
Formula guide tab for Options Alpha Analyzer
Contains explanations of the metrics and formulas used in the application
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt


class GuideTab(QWidget):
    """Guide tab explaining the formulas and metrics used in the application"""
    
    def __init__(self, parent=None):
        """Initialize the guide tab
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the guide tab UI"""
        guide_layout = QVBoxLayout(self)
        
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