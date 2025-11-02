@echo off
echo ========================================
echo    Enhanced OCR Processor v3.0
echo    With Advanced Image Preprocessing
echo ========================================
echo.
echo This version includes:
echo - Deskewing (image straightening)
echo - Adaptive thresholding
echo - Confidence-based quality control
echo - Enhanced Tesseract configuration
echo.
pause

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Running Enhanced OCR Processor...
python enhanced_ocr_processor.py

echo.
echo Processing complete!
echo Check the output folder for results
echo Low-confidence extractions will be flagged for review
echo.
pause