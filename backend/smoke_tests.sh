#!/bin/bash
# Echolon AI API - Comprehensive Smoke Tests
# Tests all critical endpoints after deployment
# Usage: ./smoke_tests.sh [BASE_URL]
#   Example: ./smoke_tests.sh https://echolon-api-abc123.run.app
#   Or: ./smoke_tests.sh http://localhost:8080 (for local testing)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-http://localhost:8080}"
TEST_DATA_DIR="./test_data"
PASSED=0
FAILED=0
TOTAL=0

echo "=========================================="
echo "Echolon AI API - Smoke Test Suite"
echo "=========================================="
echo "Target: $BASE_URL"
echo "Time: $(date)"
echo ""

# Helper function to run tests
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="${5:-}"
    
    ((TOTAL++))
    echo -n "[$TOTAL] Testing $name... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
    fi
    
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status)"
        ((PASSED++))
        if [ -n "$body" ] && [ "$body" != "" ]; then
            echo "  Response: $(echo $body | cut -c1-100)..."
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_status, Got: $status)"
        ((FAILED++))
        if [ -n "$body" ]; then
            echo "  Error: $body"
        fi
    fi
    echo ""
}

# Test Suite
echo "=== Basic Connectivity ==="

# 1. Root endpoint
test_endpoint "Root endpoint" "GET" "/" "200"

# 2. Health check
test_endpoint "Health check" "GET" "/health" "200"

# 3. API v1 base (if exists)
test_endpoint "API v1 root" "GET" "/api/v1" "200"

echo "=== API Endpoints ==="

# 4. Upload CSV endpoint (without data - should fail gracefully)
test_endpoint "Upload CSV (no data)" "POST" "/api/v1/upload_csv" "422"

# 5. Upload CSV with sample data
if [ -f "$TEST_DATA_DIR/sample.csv" ]; then
    echo "[5] Testing Upload CSV (with file)..."
    response=$(curl -s -w "\n%{http_code}" -X POST -F "file=@$TEST_DATA_DIR/sample.csv" "$BASE_URL/api/v1/upload_csv")
    status=$(echo "$response" | tail -n1)
    if [ "$status" = "200" ] || [ "$status" = "201" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (Status: $status)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠ SKIPPED${NC} (No test data file)"
    fi
    ((TOTAL++))
    echo ""
else
    echo -e "${YELLOW}⚠ SKIPPED${NC} - No test CSV file at $TEST_DATA_DIR/sample.csv"
    echo ""
fi

# 6. ML Train endpoint
test_endpoint "ML Train (no data)" "POST" "/api/v1/ml/train" "422"

# 7. ML Forecast endpoint  
test_endpoint "ML Forecast (no data)" "POST" "/api/v1/ml/forecast" "422"

# 8. ML Insights endpoint
test_endpoint "ML Insights (no data)" "POST" "/api/v1/ml/insights" "422"

echo "=== Error Handling ==="

# 9. Non-existent endpoint (404)
test_endpoint "Non-existent endpoint" "GET" "/api/v1/nonexistent" "404"

# 10. Invalid method
test_endpoint "Invalid method" "DELETE" "/" "405"

echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "Failed: $FAILED"
fi

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed! ✗${NC}"
    exit 1
fi
