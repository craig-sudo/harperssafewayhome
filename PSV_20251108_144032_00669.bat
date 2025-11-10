@echo off
title Harper's Evidence Processing - Bulletproof System
echo.
echo ================================================================
echo         HARPER'S EVIDENCE PROCESSING - BULLETPROOF SYSTEM
echo           Multiple Recovery Methods for Continuous Operation
echo ================================================================
echo.

echo 🎯 Starting bulletproof evidence processing for Harper's case...
echo 📂 This system will NEVER stop processing your evidence
echo.

REM Method 1: Start the progress monitor (most robust)
echo [%time%] Method 1: Starting intelligent progress monitor...
start "Harper OCR Monitor" /MIN py ocr_monitor.py

REM Wait 10 seconds to let monitor start
timeout /t 10 /nobreak >nul

REM Method 2: Backup auto-restart (in case monitor fails)
echo [%time%] Method 2: Starting backup auto-restart system...
start "Harper OCR Backup" /MIN AUTO_RESTART_OCR.bat

echo.
echo ✅ BULLETPROOF SYSTEM ACTIVE!
echo.
echo 🔄 Multiple protection layers running:
echo    • Intelligent progress monitor
echo    • Automatic restart system  
echo    • Process health monitoring
echo    • Stuck detection & recovery
echo.
echo 💪 Your evidence processing is now UNSTOPPABLE!
echo.
echo 📊 To check progress:
echo    • View output folder for CSV results
echo    • Check logs folder for detailed status
echo    • Press Ctrl+C to stop all systems
echo.

:keep_alive
timeout /t 30 /nobreak >nul
echo [%time%] Bulletproof system still active - Harper's evidence being processed...
goto keep_alive