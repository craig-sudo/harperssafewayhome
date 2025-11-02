@echo off
echo ========================================
echo    AI Legal Contradiction Analyzer
echo ========================================
echo.
echo This tool analyzes your OCR evidence against
echo sworn statements to detect perjury and contempt.
echo.
echo IMPORTANT: Ensure GEMINI_API_KEY is set as environment variable
echo.
pause

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Running AI Legal Analyzer...
python ai_legal_analyzer.py

echo.
echo Analysis complete!
echo Check output\AI_CONTRADICTION_REPORT.csv for results
echo.
pause