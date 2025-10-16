# Test Coverage Runner for Airline Policy Assistant Service (PowerShell)
# This script runs pytest with coverage reporting

Write-Host "=========================================="
Write-Host "Running Unit Tests with Coverage"
Write-Host "=========================================="
Write-Host ""

# Run pytest with coverage
pipenv run coverage run -m pytest tests/unit -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Generating Coverage Report"
Write-Host "=========================================="
Write-Host ""

# Generate coverage report
pipenv run coverage report -m

Write-Host ""
Write-Host "=========================================="
Write-Host "Generating HTML Coverage Report"
Write-Host "=========================================="
Write-Host ""

# Generate HTML coverage report
pipenv run coverage html

Write-Host ""
Write-Host "Coverage report generated in: htmlcov/index.html" -ForegroundColor Green
Write-Host ""
Write-Host "To view the HTML report, open: htmlcov/index.html in your browser"
Write-Host ""
