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

:: Check Python version
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
python -c "import sys; sys.exit(0 if sys.version_info.major >= 3 and sys.version_info.minor >= 7 else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Warning: This application requires Python 3.7 or higher.
    echo Current Python version may not be compatible.
    echo Press any key to continue anyway or Ctrl+C to exit...
    pause >nul
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
    echo.
    
    :: Try different installation methods
    echo Attempt 1: Using pip install...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo First attempt failed. Trying alternate methods...
        echo.
        
        echo Attempt 2: Using python -m pip install...
        python -m pip install -r requirements.txt
        if %ERRORLEVEL% NEQ 0 (
            echo Second attempt failed. Trying with --user flag...
            echo.
            
            echo Attempt 3: Using pip install with --user flag...
            pip install --user -r requirements.txt
            if %ERRORLEVEL% NEQ 0 (
                echo All installation attempts failed.
                echo.
                echo TROUBLESHOOTING TIPS:
                echo 1. Try running this script as Administrator
                echo 2. Check your internet connection
                echo 3. Manually install packages with: pip install PyQt5 numpy pandas matplotlib scipy
                echo 4. If you have multiple Python versions, try specifying fully qualified path, e.g.:
                echo    C:\Python39\python.exe -m pip install -r requirements.txt
                echo.
                echo Press any key to attempt running without installing packages...
                pause >nul
            )
        )
    )
)

:: Run the application
echo Launching Options Alpha Analyzer...
python quant_options_alpha_analyzer.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with an error.
    echo If you see an import error, you need to install the required packages.
    echo Try running: pip install PyQt5 numpy pandas matplotlib scipy
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