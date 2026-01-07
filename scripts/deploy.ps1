Write-Host "Deploying Movie Recommendation System in Docker..." -ForegroundColor Cyan

# Ensure we are in the root directory
$ScriptPath = $MyInvocation.MyCommand.Path
$RootDir = Split-Path (Split-Path $ScriptPath -Parent) -Parent
Set-Location $RootDir

# Start the stack in detached mode
docker-compose up -d

Write-Host "Deployment Started!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000"
Write-Host "Frontend UI: http://localhost:80"
Write-Host "Run 'docker-compose logs -f' to see real-time logs."
