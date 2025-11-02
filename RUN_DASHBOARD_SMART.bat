@echo off
setlocal enableextensions

REM Harper's Evidence Processor - Smart Streamlit Dashboard Launcher
REM - Uses project venv if available
REM - Chooses free port (8501 -> 8502)

cd /d "%~dp0"

REM Detect Python in project venv first
set "PYPATH=.venv\Scripts\python.exe"
if not exist "%PYPATH%" (
  set "PYPATH=python"
)

REM Pick a free port (prefer 8501)
set "PORT=8501"
for /f "tokens=*" %%p in ('powershell -NoProfile -Command "(Get-NetTCPConnection -State Listen -LocalPort 8501 -ErrorAction SilentlyContinue) -ne $null"') do set "INUSE=%%p"
if /I "%INUSE%"=="True" (
  set "PORT=8502"
)

echo ========================================
echo Harper's Evidence Processor Dashboard
echo ========================================
echo Using Python: %PYPATH%
echo Launching on: http://localhost:%PORT%
echo.
echo Press Ctrl+C in this window to stop the server.
echo ========================================
echo.

"%PYPATH%" -m streamlit run streamlit_dashboard.py --server.port %PORT% --browser.gatherUsageStats false

pause
