#!/bin/bash

# Test Coverage Runner for Airline Policy Assistant Service
# This script runs pytest with coverage reporting

set -e

echo "=========================================="
echo "Running Unit Tests with Coverage"
echo "=========================================="
echo ""

# Run pytest with coverage
pipenv run coverage run -m pytest tests/unit -v

echo ""
echo "=========================================="
echo "Generating Coverage Report"
echo "=========================================="
echo ""

# Generate coverage report
pipenv run coverage report -m

echo ""
echo "=========================================="
echo "Generating HTML Coverage Report"
echo "=========================================="
echo ""

# Generate HTML coverage report
pipenv run coverage html

echo ""
echo "Coverage report generated in: htmlcov/index.html"
echo ""
echo "To view the HTML report, open: htmlcov/index.html in your browser"
echo ""
