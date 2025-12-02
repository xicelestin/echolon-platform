# Echolon AI Dashboard

AI-powered business intelligence platform built with Streamlit for SMBs.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)
```bash
export ECHOLON_API_URL="http://localhost:8000"
export ECHOLON_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
ECHOLON_API_URL=http://localhost:8000
ECHOLON_API_KEY=your-api-key-here
```

### 3. Run the Dashboard
```bash
streamlit run app.py
```

## Project Structure

```
dashboard/
├── app.py                      # Main Streamlit application
├── api_client.py               # Backend API communication
├── insights_handler.py         # ML insights integration (Abdul)
├── predictions_handler.py      # ML predictions integration (John)
├── requirements.txt            # Python dependencies
├── sample_data.csv            # Sample data for testing
├── sample_business_data.csv   # Extended sample data
├── INTEGRATION_GUIDE.md       # Detailed integration documentation
└── README.md                  # This file
```

## Integration Points

### For Abdul (ML Insights)

The insights integration is in `insights_handler.py`:

```python
from insights_handler import render_insights_page

# In app.py, Insights page section:
if page == "Insights":
    render_insights_page()
```

**To connect your ML model:**
1. Open `insights_handler.py`
2. Find `render_insights_page()` function
3. Replace `MockAPIClient()` with `APIClient()`
4. Your ML model should return insights in this format:

```python
{
    "insights": [
        {
            "category": "Revenue Trends",
            "title": "Strong monthly growth",
            "description": "Revenue increased 12.5% over last month",
            "confidence": 0.92
        }
    ],
    "generated_at": "2025-12-01T16:00:00"
}
```

### For John (ML Predictions)

The predictions integration is in `predictions_handler.py`:

```python
from predictions_handler import render_predictions_page

# In app.py, Predictions page section:
if page == "Predictions":
    render_predictions_page()
```

**To connect your ML model:**
1. Open `predictions_handler.py`
2. Find `render_predictions_page()` function
3. Replace `MockAPIClient()` with `APIClient()`
4. Your ML model should return predictions in this format:

```python
{
    "metric": "Revenue",
    "horizon": "3 Months",
    "predictions": [
        {
            "period": "Month 1",
            "predicted_value": 105000,
            "confidence_lower": 103000,
            "confidence_upper": 107000
        }
    ],
    "model_accuracy": 0.87,
    "generated_at": "2025-12-01T16:00:00"
}
```

## API Client Usage

The `api_client.py` module handles all backend communication:

```python
from api_client import APIClient, MockAPIClient

# For production with real backend:
client = APIClient()

# For testing without backend:
client = MockAPIClient()

# Upload CSV data
response = client.upload_csv_data(dataframe)

# Get insights
insights = client.get_insights(data_source='demo')

# Get predictions
predictions = client.get_predictions(
    metric='Revenue',
    horizon='3 Months',
    data_source='demo'
)

# Health check
is_healthy = client.health_check()
```

## Testing Without Backend

All modules include mock implementations for testing:

```python
# Mock API client provides realistic test data
from api_client import MockAPIClient
client = MockAPIClient()

# Returns mock insights
insights = client.get_insights()

# Returns mock predictions with charts
predictions = client.get_predictions('Revenue', '3 Months')
```

## Backend API Endpoints

Your backend should implement these endpoints:

- `POST /api/upload` - Process uploaded CSV data
- `GET /api/insights?data_source=demo` - Return ML-generated insights
- `POST /api/predictions` - Generate predictions for metrics
- `GET /health` - Health check endpoint

See `INTEGRATION_GUIDE.md` for detailed API specifications.

## Configuration

### Environment Variables

- `ECHOLON_API_URL` - Backend API URL (default: `http://localhost:8000`)
- `ECHOLON_API_KEY` - API authentication key (optional)

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#FF9500"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"

[server]
port = 8501
enableCORS = false
```

## Data Format

CSV uploads should have these columns:

```csv
date,revenue,customers,churn_rate,avg_order_value
2025-01-01,50000,8432,2.3,285
2025-02-01,52000,8640,2.1,290
```

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect your repo: `echolon44/echolon-platform`
4. Set main file path: `dashboard/app.py`
5. Add secrets in Streamlit Cloud dashboard:
   ```
   ECHOLON_API_URL = "https://your-backend-api.com"
   ECHOLON_API_KEY = "your-production-key"
   ```

### Deploy Backend API

Your FastAPI backend should be deployed separately. Recommended platforms:
- Railway
- Render
- Fly.io
- AWS Lambda

## Troubleshooting

### Charts Not Updating
- Verify CSV has correct columns
- Check session state: `st.session_state.uploaded_data`
- Ensure data source is set: `st.session_state.data_source = 'uploaded'`

### API Connection Fails
- Check `ECHOLON_API_URL` is correct
- Verify backend is running
- Test with `MockAPIClient` first
- Check CORS settings if deployed

### Import Errors
- Run `pip install -r requirements.txt`
- Verify all .py files are in same directory
- Check Python version >= 3.8

## Next Steps

1. Test locally with mock data
2. Connect Abdul's ML insights model
3. Connect John's ML predictions model
4. Deploy backend API
5. Update API URLs in production
6. Deploy to Streamlit Cloud

## Support

For questions:
- Check `INTEGRATION_GUIDE.md` for detailed documentation
- Review code comments in each module
- Test with mock clients before connecting real backend

---

**Built with Streamlit & FastAPI**  
© 2024 Echolon AI
