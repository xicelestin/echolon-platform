# AI Insights Implementation Guide

**For:** Abdul (Backend Engineer)
**Status:** Priority - Frontend is ready, backend endpoint needed
**Error on Dashboard:** `Could not connect to insights backend: Expecting value: line 1 column 1 (char 0)`

---

## Quick Summary

The Streamlit dashboard has a complete **Insights page** that's trying to call the `/api/insights` endpoint, but the backend doesn't have this endpoint implemented yet. Users see an error and placeholder KPIs instead of AI-generated insights.

**Your task:** Implement the `/api/insights` endpoint in FastAPI that analyzes uploaded CSV data and returns AI-generated business insights.

---

## Frontend Context: What's Currently Happening

### Current Flow (Broken)

1. User uploads CSV data via "Upload Data" page
2. Dashboard stores data in session state
3. User navigates to "Insights" page
4. Dashboard sends GET request to `/api/insights`
5. **Backend returns nothing or error** (PROBLEM)
6. Dashboard shows error: `Could not connect to insights backend`
7. Only hardcoded placeholder metrics display

### Expected Flow (After Implementation)

1. User uploads CSV data via "Upload Data" page
2. Dashboard stores data in session state and calls `/api/upload_csv`
3. User navigates to "Insights" page
4. Dashboard sends GET request to `/api/insights`
5. **Backend returns AI-generated insights** (YOUR TASK)
6. Dashboard displays insights dynamically

---

## Implementation Checklist

### Backend Endpoint: POST `/api/insights`

**Purpose:** Accept business metrics data, run ML analysis, return insights

**Request Format:**
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "revenue": 45000,
      "customers": 245,
      "churn_rate": 2.1,
      "customer_acquisition_cost": 241000,
      "customer_lifetime_value": 12450,
      "support_tickets": 42,
      "product_a_sales": 18000,
      "product_b_sales": 15000,
      "product_c_sales": 12000
    },
    // ... 29 more days of data
  ]
}
```

**Response Format:**
```json
{
  "status": "success",
  "insights": [
    {
      "metric": "Revenue",
      "insight": "Revenue has increased by 4.0%",
      "trend": "upward",
      "confidence": 0.85
    },
    {
      "metric": "Customers",
      "insight": "Customers has increased by 1.2%",
      "trend": "upward",
      "confidence": 0.92
    },
    {
      "metric": "Revenue",
      "insight": "Recent revenue shows downward trend (+0.0%)",
      "trend": "flat",
      "confidence": 0.78
    },
    {
      "metric": "Customers",
      "insight": "Recent customers shows downward trend (+0.0%)",
      "trend": "flat",
      "confidence": 0.65
    }
  ],
  "summary": {
    "total_records": 30,
    "date_range": "2024-01-01 to 2024-01-30",
    "analysis_timestamp": "2024-12-01T16:00:00Z"
  }
}
```

---

## Implementation Steps

### Step 1: Decide on ML Approach

Choose one (or combine):

**Option A: Simple Statistical Analysis (Quick MVP)**
- Calculate growth rates for each metric
- Detect trends using moving averages
- Identify anomalies using standard deviation
- Implementation time: 2-4 hours
- No ML dependencies needed

**Option B: ML Model-Based (More Powerful)**
- Use scikit-learn for trend detection
- Train models on historical data patterns
- Generate predictions alongside insights
- Implementation time: 6-8 hours
- Requires ML pipeline setup

**Option C: LLM-Based Insights (Most Advanced)**
- Send data to OpenAI/Claude API
- Get natural language insights
- Format and return to frontend
- Implementation time: 4-6 hours
- Requires API key management

**Recommendation:** Start with **Option A** (statistical), users see real insights immediately. Upgrade to Option B/C later.

### Step 2: Create Insights Engine

Create file: `backend/ml_engine/insights.py`

```python
import pandas as pd
from typing import List, Dict

