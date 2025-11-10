@echo off
REM Harper's Evidence Processing - Quick Test Harness Launcher
REM Runs system verification tests for all evidence processing tools

echo ===============================================================
echo     HARPER'S EVIDENCE PROCESSING - SYSTEM VERIFICATION
echo ===============================================================
echo.
echo 🔍 Running comprehensive system tests...
echo 💡 This will verify all evidence processing tools work correctly
echo.

REM Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Run the test harness
python quick_test_harness.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ ALL TESTS PASSED! System is ready for evidence processing.
    echo 💡 You can now run MASTER_LAUNCHER.bat to start processing.
) else (
    echo.
    echo ⚠️ Some tests failed. Please review the output above.
    echo 💡 Contact support if you need assistance resolving issues.
)

echo.
echo 📋 Next steps:
echo   - Run MASTER_LAUNCHER.bat for Windows interface
echo   - Run "python master_control_system.py" for Python interface
echo   - Check README.md for detailed usage instructions
echo.
pause