# TiDB Cluster Setup Script
Write-Host "Starting TiDB cluster..." -ForegroundColor Green

# Start the TiDB cluster
docker-compose up -d

# Wait for services to be ready
Write-Host "Waiting for TiDB to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if TiDB is accessible
Write-Host "Testing TiDB connection..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0

do {
    $attempt++
    try {
        # Test connection to TiDB
        # mysql -h localhost -P 4000 -u root -e "SELECT 1;" 2>$null
        mysql --comments -u '3Eo7CXZzQYFQ3i5.root' -h gateway01.us-east-1.prod.aws.tidbcloud.com -P 4000 -D 'aurora' --ssl-mode=VERIFY_IDENTITY --ssl-ca=ca-cert.pem -p'sgCKlsXv6OhBfMta'
        if ($LASTEXITCODE -eq 0) {
            Write-Host "TiDB is ready!" -ForegroundColor Green
            break
        }
    }
    catch {
        Write-Host "Attempt $attempt failed, retrying..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
} while ($attempt -lt $maxAttempts)

if ($attempt -eq $maxAttempts) {
    Write-Host "Failed to connect to TiDB after $maxAttempts attempts" -ForegroundColor Red
    exit 1
}

Write-Host "TiDB cluster is running!" -ForegroundColor Green
Write-Host "Connection details:" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 4000" -ForegroundColor White
Write-Host "  User: root" -ForegroundColor White
Write-Host "  Password: (none)" -ForegroundColor White
Write-Host ""
Write-Host "Dashboard: http://localhost:12333" -ForegroundColor Cyan
Write-Host ""
Write-Host "To connect: mysql -h localhost -P 4000 -u root" -ForegroundColor Yellow