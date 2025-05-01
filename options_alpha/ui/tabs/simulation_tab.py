"""
Simulation tab for Options Alpha Analyzer
Provides Monte Carlo simulations for options trading strategies
"""

import numpy as np
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QDoubleSpinBox, QCheckBox, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QGroupBox, QMessageBox, QProgressDialog, 
                            QApplication, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont

from options_alpha.ui.visualizations.simulation_visualizer import SimulationVisualizer


class SimulationTab(QWidget):
    """Tab for running Monte Carlo simulations on options strategies"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.sim_results = None
        self.simulation_detailed_results = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the simulation tab UI"""
        sim_layout = QVBoxLayout(self)
        
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
        
    def run_simulation(self):
        """Run the options simulation based on user parameters"""
        # Get options data from parent window
        if not hasattr(self.parent_window, 'options_data') or not self.parent_window.options_data:
            QMessageBox.warning(self, "No Data", 
                               "No options data to simulate. Please add options first or load example contracts.")
            return
        
        options_data = self.parent_window.options_data
        
        # Get simulation parameters
        num_sims = int(self.sim_trades.value())
        stock_price = self.sim_price.value()
        volatility = self.sim_vol.value() / 100  # Convert from percentage
        holding_period = int(self.sim_holding.value())
        use_realistic = self.sim_realistic.isChecked()
        
        # Create a more responsive progress dialog
        progress = QProgressDialog("Running simulations...", "Cancel", 0, len(options_data) * num_sims, self)
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
        for option_idx, option in enumerate(options_data):
            # Update progress dialog description
            progress.setLabelText(f"Simulating option {option_idx+1} of {len(options_data)}\nStrike price: {option['strike']}")
            
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
                return_value = exit_price - initial_value
                return_pct = (return_value / initial_value) * 100 if initial_value > 0 else 0
                
                # Track results
                returns.append(return_value)
                detailed_data['returns'].append(return_value)
                detailed_data['delta_contributions'].append(this_delta_contrib)
                detailed_data['gamma_contributions'].append(this_gamma_contrib)
                detailed_data['theta_contributions'].append(this_theta_contrib)
                detailed_data['vega_contributions'].append(this_vega_contrib)
                
                if return_value > 0:
                    win_count += 1
                
                best_case = max(best_case, return_value)
                
                # Update progress
                sim_counter += 1
                progress.setValue(sim_counter)
                QApplication.processEvents()  # Keep UI responsive
            
            # Calculate average return and win rate
            if returns:
                avg_return = sum(returns) / len(returns)
                avg_return_pct = (avg_return / initial_value) * 100 if initial_value > 0 else 0
                win_rate = (win_count / len(returns)) * 100
            else:
                avg_return = 0
                avg_return_pct = 0
                win_rate = 0
            
            # Determine primary edge factor
            total_contrib = delta_contrib + gamma_contrib + theta_contrib + vega_contrib
            factor_contribs = {
                "Delta": delta_contrib / total_contrib if total_contrib > 0 else 0,
                "Gamma": gamma_contrib / total_contrib if total_contrib > 0 else 0,
                "Theta": theta_contrib / total_contrib if total_contrib > 0 else 0,
                "Vega": vega_contrib / total_contrib if total_contrib > 0 else 0
            }
            
            # Determine the primary edge factor
            primary_factor = max(factor_contribs.items(), key=lambda x: x[1])[0]
            
            # Calculate initial score from base analyzer
            # Check if the parent window has an analyzer_tab attribute to get the calculate_results method
            formula = "N/A"
            score = 0
            if hasattr(self.parent_window, 'analyzer_tab') and hasattr(self.parent_window.analyzer_tab, 'calculate_results'):
                formula, score = self.parent_window.analyzer_tab.calculate_results(option)
            
            # Store simulation results
            option_result = {
                "strike": strike,
                "initial_score": score,
                "avg_return": avg_return,
                "avg_return_pct": avg_return_pct,
                "win_rate": win_rate,
                "best_case": best_case,
                "primary_factor": primary_factor,
                "factor_contributions": factor_contribs
            }
            
            # Add to results
            sim_results.append(option_result)
            
            # Store detailed data for visualization
            self.simulation_detailed_results[strike] = detailed_data
        
        # Close progress dialog
        progress.close()
        
        # Store the results
        self.sim_results = sim_results
        
        # Enable the visualize button now that we have results
        self.visualize_sim_btn.setEnabled(True)
        
        # Update the results table
        self.update_results_table()
        
        # Show completion message
        QMessageBox.information(self, "Simulation Complete", 
                              f"Successfully completed {num_sims} simulations for {len(options_data)} option contracts.")
    
    def visualize_simulation_results(self):
        """Visualize the simulation results with multiple charts"""
        if not self.sim_results:
            QMessageBox.warning(self, "No Results", 
                              "No simulation results to visualize. Please run a simulation first.")
            return
        
        # Use the SimulationVisualizer to show the visualization dialog
        from options_alpha.ui.canvas import MplCanvas
        dialog = SimulationVisualizer.create_visualization_dialog(
            self, self.sim_results, self.simulation_detailed_results, MplCanvas
        )
        dialog.exec_() 

    def update_results_table(self):
        """Update the simulation results table with the current results"""
        if not self.sim_results:
            return
            
        # Sort results by average return (descending)
        self.sim_results.sort(key=lambda x: x["avg_return"], reverse=True)
        
        # Update the results table
        self.sim_results_table.setSortingEnabled(False)
        self.sim_results_table.setRowCount(len(self.sim_results))
        
        for row, result in enumerate(self.sim_results):
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