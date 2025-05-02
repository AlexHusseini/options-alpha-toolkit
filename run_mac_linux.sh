#!/bin/bash

echo "Starting Options Alpha Toolkit..."

# Make this script executable if it isn't already
if [ ! -x "$0" ]; then
    chmod +x "$0"
    echo "Made script executable"
fi

# Check if virtual environment exists and activate it
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f "env/bin/activate" ]; then
    echo "Activating virtual environment..."
    source env/bin/activate
fi

# Check if requirements are installed
echo "Checking requirements..."
python3 -c "import PyQt5, numpy, pandas, matplotlib, scipy" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Run the application
echo "Launching Options Alpha Analyzer..."
python3 quant_options_alpha_analyzer.py

# If we activated a virtual environment, deactivate it
if [ -f "venv/bin/activate" ] || [ -f "env/bin/activate" ]; then
    deactivate
fi

echo "Press Enter to exit..."
read 