class InsightsEngine:
    @staticmethod
    def analyze(data: List[Dict]) -> Dict:
        """Analyze metrics and generate insights"""
        df = pd.DataFrame(data)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        insights = []
        
        # Analyze each numeric column
        for column in df.select_dtypes(include=['number']).columns:
            # Calculate overall trend
            first_val = df[column].iloc[0]
            last_val = df[column].iloc[-1]
            change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
            
            # Calculate recent trend (last 7 days vs previous 7 days)
            if len(df) >= 14:
                recent = df[column].iloc[-7:].mean()
                previous = df[column].iloc[-14:-7].mean()
                recent_trend = ((recent - previous) / previous * 100) if previous != 0 else 0
            else:
                recent_trend = change_pct
            
            # Generate insight
            trend = "upward" if change_pct > 1 else "downward" if change_pct < -1 else "flat"
            insights.append({
                "metric": column.replace('_', ' ').title(),
                "insight": f"{column.replace('_', ' ').title()} has increased by {change_pct:.1f}%",
                "trend": trend,
                "confidence": 0.85  # Placeholder
            })
        
        return {
            "status": "success",
            "insights": insights,
            "summary": {
                "total_records": len(df),
                "date_range": f"{df['date'].min().date()} to {df['date'].max().date()}",
                "analysis_timestamp": pd.Timestamp.now().isoformat()
            }
        }
```

### Step 3: Create FastAPI Endpoint

Add to `backend/routes/insights.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from ml_engine.insights import InsightsEngine

router = APIRouter(prefix="/api", tags=["insights"])

class InsightsRequest(BaseModel):
    data: List[Dict]

@router.post("/insights")
async def generate_insights(request: InsightsRequest):
    """Generate AI-powered insights from business data"""
    try:
        if not request.data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        # Run insights analysis
        insights = InsightsEngine.analyze(request.data)
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights():
    """Get insights from previously uploaded data"""
    # This is called by dashboard when no active data session
    # Return sample insights or stored data
    return {
        "status": "info",
        "message": "Upload CSV data first to generate insights"
    }
```

### Step 4: Register Route in Main App

In `backend/main.py`:

```python
from routes import insights

app = FastAPI()

# Include insights router
app.include_router(insights.router)
```

### Step 5: Test the Endpoint

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/insights \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"date": "2024-01-01", "revenue": 45000, "customers": 245},
      {"date": "2024-01-02", "revenue": 46000, "customers": 248}
    ]
  }'
```

**Using Python:**
```python
import requests

data = {
    "data": [
        {"date": "2024-01-01", "revenue": 45000, "customers": 245},
        {"date": "2024-01-02", "revenue": 46000, "customers": 248}
    ]
}

response = requests.post("http://localhost:8000/api/insights", json=data)
print(response.json())
```

---

## Frontend Integration (Already Ready)

The frontend code that calls this endpoint:

```python
# In dashboard app.py (Insights page)
try:
    response = requests.get(f"{BACKEND_API_URL}/api/insights", timeout=10)
    if response.status_code == 200:
        insights_data = response.json()
        st.success("Connected to ML insights model")
except Exception as e:
    st.warning(f"Could not connect to insights backend: {str(e)}")
```

Once your endpoint is working, the dashboard will automatically display insights.

---

## Validation Checklist Before Submitting

- [ ] Endpoint accepts POST requests to `/api/insights`
- [ ] Request body includes `data` field with array of records
- [ ] Each record has at least `date`, `revenue`, `customers` fields
- [ ] Response returns JSON with `status`, `insights`, `summary` fields
- [ ] Insights array contains at least 2-4 insight objects
- [ ] Each insight has `metric`, `insight`, `trend`, `confidence` fields
- [ ] Endpoint handles empty data gracefully (returns 400 error)
- [ ] Endpoint handles malformed data gracefully (returns 500 error)
- [ ] Tested with curl/httpie and works without errors
- [ ] When called, dashboard shows insights instead of error message

---

## Success Criteria

✅ **Endpoint is working when:**

1. Dashboard Insights page shows: "Connected to ML insights model" (green success)
2. Auto-generated insights display below KPI metrics
3. Insights update dynamically when user uploads new CSV data
4. No warning/error message appears

---

## Questions?

If you need clarification on:
- ML approach to use
- Data format expected
- Response structure
- How to integrate with existing ML models

Refer to API_SPECS.md for the full API contract or ask for help.

**This is a priority task - dashboard is 90% ready, insights endpoint is the last piece for demo-ready MVP.**
