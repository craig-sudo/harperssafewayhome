@echo off
echo.
echo ================================================================
echo              HARPER'S EVIDENCE ORGANIZER LAUNCHER
echo                    Automatic Screenshot Organization
echo ================================================================
echo.

echo [1/2] Checking Python and launching organizer...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found, launching Evidence Organizer...
echo.
echo 🎯 This will organize all your screenshots automatically:
echo    • Smart categorization (Emma, Jane, Dec 9th, etc.)
echo    • Systematic renaming (EMMA_2023-12-09_001.png)
echo    • Organized folder structure for legal review
echo    • OCR-based content analysis for sorting
echo.

REM Install required packages silently
py -m pip install --quiet pillow pytesseract pathlib

echo 📁 Organizing Harper's evidence for FDSJ-739-24...
echo.

py evidence_organizer.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Organization failed. Common fixes:
    echo - Make sure images are in 'custody_screenshots' folder
    echo - Check that Python packages are installed
    echo - Ensure you have write permissions
)

echo.
echo ================================================================
echo                    ORGANIZATION COMPLETE
echo ================================================================
pause