@echo off
REM Harper's Evidence Processor - Streamlit Dashboard Launcher
REM Beautiful web-based interface

echo ========================================
echo Harper's Evidence Processor Dashboard
echo ========================================
echo.
echo Starting web interface...
echo.
echo Once started, the dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m streamlit run streamlit_dashboard.py

pause
