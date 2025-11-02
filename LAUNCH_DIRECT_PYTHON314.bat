@echo off
setlocal enabledelayedexpansion

echo ================================================================
echo          HARPER'S EVIDENCE PROCESSOR - DIRECT LAUNCH
echo                    For Python 3.14 Installation
echo ================================================================
echo.

REM Use the Python launcher which we know works
set "PYTHON_CMD=py"

echo [1/3] Testing your Python 3.14 installation...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Found Python via 'py' command:
    py --version
) else (
    echo ❌ Python launcher not working
    echo.
    echo 🔍 Searching for Python 3.14 in other locations...
    
    REM Try alternative paths
    set "ALT_PATH1=%APPDATA%\Local\Programs\Python\Python314\python.exe"
    set "ALT_PATH2=C:\Program Files\Python314\python.exe"
    set "ALT_PATH3=C:\Python314\python.exe"
    
    if exist "!ALT_PATH1!" (
        set "PYTHON_PATH=!ALT_PATH1!"
        echo ✅ Found at: !ALT_PATH1!
    ) else if exist "!ALT_PATH2!" (
        set "PYTHON_PATH=!ALT_PATH2!"
        echo ✅ Found at: !ALT_PATH2!
    ) else if exist "!ALT_PATH3!" (
        set "PYTHON_PATH=!ALT_PATH3!"
        echo ✅ Found at: !ALT_PATH3!
    ) else (
        echo ❌ Could not locate Python 3.14 installation
        echo.
        echo 🔧 Manual check needed:
        echo 1. Open File Explorer
        echo 2. Navigate to: %LOCALAPPDATA%\Programs\Python\
        echo 3. Look for a Python314 or similar folder
        echo 4. Let me know the exact path
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Installing required packages...
py -m pip install --user pytesseract pillow pandas tqdm openpyxl numpy python-dateutil
if %errorlevel% neq 0 (
    echo ⚠️  Package installation had issues, but continuing...
) else (
    echo ✅ Packages installed successfully
)

echo.
echo [3/3] Launching Harper's Evidence Processor...
echo.
echo ================================================================
echo                    🚀 STARTING EVIDENCE PROCESSOR
echo ================================================================
echo Password: password
echo.

REM Check if processor file exists
if not exist "secure_evidence_processor.py" (
    echo ❌ Evidence processor file not found!
    echo Make sure you're running this from the Harper's processor folder
    pause
    exit /b 1
)

py secure_evidence_processor.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Launch failed
    echo 📋 This usually means missing dependencies
    echo Try running this again or check the error message above
)

echo.
echo ================================================================
echo                    SESSION COMPLETE
echo ================================================================
pause