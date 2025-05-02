"""
Simulation visualization for Options Alpha Analyzer
Provides visualization functions for simulation results
"""

import numpy as np
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QComboBox, QPushButton, QWidget, QTabWidget)
from PyQt5.QtCore import Qt
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import make_interp_spline, interp1d

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
        
        # Add more space at the top of the dialog for visualizations
        layout.setContentsMargins(10, 15, 10, 10)
        
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
        
        tab_widget.addTab(distribution_tab, "Return Distribution")
        
        # Tab 2: Greeks Contribution
        greek_tab = QWidget()
        greek_layout = QVBoxLayout(greek_tab)
        
        greek_canvas = canvas_class(greek_tab, width=8, height=5)
        greek_layout.addWidget(greek_canvas)
        
        tab_widget.addTab(greek_tab, "Greek Contributions")
        
        # Tab 3: Performance Metrics
        metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(metrics_tab)
        
        metrics_canvas = canvas_class(metrics_tab, width=8, height=5)
        metrics_layout.addWidget(metrics_canvas)
        
        tab_widget.addTab(metrics_tab, "Performance Metrics")
        
        # Tab 4: Probability Cone
        prob_cone_tab = QWidget()
        prob_cone_layout = QVBoxLayout(prob_cone_tab)
        
        # Controls for probability cone
        prob_cone_controls = QHBoxLayout()
        
        # Add volatility control
        prob_cone_controls.addWidget(QLabel("Volatility (%):"))
        volatility_input = QComboBox()
        volatility_input.addItems(["20", "30", "40", "50", "60"])
        volatility_input.setCurrentIndex(1)  # Default 30%
        prob_cone_controls.addWidget(volatility_input)
        
        # Add time horizon control
        prob_cone_controls.addWidget(QLabel("Days:"))
        days_input = QComboBox()
        days_input.addItems(["7", "14", "30", "60", "90"])
        days_input.setCurrentIndex(2)  # Default 30 days
        prob_cone_controls.addWidget(days_input)
        
        # Add confidence interval control
        prob_cone_controls.addWidget(QLabel("Confidence:"))
        confidence_input = QComboBox()
        confidence_input.addItems(["68% (1σ)", "95% (2σ)", "99.7% (3σ)"])
        confidence_input.setCurrentIndex(1)  # Default 95%
        prob_cone_controls.addWidget(confidence_input)
        
        prob_cone_layout.addLayout(prob_cone_controls)
        
        # Canvas for probability cone
        prob_cone_canvas = canvas_class(prob_cone_tab, width=8, height=5)
        prob_cone_layout.addWidget(prob_cone_canvas)
        
        tab_widget.addTab(prob_cone_tab, "Probability Cone")
        
        layout.addWidget(tab_widget)
        
        # Button row for actions
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Plot initial distribution
        def plot_return_distribution():
            strike_idx = strike_selector.currentIndex()
            if strike_idx < 0 or strike_idx >= len(sim_results):
                return
            
            selected_strike = sim_results[strike_idx]['strike']
            detailed_data = simulation_detailed_results.get(selected_strike, None)
            
            if not detailed_data or not detailed_data.get('returns', []):
                dist_canvas.axes.clear()
                dist_canvas.axes.text(0.5, 0.5, "No data available", 
                                     horizontalalignment='center',
                                     verticalalignment='center',
                                     transform=dist_canvas.axes.transAxes)
                dist_canvas.draw()
                return
            
            returns = detailed_data['returns']
            
            # Plot histogram
            dist_canvas.axes.clear()
            n, bins, patches = dist_canvas.axes.hist(returns, bins=20, density=True, alpha=0.7)
            
            # Add a line for the mean
            mean_return = np.mean(returns)
            max_height = n.max() if len(n) > 0 else 1
            dist_canvas.axes.axvline(mean_return, color='red', linestyle='dashed', linewidth=2)
            dist_canvas.axes.text(mean_return, max_height*0.95, f' Mean: ${mean_return:.2f}', 
                                color='red', fontweight='bold')
            
            # Label breakeven point
            dist_canvas.axes.axvline(0, color='black', linestyle='dotted', linewidth=1)
            dist_canvas.axes.text(0, max_height*0.8, ' Breakeven', rotation=90, 
                                 verticalalignment='top')
            
            # Calculate win rate
            win_count = sum(1 for r in returns if r > 0)
            win_rate = (win_count / len(returns)) * 100 if returns else 0
            
            dist_canvas.axes.set_title(f'Return Distribution for Strike ${selected_strike} (Win Rate: {win_rate:.1f}%)')
            dist_canvas.axes.set_xlabel('Return ($)')
            dist_canvas.axes.set_ylabel('Probability Density')
            dist_canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # Add padding to prevent cutoff
            dist_canvas.fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
            
            dist_canvas.draw()

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
            
            # Position legend above the chart to avoid overlap with bars
            greek_canvas.axes.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4)
            
            # Adjust padding to accommodate the legend
            greek_canvas.fig.subplots_adjust(top=0.85, bottom=0.15)
            
            greek_canvas.draw()
            
        def plot_performance_metrics():
            # Get the sorted strike prices and corresponding data
            data_with_strikes = [(result['strike'], result) for result in sim_results]
            data_with_strikes.sort(key=lambda x: x[0])  # Sort by strike price
            
            if not data_with_strikes:
                metrics_canvas.axes.clear()
                metrics_canvas.axes.text(0.5, 0.5, "No data available", 
                                        horizontalalignment='center',
                                        verticalalignment='center',
                                        transform=metrics_canvas.axes.transAxes)
                metrics_canvas.draw()
                return
                
            # Extract sorted data
            strikes = [item[0] for item in data_with_strikes]
            win_rates = [item[1]['win_rate'] for item in data_with_strikes]
            avg_returns = [item[1]['avg_return'] for item in data_with_strikes]
            
            # Clear previous figure to avoid stacking axes
            metrics_canvas.fig.clear()
            
            # Create figure with more padding to prevent cutoff
            metrics_canvas.fig.set_tight_layout(False)
            metrics_canvas.axes = metrics_canvas.fig.add_subplot(111)
            
            # Create smooth curves
            if len(strikes) >= 4:
                # If we have enough points, create a smooth interpolation
                # Create a finer x scale for the smooth curve
                strikes_fine = np.linspace(min(strikes), max(strikes), 300)
                
                # Generate smooth curves with cubic spline interpolation
                try:
                    # Win rates smooth curve
                    win_rate_smooth = interp1d(strikes, win_rates, kind='cubic', 
                                               bounds_error=False, fill_value="extrapolate")
                    win_rates_fine = win_rate_smooth(strikes_fine)
                    
                    # Avg returns smooth curve
                    avg_return_smooth = interp1d(strikes, avg_returns, kind='cubic', 
                                                bounds_error=False, fill_value="extrapolate")
                    avg_returns_fine = avg_return_smooth(strikes_fine)
                    
                    # Use the smoothed data
                    plot_strikes = strikes_fine
                    plot_win_rates = win_rates_fine
                    plot_avg_returns = avg_returns_fine
                except (ValueError, np.linalg.LinAlgError):
                    # Fallback to original data if interpolation fails
                    plot_strikes = strikes
                    plot_win_rates = win_rates
                    plot_avg_returns = avg_returns
            else:
                # Not enough points for cubic interpolation, use original data
                plot_strikes = strikes
                plot_win_rates = win_rates
                plot_avg_returns = avg_returns
            
            # Primary axis for win rate - smooth blue curve
            metrics_canvas.axes.set_xlabel('Strike Price ($)')
            metrics_canvas.axes.set_ylabel('Win Rate (%)', color='blue')
            win_line, = metrics_canvas.axes.plot(plot_strikes, plot_win_rates, '-', 
                                              color='royalblue', linewidth=2.5, label='Win Rate')
            # Add original points as markers
            metrics_canvas.axes.plot(strikes, win_rates, 'o', color='blue', markersize=6)
            metrics_canvas.axes.tick_params(axis='y', labelcolor='blue')
            metrics_canvas.axes.set_ylim([0, 100])
            
            # Secondary axis for returns - smooth green curve
            ax2 = metrics_canvas.axes.twinx()
            ax2.set_ylabel('Avg Return ($)', color='green')
            ret_line, = ax2.plot(plot_strikes, plot_avg_returns, '-', 
                               color='forestgreen', linewidth=2.5, label='Avg Return')
            # Add original points as markers
            ax2.plot(strikes, avg_returns, 'o', color='green', markersize=6)
            ax2.tick_params(axis='y', labelcolor='green')
            
            # Set sensible y limits for returns
            if avg_returns:
                max_return = max(avg_returns)
                min_return = min(avg_returns)
                range_returns = max_return - min_return
                # Add 20% padding
                ax2.set_ylim([min_return - 0.2 * range_returns, max_return + 0.2 * range_returns])
            
            # Set up legend entries
            legend_lines = [win_line, ret_line]
            legend_labels = ['Win Rate (%)', 'Avg Return ($)']
            
            # Add grid
            metrics_canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # Title and legend - place it inside the plot for better visibility
            metrics_canvas.axes.set_title('Performance Metrics by Strike Price')
            
            # Create a legend that works with multiple axes - moved above the plot
            metrics_canvas.fig.legend(legend_lines, legend_labels, 
                                    loc='upper center', bbox_to_anchor=(0.5, 0.97), 
                                    ncol=2, fancybox=True, shadow=True)
            
            # Adjust layout to make room for legend at top and prevent curve cutoff
            metrics_canvas.fig.subplots_adjust(top=0.85, bottom=0.1, left=0.1, right=0.9)
            
            metrics_canvas.draw()
            
        def plot_probability_cone():
            # Get user-selected parameters
            volatility = float(volatility_input.currentText()) / 100  # Convert from percentage
            days = int(days_input.currentText())
            confidence_idx = confidence_input.currentIndex()
            
            # Map confidence index to standard deviations
            std_devs = [1.0, 2.0, 3.0][confidence_idx]
            conf_pct = ["68%", "95%", "99.7%"][confidence_idx]
            
            # Use the current stock price from the first result (assumes all have same underlying)
            if not sim_results:
                return
                
            # Try to get the stock price from sim_results
            stock_price = 100  # Default fallback
            if hasattr(parent, 'sim_price') and hasattr(parent.sim_price, 'value'):
                stock_price = parent.sim_price.value()
            
            # Create time points
            time_points = np.linspace(0, days, 100)
            
            # Calculate the standard deviation at each time point
            std_dev = stock_price * volatility * np.sqrt(time_points / 252)
            
            # Calculate the expected range at each time point
            upper_bound = stock_price * np.exp(std_devs * std_dev / stock_price)
            lower_bound = stock_price * np.exp(-std_devs * std_dev / stock_price)
            
            # Create price paths for visualization (optional)
            num_paths = 30
            price_paths = []
            for _ in range(num_paths):
                path = [stock_price]
                for i in range(1, len(time_points)):
                    daily_vol = volatility / np.sqrt(252)
                    dt = time_points[i] - time_points[i-1]
                    price_change = path[-1] * daily_vol * np.sqrt(dt) * np.random.normal()
                    new_price = path[-1] + price_change
                    path.append(new_price)
                price_paths.append(path)
            
            # Plot the probability cone
            prob_cone_canvas.axes.clear()
            
            # Plot the cone
            prob_cone_canvas.axes.fill_between(time_points, lower_bound, upper_bound, 
                                            color='lightblue', alpha=0.5, 
                                            label=f'{conf_pct} Confidence Interval')
            
            # Plot the median line
            prob_cone_canvas.axes.plot(time_points, [stock_price] * len(time_points), 
                                    'b-', label='Starting Price')
            
            # Plot the sample paths
            for path in price_paths:
                prob_cone_canvas.axes.plot(time_points, path, 'k-', alpha=0.1)
            
            # Add labels and title
            prob_cone_canvas.axes.set_title(f'Price Probability Cone ({volatility*100:.0f}% Volatility, {days} Days)')
            prob_cone_canvas.axes.set_xlabel('Days')
            prob_cone_canvas.axes.set_ylabel('Price ($)')
            
            # Position legend in a better location
            prob_cone_canvas.axes.legend(loc='upper right')
            prob_cone_canvas.axes.grid(True, linestyle='--', alpha=0.7)
            
            # Add standard deviation markers at end
            end_time = days
            for i, sd in enumerate([1.0, 2.0, 3.0]):
                if sd <= std_devs:
                    upper_price = stock_price * np.exp(sd * volatility * np.sqrt(end_time / 252))
                    lower_price = stock_price * np.exp(-sd * volatility * np.sqrt(end_time / 252))
                    
                    # Standard deviation at the end
                    prob_cone_canvas.axes.annotate(f'{sd}σ', xy=(end_time, upper_price),
                                              xytext=(5, 0), textcoords='offset points',
                                              fontsize=8, fontstyle='italic')
                    prob_cone_canvas.axes.annotate(f'{sd}σ', xy=(end_time, lower_price),
                                              xytext=(5, 0), textcoords='offset points',
                                              fontsize=8, fontstyle='italic')
            
            # Adjust padding to prevent cutoff
            prob_cone_canvas.fig.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9)
            
            prob_cone_canvas.draw()
        
        # Connect signals
        strike_selector.currentIndexChanged.connect(plot_return_distribution)
        volatility_input.currentIndexChanged.connect(plot_probability_cone)
        days_input.currentIndexChanged.connect(plot_probability_cone)
        confidence_input.currentIndexChanged.connect(plot_probability_cone)
        
        # Initial plots
        plot_return_distribution()
        plot_greek_contributions()
        plot_performance_metrics()
        plot_probability_cone()
        
        return dialog 