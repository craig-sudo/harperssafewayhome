@echo off
REM Enhanced OCR Processor - Run with project venv

cd /d "%~dp0"

echo ========================================
echo Enhanced OCR Processor v2.0
echo ========================================
echo.
echo This will re-OCR all screenshots with:
echo - Better text formatting and spacing
echo - Sender/Recipient detection
echo - Cleaner message text
echo.
echo Processing may take 10-30 minutes depending on file count...
echo.
pause

echo.
echo Starting enhanced OCR processing...
echo.

.venv\Scripts\python.exe enhanced_ocr_processor.py

echo.
echo ========================================
echo Processing Complete!
echo ========================================
echo.
echo Check the output/ folder for results.
echo Review the preview file to see samples.
echo Edit sender/recipient columns as needed.
echo.
pause
