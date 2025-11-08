@echo off
REM Harper's Master Evidence Processing Launcher
REM Complete Windows batch interface for all processing systems
REM Case: FDSJ-739-24

title Harper's Master Evidence Processing System - FDSJ-739-24

REM Set colors for better visibility
color 0F

REM Display header
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║           👑 HARPER'S MASTER PROCESSING LAUNCHER 👑              ║
echo ║                                                                  ║
echo ║  🎯 Complete Windows Interface for Evidence Processing          ║
echo ║  🚀 Professional Legal Documentation System                     ║
echo ║  ⚖️ Case: FDSJ-739-24 ^| One-Click Processing Suite             ║
echo ║                                                                  ║
echo ║  📅 System Launched: %date% %time%                              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ from https://python.org
    echo 📋 Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "master_control_system.py" (
    echo ❌ ERROR: Script files not found in current directory
    echo 📂 Current directory: %cd%
    echo 💡 Please navigate to the Harper's evidence processing directory
    pause
    exit /b 1
)

:MAIN_MENU
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                     🎛️ MASTER CONTROL PANEL                     ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 🤖 AUTOMATIC PROCESSING:
echo   [1] 🧠 Intelligent Processing Manager (AI-Powered Auto-Selection)
echo.
echo 🔄 MANUAL PROCESSING:
echo   [2] 🔍 Enhanced Quality Processor (Advanced OCR + Quality Control)
echo   [3] 🔐 Secure Evidence Processor (Password Protected + Exporter)echo   [3] 🔐 Secure Evidence Processor (Password Protected + Export)
echo   [4] 📄 Advanced Evidence Processor (Multi-Format: PDF/Video/Audio)
echo   [5] ⚡ Batch OCR Processor (Fast Large Volume Processing)
echo.
echo 👀 MONITORING ^& CONTROL:
echo   [6] 👁️ OCR Monitor (Auto-Restart ^& Progress Tracking)
echo   [7] 📊 Ultimate Progress Monitor (Real-Time Statistics)
echo.
🔧 SYSTEM MAINTENANCE:
echo   [8] 🛠️ Automated Maintenance System (Cleanup ^& Optimization)
echo   [9] 🧹 Manual System Cleanup
echo   [X] 🗑️ Duplicate File Manager (Find ^& Delete Duplicates)
echo.
echo 🛡️ EVIDENCE VALIDATION:
echo   [Z] 🔍 Evidence Integrity Checker (File Validation ^& Verification)
echo   [Y] 📦 Court Package Exporter (Professional Evidence Packages)
echo   [W] ⚖️ Legal Triage ^& Output Suite (Court-Admissible Exhibits)
echo.
echo 🚀 ADVANCED AUTOMATION:
echo   [B] 🤖 Automated Batch Engine (Intelligent Processing Automation)
echo   [P] 📊 Performance Monitor (Real-Time System Analytics)
echo.
echo 📊 REPORTS ^& ANALYSIS:
echo   [R] ⚖️ Court Report Generator (Professional Legal Reports)
echo   [T] 📅 Evidence Timeline Generator (Chronological Analysis)
echo.
echo 🚀 QUICK ACTIONS:
echo   [A] ⚡ Auto-Process Everything (Smart Selection + Processing)
echo   [K] 🔍 Check System Status
echo   [C] 📄 View Recent Results
echo   [D] 🧪 Run Full System Test
echo.
echo 🎮 ADVANCED OPTIONS:
echo   [M] 🎛️ Python Master Control Interface (Interactive Mode)
echo   [S] ⚙️ System Configuration
echo   [L] 📋 View System Logs
echo.
echo   [0] 🚪 Exit
echo.
echo ══════════════════════════════════════════════════════════════════
set /p choice="🎯 Select option: "

