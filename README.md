# Quant Options Alpha Analyzer

A desktop application for quantitative analysis of options trading opportunities based on various alpha metrics.

## Features

- **Multiple Alpha Metrics**: Calculate SAS, RA-SAS, TAS, and Expected Return
- **Real-time Analysis**: Analyze options as you input data
- **Sortable Results**: Automatically rank options by their alpha metrics
- **Data Import/Export**: Import option chains from CSV and export analysis results
- **Formula Guide**: Built-in explanations of each formula and when to use it

## Installation

### Requirements
- Python 3.7+
- PyQt5
- NumPy
- Pandas

### Setup

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install PyQt5 numpy pandas
```

3. Run the application:

```bash
python quant_options_alpha_analyzer.py
```

## Usage

### Basic Operation

1. Select a metric to calculate from the dropdown menu
2. Enter option data in the input fields:
   - Strike price
   - Greeks (Delta, Gamma, Theta, Vega)
   - Bid/Ask prices
   - Underlying price and ATR
   - Implied Volatility (IV)
3. Click "Add to Analysis" to add the option to the results table
4. Results are automatically ranked by the selected metric

### Formulas

#### SAS (Scalping Alpha Score)
`SAS = (Delta * Gamma) / |Theta|`

Best for: Short-term scalping opportunities

#### RA-SAS (Risk-Adjusted SAS)
`RA-SAS = (Delta * Gamma) / (|Theta| + Spread + Slippage)`

Best for: Real-world trading with execution costs considered

#### TAS (True Alpha Score)
`TAS = (Delta * Gamma) / |Theta| + (RV - IV) * Vega`

Best for: Swing trading positions with volatility edge

#### Expected Return
`Expected Return = RA-SAS + (RV - IV) * Vega`

Best for: Comprehensive analysis and position sizing

### CSV Import

For bulk analysis, prepare a CSV file with columns for:
- Strike
- Delta
- Gamma
- Theta
- Vega
- Bid
- Ask
- IV (Implied Volatility)

Then use the "Import CSV" button to analyze the entire option chain at once.

## License

This software is provided as-is for educational and informational purposes only. Not financial advice.
