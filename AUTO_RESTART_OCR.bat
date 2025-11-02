@echo off
title Harper's OCR Processor - Auto-Restart System
echo.
echo ================================================================
echo         HARPER'S OCR PROCESSOR - AUTO RESTART SYSTEM
echo              Ensuring Continuous Evidence Processing
echo ================================================================
echo.

:restart_loop
echo [%time%] Starting/Restarting OCR Processor...
echo.

REM Try to run the OCR processor
py batch_ocr_processor.py

REM If it exits, wait 5 seconds and restart
echo.
echo [%time%] Process ended. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul

goto restart_loop