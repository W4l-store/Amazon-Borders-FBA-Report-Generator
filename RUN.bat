@echo off
echo Welcome to the Amazon Borders FBA Report Generator

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)


python run_app.py

:end
echo.
echo Press any key to exit...
pause >nul