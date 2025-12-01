# Echolon AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Python 3.10+
- pip
- Homebrew (macOS)

---

## 1️⃣ Install Dependencies

### Backend
```bash
cd echolon-platform/backend
pip install -r requirements.txt
```

### Dashboard
```bash
cd echolon-platform/dashboard
pip install -r requirements.txt
```

### macOS - Install OpenMP for XGBoost

**Apple Silicon (M1/M2/M3):**
```bash
# IMPORTANT: Must use ARM Homebrew at /opt/homebrew
/opt/homebrew/bin/brew install libomp
```

**Intel Mac:**
```bash
brew install libomp
```

**Verify XGBoost works:**
```bash
python3 -c "import xgboost; print('✅ XGBoost:', xgboost.__version__)"
```

---

## 2️⃣ Start the Services

### Terminal 1 - Backend API (Port 8000)
```bash
cd echolon-platform/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Frontend Dashboard (Port 8501)
```bash
cd echolon-platform/dashboard
streamlit run app.py --server.port 8501 --server.headless true
```

---

## 3️⃣ Test the Application

### Open the Dashboard
Navigate to: **http://localhost:8501**

### Upload Sample Data
1. Go to **📤 Upload Data** in the sidebar
2. Upload `backend/sample.csv` (or any CSV with `date`, `metric_name`, `value` columns)

### Generate a Forecast
1. Go to **🔮 Predictions** in the sidebar
2. Configure:
   - **Metric Name**: `Revenue` (must match your uploaded data)
   - **Horizon**: `30 Days`
   - **Model Type**: `auto` (uses XGBoost if available, else Prophet)
   - **Business ID**: `1`
3. Click **🚀 Generate Forecast**

### Quick API Test
```bash
# Health check
curl http://localhost:8000/health

# Upload sample data
curl -X POST http://localhost:8000/api/v1/upload_csv \
  -F "file=@backend/sample.csv"

# Generate forecast
curl -X POST http://localhost:8000/api/v1/ml/forecast \
  -H "Content-Type: application/json" \
  -d '{"business_id": 1, "metric_name": "Revenue", "horizon": 30, "model_type": "auto"}'
```

---

## ✅ Expected Results

- 📈 Interactive forecast chart with predictions
- 📊 Model performance metrics (MAE, RMSE)
- 📋 Forecast summary with growth/decline projections
- 🔍 Confidence intervals (Prophet model)

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/upload_csv` | POST | Upload CSV data (multipart form) |
| `/api/v1/ml/forecast` | POST | Generate forecast |
| `/api/v1/ml/train/{business_id}/{metric_name}` | POST | Train model explicitly |
| `/api/v1/ml/insights` | POST | Generate AI insights |
| `/api/v1/insights` | GET | Get cached insights |
| `/api/v1/predictions` | GET | Get cached predictions |

### Forecast Request Schema
```json
{
  "business_id": 1,
  "metric_name": "Revenue",
  "horizon": 30,
  "model_type": "auto"  // "auto", "xgboost", or "prophet"
}
```

---

## 🐛 Troubleshooting

### "No data found" error
- Ensure CSV was uploaded successfully
- Check metric name matches exactly (case-sensitive)
- Verify business_id matches your upload (default: 1)

### "Insufficient data" error
- Need at least 30 data points for training
- Upload more historical data

### XGBoost not loading (macOS)

**Symptom:** `XGBoost Library (libxgboost.dylib) could not be loaded`

**Apple Silicon (M1/M2/M3):**
```bash
# Check architecture
uname -m  # Should show: arm64

# Install ARM libomp (MUST use /opt/homebrew)
/opt/homebrew/bin/brew install libomp

# Verify
python3 -c "import xgboost; print('✅ Works!')"
```

**Common Issue - Architecture Mismatch:**
If you see `incompatible architecture (have 'x86_64', need 'arm64')`, your libomp is Intel-based. Install via ARM Homebrew:
```bash
/opt/homebrew/bin/brew install libomp
```

### Backend not responding
- Ensure you're in the `backend` directory
- Check port 8000: `lsof -i :8000`
- Kill existing process: `pkill -f "uvicorn main:app"`

### Frontend not loading
- Check port 8501: `lsof -i :8501`
- Verify backend is running first

---

## 📁 Project Structure

```
echolon-platform/
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints.py     # API routes
│   │   ├── db/database.py       # Database config
│   │   ├── models/models.py     # SQLAlchemy models
│   │   ├── schemas/schemas.py   # Pydantic schemas
│   │   └── services/ml/         # ML Forecasting Engine
│   │       ├── forecast_service.py   # Main orchestrator
│   │       ├── models_xgboost.py     # XGBoost implementation
│   │       ├── models_prophet.py     # Prophet implementation
│   │       ├── preprocessing.py      # Data preparation
│   │       ├── insights_service.py   # AI insights (OpenAI)
│   │       └── models_store/         # Trained models (auto-generated)
│   ├── main.py                  # FastAPI app entry
│   ├── sample.csv               # Sample data
│   └── requirements.txt
│
├── dashboard/                   # Streamlit Frontend
│   ├── app.py                   # Dashboard entry
│   └── requirements.txt
│
├── docs/                        # Documentation
│   ├── API_ENDPOINTS.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── TROUBLESHOOTING_FAQ.md
│
├── infra/                       # Infrastructure
│   ├── deployment.md
│   └── env.example
│
├── QUICK_START.md               # This file
└── README.md
```

---

## 🤖 ML Models

| Model | Description | Confidence Intervals |
|-------|-------------|---------------------|
| **XGBoost** | Gradient boosting, faster training | No |
| **Prophet** | Facebook's time-series model | Yes |

Models are automatically trained on first forecast request and cached in `models_store/`.

---

## 📚 Additional Documentation

| Document | Description |
|----------|-------------|
| `docs/API_ENDPOINTS.md` | Full API reference |
| `docs/DEPLOYMENT_CHECKLIST.md` | Production deployment guide |
| `docs/TROUBLESHOOTING_FAQ.md` | Common issues & solutions |
| `backend/CLOUD_RUN_DEPLOY.md` | GCP Cloud Run deployment |
| `dashboard/INTEGRATION_GUIDE.md` | Frontend-backend integration |

---

## 🎯 Next Steps

1. **Add your own data** - Upload CSV with your business metrics
2. **Train models** - System auto-trains on first forecast request
3. **Enable AI Insights** - Set `OPENAI_API_KEY` environment variable
4. **Deploy** - See `docs/DEPLOYMENT_CHECKLIST.md` for production setup

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Production |
| `OPENAI_API_KEY` | OpenAI API key for insights | Optional |
| `BACKEND_API_URL` | Backend URL for frontend | Optional |

For local development, SQLite is used by default (no config needed).

---

*Built with FastAPI, Streamlit, XGBoost, and Prophet*
