# Echolon Platform API Reference

**Version:** 1.0 | **Base URL:** `https://YOUR-CLOUD-RUN-SERVICE-URL`

## Authentication

Include API key in all requests:
```bash
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check
`GET /health` - Verify service status
```bash
curl https://YOUR-URL/health
# Response: {"status": "healthy", "version": "1.0"}
```

### Upload CSV
`POST /api/v1/upload_csv` - Upload data for analysis
```bash
curl -X POST -H "Authorization: Bearer KEY" \
  -F "file=@data.csv" https://YOUR-URL/api/v1/upload_csv
```
**Response:** `dataset_id`, `rows_processed`, `columns`

### Train Model
`POST /ml/train` - Train ML model on dataset
```bash
curl -X POST -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": "ds_123", "forecast_horizon": 30}' \
  https://YOUR-URL/ml/train
```
**Parameters:**
- `dataset_id` (required)
- `forecast_horizon` (7-365 days, default: 30)
- `model_type` ("linear", "ensemble", "neural_network")

**Response:** `training_job_id`, `status`, `estimated_completion`

### Generate Forecast
`POST /ml/forecast` - Get predictions
```bash
curl -X POST -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "model_123"}' https://YOUR-URL/ml/forecast
```
**Response:** Forecast data with confidence intervals

### Get Insights
`GET /ml/insights?model_id=MODEL_ID` - AI-generated recommendations
```bash
curl -H "Authorization: Bearer KEY" \
  "https://YOUR-URL/ml/insights?model_id=model_123&top_insights=5"
```
**Insight Types:** trends, anomalies, recommendations

## Error Handling

All errors return:
```json
{
  "error": true,
  "error_code": "CODE",
  "message": "Description",
  "timestamp": "2024-12-01T00:00:00Z"
}
```

**Common Codes:**
- `UNAUTHORIZED` (401) - Invalid API key
- `NOT_FOUND` (404) - Resource doesn't exist
- `INVALID_REQUEST` (400) - Bad parameters
- `RATE_LIMIT` (429) - Too many requests

## Rate Limits

| Plan | Requests/Hour | Datasets | Models |
|------|---------------|----------|--------|
| Free Trial | 100 | 3 | 5 |
| Starter | 500 | 10 | 20 |
| Pro | 2,000 | 50 | 100 |
| Enterprise | Custom | Custom | Custom |

## Complete Workflow Example

```bash
# 1. Upload CSV
RESP=$(curl -X POST -H "Authorization: Bearer KEY" \
  -F "file=@sales.csv" https://YOUR-URL/api/v1/upload_csv)
DATASET_ID=$(echo $RESP | jq -r '.dataset_id')

# 2. Train model
RESP=$(curl -X POST -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d "{\"dataset_id\": \"$DATASET_ID\"}" \
  https://YOUR-URL/ml/train)
MODEL_ID=$(echo $RESP | jq -r '.model_id')

# 3. Get forecast
curl -X POST -H "Authorization: Bearer KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model_id\": \"$MODEL_ID\"}" \
  https://YOUR-URL/ml/forecast

# 4. Get insights
curl -H "Authorization: Bearer KEY" \
  "https://YOUR-URL/ml/insights?model_id=$MODEL_ID"
```

## Support

- **Docs:** `docs/README.md`
- **Issues:** GitHub Issues
- **Email:** support@echolon.ai

**Ready to start?** [Sign up for 4 weeks free](https://echolon.ai/signup)!
