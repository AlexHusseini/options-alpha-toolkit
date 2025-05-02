#!/bin/bash

echo "Starting Options Alpha Toolkit..."

# Make this script executable if it isn't already
if [ ! -x "$0" ]; then
    chmod +x "$0"
    echo "Made script executable"
fi

# Function to find Python
find_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        # Check if python is at least Python 3
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
        if [ "$PYTHON_VERSION" -ge 3 ]; then
            PYTHON_CMD="python"
        else
            echo "Error: Python 3 is required but only Python $PYTHON_VERSION is available."
            return 1
        fi
    else
        echo "Error: Python 3 not found. Please install Python 3.7 or higher."
        echo "Visit https://www.python.org/downloads/"
        return 1
    fi
    return 0
}

# Find Python command
find_python
if [ $? -ne 0 ]; then
    read -p "Press Enter to exit..."
    exit 1
fi
echo "Using Python command: $PYTHON_CMD"

# Check if virtual environment exists and activate it
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    VENV_ACTIVE=1
elif [ -f "env/bin/activate" ]; then
    echo "Activating virtual environment..."
    source env/bin/activate
    VENV_ACTIVE=1
else
    VENV_ACTIVE=0
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if main script exists
if [ ! -f "quant_options_alpha_analyzer.py" ]; then
    echo "Error: quant_options_alpha_analyzer.py not found."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if requirements are installed
echo "Checking requirements..."
$PYTHON_CMD -c "import sys; sys.exit(0 if all(m in sys.modules or __import__(m) for m in ['PyQt5', 'numpy', 'pandas', 'matplotlib', 'scipy']) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    if [ $VENV_ACTIVE -eq 1 ]; then
        pip install -r requirements.txt
    else
        $PYTHON_CMD -m pip install -r requirements.txt
    fi
    
    if [ $? -ne 0 ]; then
        echo "Failed to install required packages."
        echo "Please run: pip install -r requirements.txt"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Run the application
echo "Launching Options Alpha Analyzer..."
$PYTHON_CMD quant_options_alpha_analyzer.py

# Capture exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Application exited with error code: $EXIT_CODE"
fi

# If we activated a virtual environment, deactivate it
if [ $VENV_ACTIVE -eq 1 ]; then
    deactivate 2>/dev/null
fi

echo "Application closed."
read -p "Press Enter to exit..." 