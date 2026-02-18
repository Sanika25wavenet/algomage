# Intelligent Event Photo Retrieval System - Dev Launcher
# Usage: .\dev.ps1

Write-Host "🚀 Starting Intelligent Event Photo Retrieval System..." -ForegroundColor Cyan

# 1. Start Infrastructure (Redis)
Write-Host "📦 Starting Redis via Docker Compose..." -ForegroundColor DarkCyan
docker-compose up -d

# 2. Check if venv exists and is ready
if (-not (Test-Path "server\.venv")) {
    Write-Host "❌ Server virtual environment not found. Please run 'cd server; python -m venv .venv; pip install .' first." -ForegroundColor Red
    exit
}

# 3. Start Services in separate windows for easier log viewing
# Alternatively, we could use concurrently if npm is preferred.

Write-Host "📡 Launching Backend API (http://localhost:8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server; .\.venv\Scripts\python -m uvicorn main:app --reload"

Write-Host "⚙️ Launching Celery Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server; .\.venv\Scripts\python -m celery -A config.celery_app worker --loglevel=info --pool=solo"

Write-Host "🎨 Launching Frontend (http://localhost:3000)..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd client; npm run dev"

Write-Host "`n✅ All services are starting up!" -ForegroundColor Green
Write-Host "You can close this window now. Services will keep running in their own terminals." -ForegroundColor Cyan
