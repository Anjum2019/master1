Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Enterprise AI Agent Suite for Business Analysis" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

Write-Host "Checking required dependencies..." -ForegroundColor Yellow
& python -m pip install -r requirements.txt

Write-Host "`nLaunching Gradio Web App..." -ForegroundColor Green
Write-Host "Open your browser at: http://127.0.0.1:7860`n" -ForegroundColor Green
& python app.py
