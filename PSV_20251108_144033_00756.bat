@echo off
echo ================================================================
echo               PYTHON DETECTION TEST FOR HARPER'S CASE
echo ================================================================
echo.
echo Testing different ways to run Python...
echo.

echo 1. Trying 'python' command:
python --version 2>nul
if %errorlevel% equ 0 (
    echo    ✅ SUCCESS: 'python' works!
    set WORKING_CMD=python
) else (
    echo    ❌ 'python' not recognized
)

echo.
echo 2. Trying 'py' command:
py --version 2>nul
if %errorlevel% equ 0 (
    echo    ✅ SUCCESS: 'py' works!
    set WORKING_CMD=py
) else (
    echo    ❌ 'py' not recognized
)

echo.
echo 3. Trying 'python3' command:
python3 --version 2>nul
if %errorlevel% equ 0 (
    echo    ✅ SUCCESS: 'python3' works!
    set WORKING_CMD=python3
) else (
    echo    ❌ 'python3' not recognized
)

echo.
echo 4. Checking direct Python 3.14 path:
set "PYTHON314=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%PYTHON314%" (
    "%PYTHON314%" --version 2>nul
    if %errorlevel% equ 0 (
        echo    ✅ SUCCESS: Found Python 3.14 at %PYTHON314%
        set WORKING_CMD="%PYTHON314%"
    )
) else (
    echo    ❌ Python 3.14 not found at expected location
)

echo.
echo ================================================================

if defined WORKING_CMD (
    echo ✅ PYTHON FOUND! Working command: %WORKING_CMD%
    echo.
    echo Now you can run Harper's Evidence Processor!
    echo Just double-click: LAUNCH_HARPER_PROCESSOR.bat
) else (
    echo ❌ NO PYTHON COMMAND WORKS
    echo.
    echo 🔧 SOLUTION:
    echo 1. Open Start Menu and search "python"
    echo 2. If you see Python in results, click it to test
    echo 3. If not found, reinstall Python from python.org
    echo 4. During installation, CHECK "Add Python to PATH"
    echo.
    echo 📞 Alternative: Use the manual OCR methods in CANT_GET_IT_WORKING.md
)

echo.
pause