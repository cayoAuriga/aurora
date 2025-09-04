# Build script for Aurora shared libraries

Write-Host "Building Aurora Shared Libraries..." -ForegroundColor Green

# Build base Docker image
Write-Host "Building base Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.base -t aurora/shared:base ..

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Base Docker image built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build base Docker image" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "Installing shared dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Shared dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install shared dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Aurora shared libraries built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  Generate new service: python generate_service.py my-service 8005" -ForegroundColor White
Write-Host "  Build service: docker build -t aurora/my-service ." -ForegroundColor White
Write-Host "  Run service: docker run -p 8005:8005 aurora/my-service" -ForegroundColor White