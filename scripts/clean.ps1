Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow

# Ensure we are in the root directory
$ScriptPath = $MyInvocation.MyCommand.Path
$RootDir = Split-Path (Split-Path $ScriptPath -Parent) -Parent
Set-Location $RootDir

# Stop and remove containers, networks, and images created by compose
docker-compose down --rmi all --volumes --remove-orphans

Write-Host "Cleanup Complete!" -ForegroundColor Green