REM Process user choice
if "%choice%"=="1" goto INTELLIGENT_PROCESSING
if "%choice%"=="2" goto ENHANCED_QUALITY
if "%choice%"=="3" goto SECURE_EVIDENCE
if "%choice%"=="4" goto ADVANCED_EVIDENCE
if "%choice%"=="5" goto BATCH_OCR
if "%choice%"=="6" goto OCR_MONITOR
if "%choice%"=="7" goto PROGRESS_MONITOR
if "%choice%"=="8" goto MAINTENANCE
if "%choice%"=="9" goto MANUAL_CLEANUP
if /i "%choice%"=="X" goto DUPLICATE_MANAGER
if /i "%choice%"=="Z" goto INTEGRITY_CHECKER
if /i "%choice%"=="Y" goto COURT_EXPORTER
if /i "%choice%"=="W" goto LEGAL_TRIAGE
if /i "%choice%"=="B" goto BATCH_ENGINE
if /i "%choice%"=="P" goto PERFORMANCE_MONITOR
if /i "%choice%"=="R" goto COURT_REPORT
if /i "%choice%"=="T" goto TIMELINE
if /i "%choice%"=="A" goto AUTO_PROCESS
if /i "%choice%"=="K" goto SYSTEM_STATUS
if /i "%choice%"=="C" goto RECENT_RESULTS
if /i "%choice%"=="D" goto SYSTEM_TEST
if /i "%choice%"=="M" goto MASTER_CONTROL
if /i "%choice%"=="S" goto SYSTEM_CONFIG
if /i "%choice%"=="L" goto VIEW_LOGS
if "%choice%"=="0" goto EXIT

echo ❌ Invalid selection. Please try again.
timeout /t 2 >nul
goto MAIN_MENU

:INTELLIGENT_PROCESSING
echo.
echo 🧠 LAUNCHING INTELLIGENT PROCESSING MANAGER...
echo ════════════════════════════════════════════
echo 🎯 AI-powered system will analyze your evidence and select optimal processing
echo 📊 Automatic quality assessment and smart categorization
echo.
python intelligent_processing_manager.py
if %errorlevel% neq 0 (
    echo ❌ Processing failed with error code %errorlevel%
) else (
    echo ✅ Intelligent processing completed successfully!
)
pause
goto MAIN_MENU

:ENHANCED_QUALITY
echo.
echo 🔍 LAUNCHING ENHANCED QUALITY PROCESSOR...
echo ══════════════════════════════════════════
echo 💎 Advanced OCR with quality control and confidence scoring
echo 🎯 Smart categorization and duplicate detection
echo.
python enhanced_quality_processor.py
if %errorlevel% neq 0 (
    echo ❌ Processing failed with error code %errorlevel%
) else (
    echo ✅ Enhanced quality processing completed successfully!
)
pause
goto MAIN_MENU

:SECURE_EVIDENCE
echo.
echo 🔐 LAUNCHING SECURE EVIDENCE PROCESSOR...
echo ════════════════════════════════════════
echo 🛡️ Password-protected evidence processing
echo 📤 Google Sheets export and PDF report generation
echo.
python secure_evidence_processor.py
if %errorlevel% neq 0 (
    echo ❌ Processing failed with error code %errorlevel%
) else (
    echo ✅ Secure evidence processing completed successfully!
)
pause
goto MAIN_MENU

:ADVANCED_EVIDENCE
echo.
echo 📄 LAUNCHING ADVANCED EVIDENCE PROCESSOR...
echo ═══════════════════════════════════════════
echo 🎬 Multi-format support: PDFs, Videos, Audio, Documents
echo 🔊 Speech recognition and multimedia analysis
echo.
python advanced_evidence_processor.py
if %errorlevel% neq 0 (
    echo ❌ Processing failed with error code %errorlevel%
) else (
    echo ✅ Advanced evidence processing completed successfully!
)
pause
goto MAIN_MENU

:BATCH_OCR
echo.
echo ⚡ LAUNCHING BATCH OCR PROCESSOR...
echo ═════════════════════════════════════
echo 🚀 High-speed processing for large image collections
echo 📊 Progress tracking and batch optimization
echo.
python batch_ocr_processor.py
if %errorlevel% neq 0 (
    echo ❌ Processing failed with error code %errorlevel%
) else (
    echo ✅ Batch OCR processing completed successfully!
)
pause
goto MAIN_MENU

:OCR_MONITOR
echo.
echo 👁️ LAUNCHING OCR MONITOR...
echo ═════════════════════════════
echo 🔄 Continuous monitoring and auto-restart functionality
echo 📈 Real-time progress tracking and error recovery
echo.
python ocr_monitor.py
if %errorlevel% neq 0 (
    echo ❌ Monitor failed with error code %errorlevel%
) else (
    echo ✅ OCR monitoring completed successfully!
)
pause
goto MAIN_MENU

