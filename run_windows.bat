@echo off
echo Starting Options Alpha Toolkit...

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "env\Scripts\activate.bat" (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
)

:: Check if requirements are installed
echo Checking requirements...
python -c "import PyQt5, numpy, pandas, matplotlib, scipy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install -r requirements.txt
)

:: Run the application
echo Launching Options Alpha Analyzer...
python quant_options_alpha_analyzer.py

:: If we activated a virtual environment, deactivate it
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\deactivate.bat
) else if exist "env\Scripts\activate.bat" (
    call env\Scripts\deactivate.bat
)

pause 