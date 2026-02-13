"""Smoke Test Suite for Echolon AI Backend.

This script verifies that all components are properly glued together:
- FastAPI app runs without import errors
- All routes are registered
- Database connectivity works
- ML services can be initialized
"""

from fastapi.testclient import TestClient
from main import app
import json
import io
import csv

# Initialize test client
client = TestClient(app)

# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_health_check():
    """Test that /health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed")

def test_root_endpoint():
    """Test that root endpoint returns running status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Echolon AI API" in data["message"]
    assert data["status"] == "running"
    print("✓ Root endpoint passed")

# ============================================================================
# API DOCUMENTATION TESTS
# ============================================================================

def test_api_docs():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
    print("✓ API docs accessible")

def test_openapi_schema():
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    print("✓ OpenAPI schema available")

# ============================================================================
# ROUTE REGISTRATION TESTS
# ============================================================================

def test_all_endpoints_registered():
    """Test that all required endpoints are registered."""
    response = client.get("/openapi.json")
    schema = response.json()
    paths = schema["paths"]
    
    required_endpoints = [
        "/api/v1/upload_csv",
        "/api/v1/insights",
        "/api/v1/predictions",
        "/api/v1/ml/forecast",
        "/api/v1/ml/insights",
        "/api/v1/ml/train/{business_id}/{metric_name}"
    ]
    
    for endpoint in required_endpoints:
        assert endpoint in paths, f"Missing endpoint: {endpoint}"
        print(f"  ✓ {endpoint} registered")
    
    print(f"✓ All {len(required_endpoints)} required endpoints registered")

# ============================================================================
# CSV UPLOAD TESTS
# ============================================================================

def test_csv_upload_invalid_file():
    """Test that uploading non-CSV file is rejected."""
    response = client.post(
        "/api/v1/upload_csv",
        files={"file": ("test.txt", b"not a csv")}
    )
    assert response.status_code == 400
    assert "CSV" in response.json()["detail"]
    print("✓ Invalid file type rejected")

def test_csv_upload_missing_columns():
    """Test that CSV without required columns is rejected."""
    csv_content = "id,name\n1,test\n"
    response = client.post(
        "/api/v1/upload_csv",
        files={"file": ("test.csv", csv_content.encode())}
    )
    assert response.status_code == 400
    assert "date" in response.json()["detail"].lower()
    print("✓ Missing columns rejected")

def test_csv_upload_valid():
    """Test that valid CSV is accepted and processed."""
    # Create valid CSV
    csv_content = "date,metric_name,value\n2024-01-01,revenue,1000\n2024-01-02,revenue,1200\n"
    response = client.post(
        "/api/v1/upload_csv",
        files={"file": ("test.csv", csv_content.encode())}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rows_processed"] == 2
    print(f"✓ CSV upload successful ({data['rows_processed']} rows processed)")

# ============================================================================
# ML ENDPOINT TESTS
# ============================================================================

def test_ml_insights_endpoint():
    """Test that ML insights endpoint is functional."""
    payload = {
        "forecast_data": [
            {"date": "2024-12-01", "value": 1500, "lower_bound": 1400, "upper_bound": 1600},
            {"date": "2024-12-02", "value": 1550, "lower_bound": 1450, "upper_bound": 1650}
        ],
        "metric_name": "revenue",
        "business_context": "E-commerce business"
    }
    response = client.post("/api/v1/ml/insights", json=payload)
    assert response.status_code == 200
    print("✓ ML insights endpoint functional")

def test_business_insights_endpoint():
    """Test that business insights endpoint is functional."""
    response = client.get("/api/v1/insights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✓ Business insights endpoint functional ({len(data)} metrics)")

def test_predictions_endpoint():
    """Test that predictions endpoint is functional."""
    response = client.get("/api/v1/predictions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✓ Predictions endpoint functional ({len(data)} predictions)")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all smoke tests."""
    print("\n" + "="*70)
    print("ECHOLON AI BACKEND - SMOKE TEST SUITE")
    print("="*70 + "\n")
    
    tests = [
        ("Health Checks", [
            test_health_check,
            test_root_endpoint,
        ]),
        ("API Documentation", [
            test_api_docs,
            test_openapi_schema,
        ]),
        ("Route Registration", [
            test_all_endpoints_registered,
        ]),
        ("CSV Upload Functionality", [
            test_csv_upload_invalid_file,
            test_csv_upload_missing_columns,
            test_csv_upload_valid,
        ]),
        ("ML Endpoints", [
            test_ml_insights_endpoint,
            test_business_insights_endpoint,
            test_predictions_endpoint,
        ]),
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for section_name, section_tests in tests:
        print(f"\n[{section_name}]")
        for test_func in section_tests:
            total_tests += 1
            try:
                test_func()
                passed_tests += 1
            except AssertionError as e:
                failed_tests += 1
                print(f"✗ {test_func.__name__} FAILED: {str(e)}")
            except Exception as e:
                failed_tests += 1
                print(f"✗ {test_func.__name__} ERROR: {str(e)}")
    
    # Summary
    print(f"\n" + "="*70)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
    if failed_tests > 0:
        print(f"FAILED: {failed_tests} tests")
    print("="*70 + "\n")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