:PROGRESS_MONITOR
echo.
echo 📊 LAUNCHING ULTIMATE PROGRESS MONITOR...
echo ════════════════════════════════════════
echo 📈 Real-time statistics and performance metrics
echo 🎯 Advanced progress visualization
echo.
python ultimate_progress_monitor.py
if %errorlevel% neq 0 (
    echo ❌ Progress monitor failed with error code %errorlevel%
) else (
    echo ✅ Progress monitoring completed successfully!
)
pause
goto MAIN_MENU

:MAINTENANCE
echo.
echo 🛠️ LAUNCHING AUTOMATED MAINTENANCE SYSTEM...
echo ═══════════════════════════════════════════
echo 🧹 System cleanup and optimization
echo 📊 Performance monitoring and integrity checks
echo.
python automated_maintenance_system.py
if %errorlevel% neq 0 (
    echo ❌ Maintenance failed with error code %errorlevel%
) else (
    echo ✅ System maintenance completed successfully!
)
pause
goto MAIN_MENU

:MANUAL_CLEANUP
echo.
echo 🧹 MANUAL SYSTEM CLEANUP
echo ══════════════════════
echo.
echo Cleaning up temporary files...
if exist temp rd /s /q temp 2>nul
mkdir temp 2>nul

echo Organizing log files...
if not exist logs mkdir logs
for %%f in (*.log) do move "%%f" logs\ 2>nul

echo Cleaning up old backup files...
if exist secure_backups (
    cd secure_backups
    for /f "skip=10 delims=" %%f in ('dir /b /o-d *.csv 2^>nul') do del "%%f" 2>nul
    cd ..
)

echo ✅ Manual cleanup completed!
pause
goto MAIN_MENU

:DUPLICATE_MANAGER
echo.
echo 🗑️ LAUNCHING DUPLICATE FILE MANAGER...
echo ═══════════════════════════════════════
echo 🔍 Advanced duplicate detection and safe removal
echo 🛡️ Backup protection and verification system
echo ⚠️ IMPORTANT: All duplicates are backed up before deletion
echo.
python duplicate_file_manager.py
if %errorlevel% neq 0 (
    echo ❌ Duplicate management failed with error code %errorlevel%
) else (
    echo ✅ Duplicate file management completed successfully!
)
pause
goto MAIN_MENU

:INTEGRITY_CHECKER
echo.
echo 🛡️ LAUNCHING EVIDENCE INTEGRITY CHECKER...
echo ═══════════════════════════════════════════════
echo 🔍 Comprehensive file validation and verification
echo ⚖️ Legal compliance and chain of custody checking
echo 🚨 Automatic quarantine of suspicious files
echo.
python evidence_integrity_checker.py
if %errorlevel% neq 0 (
    echo ❌ Integrity checking failed with error code %errorlevel%
) else (
    echo ✅ Evidence integrity verification completed successfully!
)
pause
goto MAIN_MENU

:COURT_EXPORTER
echo.
echo ⚖️ LAUNCHING COURT PACKAGE EXPORTER...
echo ═══════════════════════════════════════════
echo 📦 Professional evidence package creation
echo 🏛️ Court-ready documentation and formatting
echo 🛡️ Chain of custody and integrity verification
echo.
python court_package_exporter.py
if %errorlevel% neq 0 (
    echo ❌ Court package export failed with error code %errorlevel%
) else (
    echo ✅ Court package creation completed successfully!
)
pause
goto MAIN_MENU

:LEGAL_TRIAGE
echo.
echo ⚖️ LAUNCHING LEGAL TRIAGE ^& OUTPUT SUITE...
echo ═════════════════════════════════════════════════
echo 📋 Court-admissible evidence package preparation
echo 🔍 SHA256 integrity verification and exhibit generation
echo 📊 Evidence categorization and weighted scoring
echo 🏛️ Professional PDF exhibits with defensibility statements
echo.
echo OPTIONS:
echo   [1] Full Triage (Generate exhibit index ^& statement)
echo   [2] Generate PDF Exhibits (requires reportlab)
echo   [3] Quick Statistics
echo   [0] Return to main menu
echo.
set /p triage_choice="Select option: "

