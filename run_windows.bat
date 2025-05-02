@echo off
echo Starting Options Alpha Toolkit...

:: Change to the script's directory
echo Setting up environment...
cd /d "%~dp0"
echo Working directory: %CD%

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python 3.7 or higher.
    echo Visit https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
)

:: Create requirements.txt if it doesn't exist
if not exist "requirements.txt" (
    echo Requirements.txt not found, creating it...
    (
        echo PyQt5^>=5.15.0
        echo numpy^>=1.19.0
        echo pandas^>=1.1.0
        echo matplotlib^>=3.3.0
        echo scipy^>=1.5.0
    ) > requirements.txt
    echo Created requirements.txt
)

:: Check if main script exists
if not exist "quant_options_alpha_analyzer.py" (
    echo Error: quant_options_alpha_analyzer.py not found.
    echo Current directory: %CD%
    echo Files in directory:
    dir
    pause
    exit /b 1
)

:: Check if requirements are installed
echo Checking requirements...
python -c "import sys; sys.exit(0 if all(m in sys.modules or __import__(m) for m in ['PyQt5', 'numpy', 'pandas', 'matplotlib', 'scipy']) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install required packages. Please run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

:: Run the application
echo Launching Options Alpha Analyzer...
python quant_options_alpha_analyzer.py
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with an error.
)

:: If we activated a virtual environment, deactivate it
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\deactivate.bat
) else if exist "env\Scripts\activate.bat" (
    call env\Scripts\deactivate.bat
)

echo.
echo Application closed.
pause 