@echo off
REM Harper's Evidence Viewer Launcher

set PORT=8777

python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python not found. Please install Python 3.8+ and ensure it's in PATH.
  pause
  exit /b 1
)

echo Starting Evidence Viewer on http://127.0.0.1:%PORT%
set HARPER_VIEWER_PORT=%PORT%
python evidence_viewer.py
pause