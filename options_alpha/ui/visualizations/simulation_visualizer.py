"""
Simulation visualization for Options Alpha Analyzer
Provides visualization functions for simulation results
"""

import numpy as np
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QPushButton, QWidget, QTabWidget)
from PyQt5.QtCore import Qt
from matplotlib.lines import Line2D

class SimulationVisualizer:
    """Class to visualize Monte Carlo simulation results"""
    
    @staticmethod
    def create_visualization_dialog(parent, sim_results, simulation_detailed_results, canvas_class):
        """
        Create a dialog with tabs for different simulation visualizations
        
        Args:
            parent: The parent widget
            sim_results: List of dictionaries with simulation results
            simulation_detailed_results: Dictionary with detailed results by strike
            canvas_class: The MplCanvas class to use for plotting
        
        Returns:
            QDialog: The visualization dialog
        """
        # Create dialog for visualizations
        dialog = QDialog(parent)
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
        strikes = [str(result['strike']) for result in sim_results]
        strike_selector.addItems(strikes)
        dist_controls.addWidget(strike_selector)
        
        dist_layout.addLayout(dist_controls)
        
        # Canvas for distribution plot
        dist_canvas = canvas_class(distribution_tab, width=8, height=5)
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
        comp_canvas = canvas_class(comparison_tab, width=8, height=5)
        comp_layout.addWidget(comp_canvas)
        
        # Tab 3: Greek Contributions
        greek_tab = QWidget()
        greek_layout = QVBoxLayout(greek_tab)
        
        # Canvas for greek contribution
        greek_canvas = canvas_class(greek_tab, width=8, height=5)
        greek_layout.addWidget(greek_canvas)
        
        # Tab 4: Return vs Strike
        return_vs_strike_tab = QWidget()
        rvs_layout = QVBoxLayout(return_vs_strike_tab)
        
        # Canvas for return vs strike
        rvs_canvas = canvas_class(return_vs_strike_tab, width=8, height=5)
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
            detailed_data = simulation_detailed_results.get(strike)
            
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
            
            strikes = [result['strike'] for result in sim_results]
            
            if metric == 0:  # Average Return ($)
                values = [result['avg_return'] for result in sim_results]
                title = 'Average Return ($) by Strike'
                ylabel = 'Return ($)'
                formatter = '${:.2f}'
                colors = ['green' if v > 0 else 'red' for v in values]
            elif metric == 1:  # Average Return (%)
                values = [result['avg_return_pct'] for result in sim_results]
                title = 'Average Return (%) by Strike'
                ylabel = 'Return (%)'
                formatter = '{:.1f}%'
                colors = ['green' if v > 0 else 'red' for v in values]
            elif metric == 2:  # Win Rate
                values = [result['win_rate'] for result in sim_results]
                title = 'Win Rate by Strike'
                ylabel = 'Win Rate (%)'
                formatter = '{:.1f}%'
                colors = ['blue' for _ in values]
            else:  # Primary Edge Factor
                # For this one, we'll do a stacked bar chart of all factors
                strikes = [result['strike'] for result in sim_results]
                delta_values = [result['factor_contributions']['Delta'] for result in sim_results]
                gamma_values = [result['factor_contributions']['Gamma'] for result in sim_results]
                theta_values = [result['factor_contributions']['Theta'] for result in sim_results]
                vega_values = [result['factor_contributions']['Vega'] for result in sim_results]
                
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
            strikes = [result['strike'] for result in sim_results]
            
            # Extract absolute factor contributions
            delta_values = [result['factor_contributions']['Delta'] for result in sim_results]
            gamma_values = [result['factor_contributions']['Gamma'] for result in sim_results]
            theta_values = [result['factor_contributions']['Theta'] for result in sim_results]
            vega_values = [result['factor_contributions']['Vega'] for result in sim_results]
            
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
                    for result in sim_results]
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
        return dialog 