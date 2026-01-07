Write-Host "Building Docker images for Movie Recommendation System..." -ForegroundColor Cyan

# Ensure we are in the root directory
$ScriptPath = $MyInvocation.MyCommand.Path
$RootDir = Split-Path (Split-Path $ScriptPath -Parent) -Parent
Set-Location $RootDir

# Build with Compose
docker-compose build --no-cache

Write-Host "Build Complete!" -ForegroundColor Green
