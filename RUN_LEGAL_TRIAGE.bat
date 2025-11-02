@echo off
REM Legal Triage Suite - Quick Launcher
REM Generates court-ready exhibits with SHA256 verification

title Harper's Legal Triage ^& Output Suite

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║            ⚖️ LEGAL TRIAGE ^& OUTPUT SUITE ⚖️                   ║
echo ║                                                                  ║
echo ║  📋 Court-Admissible Evidence Package Generator                 ║
echo ║  🔍 SHA256 Integrity Verification                               ║
echo ║  📊 Automated Evidence Categorization ^& Scoring                 ║
echo ║  🏛️ Professional PDF Exhibits                                   ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found
    pause
    exit /b 1
)

:MENU
cls
echo.
echo ══════════════════════════════════════════════════════════════════
echo   LEGAL TRIAGE ^& OUTPUT SUITE - MAIN MENU
echo ══════════════════════════════════════════════════════════════════
echo.
echo   [1] 📊 Full Triage (Generate exhibit index ^& defensibility statement)
echo   [2] 📄 Generate PDF Exhibits (requires reportlab)
echo   [3] 📈 Quick Statistics
echo   [4] 📖 Open Documentation (LEGAL_TRIAGE_GUIDE.md)
echo   [5] 📂 Open Legal Exhibits Folder
echo.
echo   [0] Exit
echo.
echo ══════════════════════════════════════════════════════════════════
set /p choice="Select option: "

if "%choice%"=="1" goto FULL_TRIAGE
if "%choice%"=="2" goto GENERATE_PDFS
if "%choice%"=="3" goto STATS
if "%choice%"=="4" goto DOCS
if "%choice%"=="5" goto OPEN_FOLDER
if "%choice%"=="0" goto EXIT

echo Invalid selection
timeout /t 2 >nul
goto MENU

:FULL_TRIAGE
echo.
echo ════════════════════════════════════════════════════════════════
echo   RUNNING FULL LEGAL TRIAGE
echo ════════════════════════════════════════════════════════════════
echo.
echo 📋 Loading processed CSV files...
echo 🔍 Scanning external data (GeoJSON, email CSVs)...
echo 📊 Categorizing evidence by legal relevance...
echo 🔢 Calculating weighted scores...
echo 🛡️ Performing SHA256 integrity verification...
echo 📝 Generating master exhibit index...
echo 📜 Creating defensibility statement...
echo.
python legal_triage_suite.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Triage failed with error code %errorlevel%
) else (
    echo.
    echo ✅ Full triage completed successfully!
    echo 📂 Output: legal_exhibits\EXHIBIT_INDEX_*.csv
    echo 📜 Statement: legal_exhibits\DEFENSIBILITY_STATEMENT_*.txt
)
echo.
pause
goto MENU

:GENERATE_PDFS
echo.
echo ════════════════════════════════════════════════════════════════
echo   GENERATING PDF EXHIBITS
echo ════════════════════════════════════════════════════════════════
echo.
echo ⚠️ This requires reportlab library
echo 💡 Install with: pip install reportlab
echo.
python legal_triage_suite.py --generate-pdfs
if %errorlevel% neq 0 (
    echo.
    echo ❌ PDF generation failed
    echo 💡 Make sure reportlab is installed: pip install reportlab
) else (
    echo.
    echo ✅ PDF exhibits generated successfully!
    echo 📂 Output: legal_exhibits\EXHIBIT-FDSJ739-*.pdf
)
echo.
pause
goto MENU

:STATS
echo.
echo ════════════════════════════════════════════════════════════════
echo   QUICK STATISTICS
echo ════════════════════════════════════════════════════════════════
echo.
python legal_triage_suite.py --stats
echo.
pause
goto MENU

:DOCS
echo.
echo Opening documentation...
if exist LEGAL_TRIAGE_GUIDE.md (
    start LEGAL_TRIAGE_GUIDE.md
) else (
    echo ❌ Documentation not found: LEGAL_TRIAGE_GUIDE.md
)
echo.
pause
goto MENU

:OPEN_FOLDER
echo.
echo Opening legal exhibits folder...
if exist legal_exhibits (
    start legal_exhibits
) else (
    echo ❌ Folder not found: legal_exhibits\
    echo 💡 Run a triage first to create the folder
)
echo.
pause
goto MENU

:EXIT
echo.
echo Goodbye!
exit /b 0
