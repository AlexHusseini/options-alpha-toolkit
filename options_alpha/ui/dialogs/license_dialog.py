"""
License agreement dialog for Options Alpha Analyzer
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt


class LicenseDialog(QDialog):
    """Dialog displaying the license agreement for the application"""
    
    def __init__(self, parent=None):
        """Initialize the license dialog
        
        Args:
            parent: Parent widget
        """
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