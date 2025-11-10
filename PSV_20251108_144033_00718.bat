@echo off
SET "PYTHON_EXE=python"

rem Check if Python is in PATH
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found in PATH. Please ensure Python 3.7+ is installed and added to your system's PATH.
    echo You can download it from https://python.org/downloads/
    pause
    exit /b 1
)

echo Running the Automated Filing Bot...
%PYTHON_EXE% auto_filing_bot.py

if %errorlevel% neq 0 (
    echo.
    echo An error occurred during the Auto-Filing Bot execution.
    echo Please review the output above for details.
    pause
)

pause
