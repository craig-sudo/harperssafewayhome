@echo off
echo.
echo ================================================================
echo          HARPER'S EVIDENCE PROCESSOR - SETUP CHECKER
echo ================================================================
echo.

echo [1/4] Checking Python installation...

REM Try different Python commands
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python found via 'python' command
    set PYTHON_CMD=python
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python found via 'py' command
    set PYTHON_CMD=py
    goto :python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python found via 'python3' command
    set PYTHON_CMD=python3
    goto :python_found
)

REM Check common installation paths
if exist "C:\Python*\python.exe" (
    for /d %%i in ("C:\Python*") do (
        "%%i\python.exe" --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Python found at %%i
            set PYTHON_CMD="%%i\python.exe"
            goto :python_found
        )
    )
)

REM Check AppData paths
if exist "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        "%%i\python.exe" --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo ✅ Python found at %%i
            set PYTHON_CMD="%%i\python.exe"
            goto :python_found
        )
    )
)

REM Check Roaming AppData paths (where Python 3.14 is installed)
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Python\Python*" (
    for /d %%i in ("%APPDATA%\Microsoft\Windows\Start Menu\Programs\Python\Python*") do (
        REM Extract version number and find actual Python installation
        set "PYTHON_VERSION=%%~ni"
        set "PYTHON_VERSION=!PYTHON_VERSION:Python =!"
        
        REM Try common Python installation paths for this version
        if exist "%LOCALAPPDATA%\Programs\Python\Python!PYTHON_VERSION!\python.exe" (
            "%LOCALAPPDATA%\Programs\Python\Python!PYTHON_VERSION!\python.exe" --version >nul 2>&1
            if !errorlevel! equ 0 (
                echo ✅ Python !PYTHON_VERSION! found in LocalAppData
                set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python!PYTHON_VERSION!\python.exe"
                goto :python_found
            )
        )
        
        REM Try system-wide installation
        if exist "C:\Program Files\Python!PYTHON_VERSION!\python.exe" (
            "C:\Program Files\Python!PYTHON_VERSION!\python.exe" --version >nul 2>&1
            if !errorlevel! equ 0 (
                echo ✅ Python !PYTHON_VERSION! found in Program Files
                set PYTHON_CMD="C:\Program Files\Python!PYTHON_VERSION!\python.exe"
                goto :python_found
            )
        )
    )
)

echo ❌ PYTHON NOT RECOGNIZED!
echo.
echo 🔧 QUICK FIXES (try these in order):
echo.
echo 1️⃣ TRY THE 'py' COMMAND:
echo    Open Command Prompt and type: py --version
echo    If this works, restart this script
echo.
echo 2️⃣ ADD PYTHON TO PATH:
echo    - Press Win+R, type: sysdm.cpl
echo    - Click "Environment Variables"
echo    - Under "System Variables" find "Path"
echo    - Click "Edit" and "New"
echo    - Add your Python installation folder
echo    - Restart Command Prompt
echo.
echo 3️⃣ REINSTALL PYTHON:
echo    - Go to: https://python.org/downloads
echo    - Download installer
echo    - CHECK "Add Python to PATH" during install
echo.
pause
exit /b 1

:python_found

echo [2/4] Checking if we're in the right folder...
if not exist "secure_evidence_processor.py" (
    echo ❌ Evidence processor files not found!
    echo Current folder: %CD%
    echo Please run this from the Harper's processor folder
    pause
    exit /b 1
) else (
    echo ✅ Evidence processor files found
)

echo [3/4] Installing required packages...
%PYTHON_CMD% -m pip install pytesseract pillow pandas tqdm openpyxl numpy python-dateutil >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Package installation had issues - trying alternative method
    %PYTHON_CMD% -m pip install --user pytesseract pillow pandas tqdm openpyxl numpy python-dateutil
) else (
    echo ✅ Packages installed successfully
)

echo [4/4] Checking Tesseract OCR...
%PYTHON_CMD% -c "import pytesseract; print('✅ Tesseract ready:', pytesseract.get_tesseract_version())" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Tesseract OCR not found - OCR may not work
    echo.
    echo 🔧 OPTIONAL INSTALL:
    echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo (System will work without it, but with limited OCR capability)
    echo.
)

echo.
echo ================================================================
echo                    🚀 READY TO LAUNCH!
echo ================================================================
echo Default password: password
echo.

%PYTHON_CMD% secure_evidence_processor.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Launch failed. Check the error messages above.
    echo 📋 Common fixes:
    echo - Make sure Python is installed correctly
    echo - Check if all files are in the right folder
    echo - Try running as administrator
)

echo.
pause
