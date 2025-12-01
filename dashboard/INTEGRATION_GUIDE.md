# Echolon AI Dashboard - Integration Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Dashboard Architecture](#dashboard-architecture)
3. [File Structure](#file-structure)
4. [Integration Points for ML Models](#integration-points-for-ml-models)
5. [CSV Upload & API Connection Flow](#csv-upload--api-connection-flow)
6. [Session State Management](#session-state-management)
7. [Code Snippets & Examples](#code-snippets--examples)
8. [Data Source Indicators](#data-source-indicators)
9. [Troubleshooting & FAQ](#troubleshooting--faq)
10. [Deployment Checklist](#deployment-checklist)

---

## Quick Start

This guide is designed for Abdul and John to understand how to integrate ML models and backend services into the Echolon AI dashboard. The dashboard is built with Streamlit and consists of 4 main pages:

- **Home**: KPI metrics, revenue chart, sales category chart, and placeholder sections for AI insights
- **Upload Data**: CSV file uploader for connecting to your backend APIs
- **Insights**: Business insights dashboard (ML model integration point)
- **Predictions**: AI-powered predictions configuration and results (ML model integration point)

### Key Principles

- **Keep it simple**: No over-engineered state management or complex validation
- **Leave integration points open**: Don't lock down API connections
- **Data-driven charts**: All charts should update dynamically based on uploaded CSV data
- **No emojis**: UI text must remain clean and professional

---

## Dashboard Architecture

### High-Level Overview

```
Streamlit App (Frontend)
    |
    ├── Home Page (KPI Dashboard)
    ├── Upload Data Page (CSV Handler)
    ├── Insights Page (ML Model #1)
    └── Predictions Page (ML Model #2)
    |
    Backend APIs
        |
        ├── CSV Processing Service
        ├── Insights Generation Service
        └── Predictions Generation Service
```

### Page Navigation

The sidebar uses Streamlit radio buttons for navigation. No emojis are used in any navigation labels.

```python
page = st.radio("Navigation", ["Home", "Upload Data", "Insights", "Predictions"])
```

---

## File Structure

```
dashboard/
├── app.py                 # Main Streamlit application
├── INTEGRATION_GUIDE.md   # This file
├── requirements.txt       # Python dependencies
└── data/                  # Data storage (optional)
    └── sample_data.csv    # Sample CSV for testing
```

---

## Integration Points for ML Models

### 1. Insights Page - Where Abdul Connects ML Insights

**Current State**: The Insights page shows a connection error placeholder

**Your Task**: Replace the error handling with actual ML model calls

**Code Location**: In `app.py`, find the Insights page section:

```python
if page == "Insights":
    st.title("Business Insights Dashboard")
    
    # INTEGRATION POINT: Connect to your ML insights model here
    try:
        # Call your backend insights API
        insights_data = get_insights_from_backend()
        display_insights(insights_data)
    except Exception as e:
        st.error(f"Error connecting to insights service: {e}")
```

### 2. Predictions Page - Where John Connects ML Predictions

**Current State**: Configuration UI with placeholder predictions

**Your Task**: Connect the "Generate Predictions" button to your ML model

**Code Location**: In `app.py`, find the Predictions page section:

```python
if page == "Predictions":
    st.title("AI-Powered Predictions")
    
    # Configuration section
    col1, col2 = st.columns(2)
    with col1:
        selected_metric = st.selectbox("Select Metric", ["Revenue", "Customer Growth", "Churn Rate"])
    with col2:
        prediction_horizon = st.selectbox("Prediction Horizon", ["1 Month", "3 Months", "6 Months"])
    
    if st.button("Generate Predictions"):
        # INTEGRATION POINT: Call your predictions API here
        predictions = get_predictions_from_ml_model(selected_metric, prediction_horizon)
        display_predictions(predictions)
```

---

## CSV Upload & API Connection Flow

### User Flow

1. User navigates to "Upload Data" page
2. User selects or drags CSV file
3. CSV is read into memory
4. Data is sent to backend API
5. API processes data and returns structured result
6. Charts on Home page automatically update with new data
7. Data source indicator shows "Connected to your uploaded data" badge

### Implementation Code

```python
if page == "Upload Data":
    st.title("Upload Your Data")
    
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type="csv",
        help="Limit 200MB per file"
    )
    
    if uploaded_file is not None:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Store in session state for access across pages
        st.session_state.uploaded_data = df
        st.session_state.data_source = "uploaded"
        
        # INTEGRATION POINT: Send to backend API
        response = send_to_backend_api(df)
        
        if response.status_code == 200:
            st.success("Data successfully processed!")
            st.session_state.api_response = response.json()
        else:
            st.error("Failed to process data. Please try again.")
    else:
        st.info("Please upload a CSV file to begin")
```

---

## Session State Management

Streamlit session state is used to persist data across page reloads and navigation:

```python
# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None

if 'data_source' not in st.session_state:
    st.session_state.data_source = 'demo'  # 'demo' or 'uploaded'

if 'api_response' not in st.session_state:
    st.session_state.api_response = None

if 'insights_cache' not in st.session_state:
    st.session_state.insights_cache = None

if 'predictions_cache' not in st.session_state:
    st.session_state.predictions_cache = None
```

### Usage Pattern

```python
# Store data
st.session_state.uploaded_data = dataframe

# Access data from other pages
if st.session_state.uploaded_data is not None:
    data = st.session_state.uploaded_data
```

---

## Code Snippets & Examples

### Snippet 1: Making an API Call to Backend

```python
import requests
import json

def send_to_backend_api(dataframe):
    """Send uploaded CSV data to backend for processing"""
    
    # Convert dataframe to JSON
    data = dataframe.to_dict(orient='records')
    
    # Prepare API request
    payload = {
        'data': data,
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    # Make API call
    try:
        response = requests.post(
            'https://your-backend-api.com/api/process-csv',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return response
    except Exception as e:
        st.error(f"API Error: {e}")
        return None
```

### Snippet 2: Fetching Insights from ML Model

```python
def get_insights_from_backend():
    """Fetch AI-generated insights from backend ML model"""
    
    # Use uploaded data if available, otherwise use demo data
    data_source = st.session_state.get('data_source', 'demo')
    
    # Prepare request payload
    payload = {
        'data_source': data_source,
        'use_cache': True  # Use cached results if available
    }
    
    try:
        response = requests.get(
            'https://your-backend-api.com/api/insights',
            params=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status {response.status_code}")
            
    except Exception as e:
        st.error(f"Could not fetch insights: {e}")
        return None
```

### Snippet 3: Dynamic Chart with CSV Data

```python
def create_revenue_chart():
    """Create revenue chart that updates with uploaded data"""
    
    # Check if user has uploaded data
    if st.session_state.get('data_source') == 'uploaded' and st.session_state.get('uploaded_data') is not None:
        df = st.session_state.uploaded_data
        
        # Use uploaded data (assumes CSV has 'date' and 'revenue' columns)
        chart_data = df[['date', 'revenue']].set_index('date')
        
        st.line_chart(
            chart_data,
            use_container_width=True,
            height=300,
            color="#FF9500"  # Orange color
        )
    else:
        # Use demo data
        demo_data = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
            'Revenue': [45000, 52000, 48000, 61000, 58000]
        }).set_index('Week')
        
        st.line_chart(
            demo_data,
            use_container_width=True,
            height=300,
            color="#FF9500"
        )
```

### Snippet 4: Data Source Indicator Badge

```python
def display_data_source_badge():
    """Show user whether using demo or uploaded data"""
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        data_source = st.session_state.get('data_source', 'demo')
        
        if data_source == 'uploaded':
            st.success("Connected to your uploaded data")
        else:
            st.info("Using demo data")

# Display in Home page
if page == "Home":
    st.title("Welcome back")
    st.subtitle("Echolon AI Dashboard")
    
    # Show data source
    display_data_source_badge()
```

---

## Data Source Indicators

### Implementation

Add a badge on the Home page to indicate whether the dashboard is using demo data or live uploaded data:

```python
# At the top of Home page
if st.session_state.get('data_source') == 'uploaded':
    st.success('Dashboard connected to your uploaded data')
else:
    st.info('Dashboard showing demo data - Upload CSV to connect live data')
```

---

## Troubleshooting & FAQ

### Q: Charts are not updating after I upload CSV data

**A**: Make sure you're storing the data in session state:
```python
st.session_state.uploaded_data = df
st.session_state.data_source = 'uploaded'
```

Also verify that your CSV has the columns the charts expect (e.g., 'date', 'revenue')

### Q: How do I test the API integration locally?

**A**: Use a mock backend service:
```python
def mock_api_call():
    return {'status': 'success', 'data': {'insights': []}}
```

### Q: Can I test without connecting to the backend?

**A**: Yes! Use demo data mode:
```python
if st.session_state.get('data_source') == 'demo':
    # Use hardcoded demo data
```

### Q: What happens if the API is down?

**A**: The app shows an error message but doesn't crash:
```python
try:
    response = requests.get(api_url, timeout=5)
except requests.Timeout:
    st.error("API timeout - please try again")
except requests.ConnectionError:
    st.error("Cannot connect to API - is it running?")
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All four navigation pages are functional
- [ ] CSV upload successfully sends data to backend API
- [ ] Charts update dynamically based on uploaded data
- [ ] Data source indicator shows correct status
- [ ] No emojis appear anywhere in the UI
- [ ] Error messages display gracefully
- [ ] Session state persists across page navigation
- [ ] Backend API endpoints are tested and working
- [ ] Insights page connects to ML insights model
- [ ] Predictions page connects to ML predictions model
- [ ] "Download sample CSV" button is functional (if added)
- [ ] All tests pass locally
- [ ] Deploy to Streamlit Cloud
- [ ] Verify live dashboard works end-to-end

---

## Next Steps

1. **Abdul**: Implement the Insights page ML model integration using Snippet 2
2. **John**: Implement the Predictions page ML model integration using code pattern from Predictions section
3. **Both**: Test CSV upload flow and verify charts update correctly
4. **Both**: Deploy to production and monitor

Contact the team if you have questions about any integration points!
