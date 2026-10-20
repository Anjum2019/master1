@echo off
echo ========================================================
echo Starting Enterprise AI Agent Suite for Business Analysis
echo ========================================================
cd /d "%~dp0"

echo Checking and installing required dependencies...
python -m pip install -r requirements.txt

echo.
echo Launching Gradio Web App...
echo Once started, open your browser at: http://127.0.0.1:7860
echo.
python app.py
pause
