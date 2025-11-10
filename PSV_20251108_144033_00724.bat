@echo off
echo ========================================
echo    Secure Evidence Processor
echo    Harper's Custody Case (FDSJ-739-24)
echo ========================================
echo.
echo This tool processes evidence with:
echo - SHA-256 cryptographic integrity verification
echo - Enhanced OCR with quality control
echo - Legal categorization and priority scoring
echo - Court-ready documentation
echo.
echo IMPORTANT: Ensure evidence images are in 'custody_screenshots' folder
echo.
pause

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Starting secure evidence processing...
python evidence_processor.py

echo.
echo Processing complete!
echo Check output folder for results with integrity hashes
echo.
pause