if "%triage_choice%"=="1" (
    echo.
    echo Running full legal triage...
    python legal_triage_suite.py
) else if "%triage_choice%"=="2" (
    echo.
    echo Generating PDF exhibits...
    python legal_triage_suite.py --generate-pdfs
) else if "%triage_choice%"=="3" (
    echo.
    echo Showing statistics...
    python legal_triage_suite.py --stats
) else if "%triage_choice%"=="0" (
    goto MAIN_MENU
) else (
    echo Invalid selection
)

if %errorlevel% neq 0 (
    echo ❌ Legal triage failed with error code %errorlevel%
) else (
    echo ✅ Legal triage completed successfully!
    echo 📂 Output location: legal_exhibits\
)
pause
goto MAIN_MENU

:BATCH_ENGINE
echo.
echo 🤖 LAUNCHING AUTOMATED BATCH ENGINE...
echo ═══════════════════════════════════════════
echo 🚀 Intelligent evidence processing automation
echo ⚡ Multi-threaded high-performance processing
echo 📊 Real-time performance monitoring and optimization
echo.
python automated_batch_engine.py
if %errorlevel% neq 0 (
    echo ❌ Automated batch processing failed with error code %errorlevel%
) else (
    echo ✅ Automated batch processing completed successfully!
)
pause
goto MAIN_MENU

:PERFORMANCE_MONITOR
echo.
echo 📊 LAUNCHING PERFORMANCE MONITORING DASHBOARD...
echo ═══════════════════════════════════════════════════
echo 📈 Real-time system performance analytics
echo 🚨 Intelligent alert system and optimization
echo ⚡ Advanced metrics and performance intelligence
echo.
python performance_monitor.py
if %errorlevel% neq 0 (
    echo ❌ Performance monitoring failed with error code %errorlevel%
) else (
    echo ✅ Performance monitoring session completed successfully!
)
pause
goto MAIN_MENU

:COURT_REPORT
if not exist court_report_generator.py (
    echo ❌ Court Report Generator not found
    echo 💡 This feature may not be available in your installation
    pause
    goto MAIN_MENU
)
echo.
echo ⚖️ LAUNCHING COURT REPORT GENERATOR...
echo ════════════════════════════════════
echo 📋 Professional legal report generation
echo 📊 Evidence analysis and court-ready formatting
echo.
python court_report_generator.py
if %errorlevel% neq 0 (
    echo ❌ Report generation failed with error code %errorlevel%
) else (
    echo ✅ Court report generated successfully!
)
pause
goto MAIN_MENU

:TIMELINE
if not exist evidence_timeline_generator.py (
    echo ❌ Timeline Generator not found
    echo 💡 This feature may not be available in your installation
    pause
    goto MAIN_MENU
)
echo.
echo 📅 LAUNCHING EVIDENCE TIMELINE GENERATOR...
echo ══════════════════════════════════════════
echo 📊 Chronological evidence analysis
echo 🎯 Timeline visualization for court presentation
echo.
python evidence_timeline_generator.py
if %errorlevel% neq 0 (
    echo ❌ Timeline generation failed with error code %errorlevel%
) else (
    echo ✅ Evidence timeline generated successfully!
)
pause
goto MAIN_MENU

:AUTO_PROCESS
echo.
echo ⚡ AUTO-PROCESS EVERYTHING
echo ═══════════════════════
echo 🤖 Running complete automated processing pipeline...
echo.
echo Step 1: System status check...
python -c "import os; print('✅ Python environment OK')"

echo Step 2: Intelligent processing selection...
python intelligent_processing_manager.py

echo Step 3: System maintenance...
python automated_maintenance_system.py

echo.
echo 🎉 Auto-processing pipeline completed!
pause
goto MAIN_MENU

:SYSTEM_STATUS
echo.
echo 🔍 SYSTEM STATUS CHECK
echo ═════════════════════
echo.
echo 🐍 Python Version:
python --version

echo.
echo 📂 Directory Structure:
if exist custody_screenshots_smart_renamed (
    echo ✅ Evidence directory found
) else (
    echo ❌ Evidence directory missing
)

