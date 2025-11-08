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

echo Launching the Master Control System...
%PYTHON_EXE% master_control_system.py

if %errorlevel% neq 0 (
    echo.
    echo An error occurred while launching the Master Control System.
    echo Please review the output above for details.
    pause
)

pause
