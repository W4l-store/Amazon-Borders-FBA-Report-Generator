@echo off
echo Installing the Amazon Borders FBA Report Generator from github

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    goto end
)

python clone_project.py

:end
echo.
echo Press any key to exit...
pause >nul
