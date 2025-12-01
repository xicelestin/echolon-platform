# Echolon AI - Backend API Specifications

## Overview

This document provides complete API specifications for the Echolon AI backend services. These specs are designed for Abdul and John to implement the FastAPI backend endpoints that connect to the Streamlit dashboard.

## Base URL

```
http://localhost:8000  # Development
https://your-backend-api.com  # Production (set via BACKEND_API_URL env var)
```

## Authentication

Currently no authentication required (development phase). Add JWT/API key authentication before production deployment.

---

## Endpoint 1: Health Check

### Purpose
Verify backend service is running and responsive

### Request

```http
GET /health
```

### Response (200 OK)

```json
{
  "status": "healthy",
  "timestamp": "2024-12-01T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Endpoint 2: Upload CSV

### Purpose
Receive uploaded CSV data from dashboard, validate, process, and store for analysis

### Request

```http
POST /api/upload_csv
Content-Type: application/json
```

#### Request Body

```json
{
  "data": [
    {
      "date": "2024-01-01",
      "revenue": 50000,
      "customers": 245,
      "churn_rate": 2.1
    },
    {
      "date": "2024-01-02",
      "revenue": 52000,
      "customers": 248,
      "churn_rate": 2.0
    }
  ]
}
```

### Response (200 OK)

```json
{
  "status": "success",
  "message": "Data received and processed",
  "rows_processed": 2,
  "data_id": "upload_1234567890",
  "timestamp": "2024-12-01T10:30:00Z",
  "preview": {
    "total_rows": 2,
    "columns": ["date", "revenue", "customers", "churn_rate"],
    "date_range": "2024-01-01 to 2024-01-02"
  }
}
```

### Response (400 Bad Request)

```json
{
  "status": "error",
  "message": "Invalid data format",
  "details": [
    "Missing required field: revenue",
    "date column not in expected format"
  ]
}
```

### Implementation Notes

- Validate all required columns are present
- Store data in database or cache for later retrieval
- Log upload event with timestamp and data_id
- Return data_id for reference in insights/predictions requests

---

## Endpoint 3: Generate Insights

### Purpose
Analyze uploaded data and generate AI-powered business insights

### Request

```http
GET /api/insights?data_id=upload_1234567890&use_cache=true
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data_id` | string | No | ID from previous upload_csv call. If not provided, use demo data |
| `use_cache` | boolean | No | Use cached insights if available (default: true) |

### Response (200 OK)

```json
{
  "status": "success",
  "insights": [
    {
      "id": "insight_001",
      "title": "Strong Revenue Growth",
      "description": "Revenue has increased 15% month-over-month, outpacing industry average of 8%",
      "severity": "positive",
      "confidence": 0.92,
      "metrics": {
        "previous_month_revenue": 45000,
        "current_month_revenue": 51750,
        "growth_rate": 0.15
      },
      "recommendation": "Maintain current growth strategy. Analyze which products/services drive this growth."
    },
    {
      "id": "insight_002",
      "title": "Customer Churn Risk",
      "description": "Customer churn rate has increased slightly. Recommend proactive engagement",
      "severity": "warning",
      "confidence": 0.78,
      "metrics": {
        "previous_churn_rate": 1.9,
        "current_churn_rate": 2.1,
        "customers_at_risk": 12
      },
      "recommendation": "Implement customer retention campaign. Review recent customer feedback."
    }
  ],
  "data_summary": {
    "rows_analyzed": 365,
    "date_range": "2023-12-01 to 2024-11-30",
    "last_updated": "2024-12-01T10:35:00Z"
  },
  "cache_hit": false
}
```

### Response (404 Not Found)

```json
{
  "status": "error",
  "message": "Data not found",
  "data_id": "upload_invalid123"
}
```

### Implementation Notes

- Use ML models to detect patterns in uploaded data
- Each insight should have: title, description, severity (positive/neutral/warning), confidence score
- Include specific metrics that support each insight
- Provide actionable recommendations
- Cache insights for 1 hour to avoid recomputation

---

## Endpoint 4: Generate Predictions

### Purpose
Generate AI-powered predictions for business metrics based on historical data

### Request

```http
POST /api/predictions
Content-Type: application/json
```

#### Request Body

```json
{
  "metric": "Revenue",
  "horizon": "3 Months",
  "data_id": "upload_1234567890",
  "confidence_level": 0.95
}
```

### Parameters

| Parameter | Type | Required | Options |
|-----------|------|----------|----------|
| `metric` | string | Yes | "Revenue", "Customer Growth", "Churn Rate" |
| `horizon` | string | Yes | "1 Month", "3 Months", "6 Months" |
| `data_id` | string | No | ID from upload_csv. If not provided, use demo data |
| `confidence_level` | number | No | 0.0 to 1.0, default 0.95 |

### Response (200 OK)

```json
{
  "status": "success",
  "prediction": {
    "metric": "Revenue",
    "horizon": "3 Months",
    "model_used": "ARIMA",
    "accuracy_score": 0.87,
    "confidence": 0.92,
    "forecast": [
      {
        "date": "2024-12-01",
        "predicted_value": 55000,
        "lower_bound": 52000,
        "upper_bound": 58000,
        "confidence_interval": 0.95
      },
      {
        "date": "2025-01-01",
        "predicted_value": 62000,
        "lower_bound": 58000,
        "upper_bound": 66000,
        "confidence_interval": 0.95
      },
      {
        "date": "2025-02-01",
        "predicted_value": 68000,
        "lower_bound": 63000,
        "upper_bound": 73000,
        "confidence_interval": 0.95
      }
    ]
  },
  "model_performance": {
    "mae": 3500,
    "rmse": 4200,
    "training_data_points": 365,
    "last_trained": "2024-12-01T08:00:00Z"
  },
  "timestamp": "2024-12-01T10:40:00Z"
}
```

### Response (400 Bad Request)

```json
{
  "status": "error",
  "message": "Invalid prediction parameters",
  "details": [
    "metric must be one of: Revenue, Customer Growth, Churn Rate",
    "horizon must be one of: 1 Month, 3 Months, 6 Months"
  ]
}
```

### Implementation Notes

- Use time-series forecasting models (ARIMA, Prophet, LSTM, etc.)
- Always return confidence intervals (lower_bound, upper_bound)
- Include model accuracy metrics (MAE, RMSE, R-squared)
- Support retraining with new data
- Cache predictions for 24 hours
- Return training data statistics for model transparency

---

## Endpoint 5: Model Training (Optional)

### Purpose
Manually trigger ML model retraining with latest data

### Request

```http
POST /api/ml/train
Content-Type: application/json
```

#### Request Body

```json
{
  "data_id": "upload_1234567890",
  "model_types": ["revenue_forecast", "churn_prediction"],
  "test_split": 0.2
}
```

### Response (202 Accepted)

```json
{
  "status": "training_started",
  "job_id": "train_job_12345",
  "estimated_time": "5 minutes",
  "models_to_train": ["revenue_forecast", "churn_prediction"]
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "message": "Human-readable error message",
  "details": [
    "Specific error detail 1",
    "Specific error detail 2"
  ],
  "request_id": "req_123456",
  "timestamp": "2024-12-01T10:45:00Z"
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `202 Accepted` - Request accepted for processing (async)
- `400 Bad Request` - Invalid parameters or data format
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily down

---

## Rate Limiting

- 1000 requests per minute per IP
- Long-running requests (training, large predictions) may take up to 5 minutes
- Implement exponential backoff for retries

---

## Testing

### Using curl/httpie

```bash
# Test health check
curl http://localhost:8000/health

# Test CSV upload
curl -X POST http://localhost:8000/api/upload_csv \
  -H "Content-Type: application/json" \
  -d @sample_data.json

# Test insights
curl http://localhost:8000/api/insights?data_id=upload_1234567890

# Test predictions
curl -X POST http://localhost:8000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{"metric": "Revenue", "horizon": "3 Months"}'
```

---

## Implementation Checklist

- [ ] Implement /health endpoint
- [ ] Implement /api/upload_csv endpoint with validation
- [ ] Implement /api/insights endpoint with ML analysis
- [ ] Implement /api/predictions endpoint with forecasting
- [ ] Add error handling for all endpoints
- [ ] Add logging for all API calls
- [ ] Implement caching layer (Redis/Memcached)
- [ ] Add rate limiting
- [ ] Add request/response validation using Pydantic
- [ ] Write unit tests for each endpoint
- [ ] Create integration tests
- [ ] Document all endpoints in OpenAPI/Swagger
- [ ] Set up CI/CD pipeline for automated testing
- [ ] Deploy to staging and production

---

## Next Steps for Abdul and John

1. **Abdul**: Implement FastAPI endpoints 1-4
2. **John**: Implement ML models for insights and predictions (endpoints 3-4)
3. **Both**: Write comprehensive tests
4. **Both**: Deploy and monitor in production

Refer to this spec for exact request/response formats. If anything is unclear, update this document and share with the team.