if exist output (
    echo ✅ Output directory found
    for /f %%i in ('dir /b output\*.csv 2^>nul ^| find /c /v ""') do echo    📄 %%i CSV files
) else (
    echo ❌ Output directory missing
)

if exist logs (
    echo ✅ Logs directory found
    for /f %%i in ('dir /b logs\*.log 2^>nul ^| find /c /v ""') do echo    📋 %%i log files
) else (
    echo ❌ Logs directory missing
)

echo.
echo 🔧 System Scripts:
for %%f in (*.py) do (
    echo ✅ %%f
)

echo.
echo 💾 Disk Space:
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do echo Available: %%a bytes

pause
goto MAIN_MENU

:RECENT_RESULTS
echo.
echo 📄 RECENT PROCESSING RESULTS
echo ═══════════════════════════
echo.
if exist output (
    cd output
    echo Most recent CSV files:
    for /f "delims=" %%f in ('dir /b /o-d *.csv 2^>nul') do (
        echo 📊 %%f
        for %%a in ("%%f") do echo    📅 %%~ta  💾 %%~za bytes
        echo.
    )
    cd ..
) else (
    echo ❌ No output directory found
)
pause
goto MAIN_MENU

:SYSTEM_TEST
echo.
echo 🧪 RUNNING FULL SYSTEM TEST
echo ══════════════════════════
echo.
echo Testing Python environment...
python -c "print('✅ Python OK')"

echo Testing required modules...
python -c "import pytesseract; print('✅ pytesseract OK')" 2>nul || echo "❌ pytesseract missing"
python -c "from PIL import Image; print('✅ PIL OK')" 2>nul || echo "❌ PIL missing"
python -c "import pandas; print('✅ pandas OK')" 2>nul || echo "❌ pandas missing"

echo Testing Tesseract OCR...
python -c "import pytesseract; pytesseract.get_tesseract_version(); print('✅ Tesseract OK')" 2>nul || echo "❌ Tesseract not configured"

echo Testing file structure...
if exist custody_screenshots_smart_renamed echo ✅ Evidence directory OK
if exist output echo ✅ Output directory OK
if exist logs echo ✅ Logs directory OK

echo.
echo 🎯 System test completed!
pause
goto MAIN_MENU

:MASTER_CONTROL
echo.
echo 🎛️ LAUNCHING PYTHON MASTER CONTROL INTERFACE...
echo ═════════════════════════════════════════════
echo 🖥️ Advanced interactive control panel
echo 🎮 Full system management capabilities
echo.
python master_control_system.py
pause
goto MAIN_MENU

:SYSTEM_CONFIG
echo.
echo ⚙️ SYSTEM CONFIGURATION
echo ═════════════════════
echo.
echo Current configuration:
echo 📂 Working Directory: %cd%
echo 🐍 Python: 
python --version
echo 📋 Environment Variables:
echo    PATH (Python): %PATH% | findstr python
echo.
echo Configuration files:
if exist config\settings.py (
    echo ✅ config\settings.py found
) else (
    echo ❌ config\settings.py missing
)
echo.
pause
goto MAIN_MENU

:VIEW_LOGS
echo.
echo 📋 VIEWING SYSTEM LOGS
echo ═════════════════════
echo.
if exist logs (
    cd logs
    echo Recent log files:
    dir /b /o-d *.log
    echo.
    set /p logfile="Enter log filename to view (or press Enter to skip): "
    if defined logfile (
        if exist "%logfile%" (
            echo.
            echo Contents of %logfile%:
            echo ═══════════════════════════════════
            type "%logfile%" | more
        ) else (
            echo ❌ Log file not found
        )
    )
    cd ..
) else (
    echo ❌ No logs directory found
)
pause
goto MAIN_MENU

:EXIT
echo.
echo 👋 Thank you for using Harper's Master Processing System
echo ⚖️ Case FDSJ-739-24 - Evidence Processing Complete
echo.
echo 💡 Remember to:
echo    📄 Check the 'output' directory for results
echo    📋 Review logs for any issues
echo    🔒 Secure your processed evidence files
echo.
echo 🎯 System shutdown: %date% %time%
echo.
timeout /t 3 >nul
exit /b 0