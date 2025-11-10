@echo off
title Harper's SUPER LAUNCHER - All Evidence Types Processing
echo.
echo ================================================================
echo       HARPER'S SUPER EVIDENCE PROCESSOR - EVERYTHING MODE
echo         Images, PDFs, Videos, Audio, Documents - ALL OF IT!
echo ================================================================
echo.

echo 🚀 Installing advanced processing packages...
echo.

REM Install video/audio processing packages
py -m pip install moviepy SpeechRecognition psutil

echo.
echo ================================================================
echo                    🎯 LAUNCHING SUPER MODE!
echo ================================================================
echo.

echo 🔥 Starting DUAL PROCESSING MODE:
echo    • Main OCR: Processing images (already running)
echo    • Advanced: Processing PDFs, videos, docs, audio
echo.

REM Start the advanced processor alongside the main one
start "Harper Advanced Processor" /MIN py advanced_evidence_processor.py

echo.
echo ✅ SUPER MODE ACTIVATED!
echo.
echo 📊 Your system is now processing:
echo    • 🖼️  Images (OCR text extraction)
echo    • 📄 PDFs (document text extraction)  
echo    • 🎥 Videos (audio transcription)
echo    • 🔊 Audio files (speech-to-text)
echo    • 📝 Word documents (content extraction)
echo    • 📋 Text files (direct processing)
echo.
echo 💪 HARPER'S EVIDENCE IS GETTING THE FULL TREATMENT!
echo.

pause