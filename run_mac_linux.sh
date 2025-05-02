#!/bin/bash

echo "Starting Options Alpha Toolkit..."

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "Script directory: $SCRIPT_DIR"

# Change to the script directory to ensure all relative paths work correctly
cd "$SCRIPT_DIR"
echo "Working directory: $(pwd)"

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

# Check Python version
$PYTHON_CMD -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
$PYTHON_CMD -c "import sys; sys.exit(0 if sys.version_info.major >= 3 and sys.version_info.minor >= 7 else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: This application requires Python 3.7 or higher."
    echo "Current Python version may not be compatible."
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

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

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Requirements.txt not found, creating it..."
    cat > requirements.txt << EOF
PyQt5>=5.15.0
numpy>=1.19.0
pandas>=1.1.0
matplotlib>=3.3.0
scipy>=1.5.0
EOF
    echo "Created requirements.txt"
fi

# Check if main script exists
if [ ! -f "quant_options_alpha_analyzer.py" ]; then
    echo "Error: quant_options_alpha_analyzer.py not found."
    echo "Current directory: $(pwd)"
    echo "Files in directory:"
    ls -la
    read -p "Press Enter to exit..."
    exit 1
fi

# Function to try installing packages with different methods
try_install_packages() {
    echo "Installing required packages..."
    echo ""
    
    # Attempt 1: Use pip directly
    echo "Attempt 1: Using pip install..."
    if [ $VENV_ACTIVE -eq 1 ]; then
        pip install -r requirements.txt
    else
        $PYTHON_CMD -m pip install -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        return 0
    fi
    
    echo "First attempt failed. Trying alternate methods..."
    echo ""
    
    # Attempt 2: Use pip with --user flag
    echo "Attempt 2: Using pip install with --user flag..."
    if [ $VENV_ACTIVE -eq 1 ]; then
        pip install --user -r requirements.txt
    else
        $PYTHON_CMD -m pip install --user -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        return 0
    fi
    
    # Attempt 3: Try using sudo if available
    echo "Second attempt failed. Trying with sudo if available..."
    echo ""
    
    if command -v sudo &>/dev/null; then
        echo "Attempt 3: Using sudo pip install..."
        echo "You may be prompted for your password."
        sudo $PYTHON_CMD -m pip install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            return 0
        fi
    else
        echo "Sudo not available, skipping third attempt."
    fi
    
    echo "All installation attempts failed."
    echo ""
    echo "TROUBLESHOOTING TIPS:"
    echo "1. Check your internet connection"
    echo "2. Try manually installing packages with: $PYTHON_CMD -m pip install PyQt5 numpy pandas matplotlib scipy"
    echo "3. If you have multiple Python versions, ensure you're using the right one"
    echo "4. On some systems, you may need to install system packages first, e.g.:"
    echo "   - Ubuntu/Debian: sudo apt-get install python3-pyqt5 python3-numpy python3-matplotlib"
    echo "   - macOS: brew install pyqt numpy matplotlib"
    echo ""
    read -p "Press Enter to attempt running without installing packages..."
    return 1
}

# Check if requirements are installed
echo "Checking requirements..."
$PYTHON_CMD -c "import sys; sys.exit(0 if all(m in sys.modules or __import__(m) for m in ['PyQt5', 'numpy', 'pandas', 'matplotlib', 'scipy']) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    try_install_packages
fi

# Run the application
echo "Launching Options Alpha Analyzer..."
$PYTHON_CMD quant_options_alpha_analyzer.py

# Capture exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "Application exited with error code: $EXIT_CODE"
    echo "If you see an import error, you need to install the required packages."
    echo "Try running: $PYTHON_CMD -m pip install PyQt5 numpy pandas matplotlib scipy"
fi

# If we activated a virtual environment, deactivate it
if [ $VENV_ACTIVE -eq 1 ]; then
    deactivate 2>/dev/null
fi

echo "Application closed."
read -p "Press Enter to exit..." 