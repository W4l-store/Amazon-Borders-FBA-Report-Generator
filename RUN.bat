@echo off
echo Welcome to the Amazon Report Generator

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)


python run_server.bat
