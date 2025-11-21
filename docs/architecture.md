# Echolon AI - System Architecture

## Overview
Echolon AI is an enterprise-grade business intelligence platform built on a modern, scalable microservices architecture. It combines FastAPI backend with Streamlit frontend for a seamless user experience.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Streamlit Dashboard (Python)                        │   │
│  │  - Multi-page application                             │   │
│  │  - Real-time data visualization                       │   │
│  │  - User authentication                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            |
                            | HTTPS
                            |
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  REST Endpoints                                      │   │
│  │  - /api/upload_csv                                   │   │
│  │  - /api/insights                                     │   │
│  │  - /api/predictions                                  │   │
│  │  - /api/auth                                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            |
                            |
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services & Models                                   │   │
│  │  - Data Processing                                   │   │
│  │  - Analytics Engine                                  │   │
│  │  - Prediction Pipeline                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            |
                            |
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer (SQLAlchemy ORM)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Models                                     │   │
│  │  - Users                                             │   │
│  │  - BusinessData                                      │   │
│  │  - Metrics                                           │   │
│  │  - Predictions                                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            |
        ┌───────────────────┼───────────────────┐
        |                   |                   |
┌───────────────┐  ┌────────────────┐  ┌──────────────────┐
│  PostgreSQL   │  │ Cloud Storage  │  │ Secret Manager   │
│  Database     │  │ (file uploads) │  │ (credentials)    │
└───────────────┘  └────────────────┘  └──────────────────┘
```

## Core Components

### Frontend (Streamlit Dashboard)
- **Technology**: Python, Streamlit, Plotly
- **Features**:
  - Multi-page navigation
  - Data upload and preview
  - Interactive visualizations
  - Real-time insights display
  - Prediction interface

### Backend API (FastAPI)
- **Technology**: Python, FastAPI, SQLAlchemy
- **Endpoints**:
  - Data Management: Upload, retrieve, delete
  - Analytics: Compute metrics, generate reports
  - Predictions: ML model inference, forecasting
  - Authentication: User management, JWT tokens

### Database
- **Type**: PostgreSQL (relational)
- **ORM**: SQLAlchemy
- **Tables**:
  - users (authentication)
  - business_data (raw data)
  - metrics (computed analytics)
  - predictions (ML outputs)

### External Services
- **Cloud Storage**: GCS for file uploads
- **Secret Manager**: GCP Secret Manager for credentials
- **Monitoring**: Cloud Logging, Cloud Monitoring

## Data Flow

1. **Data Upload**
   - User uploads CSV via dashboard
   - Frontend sends to backend API
   - Backend stores in database and GCS
   - Processing pipeline triggered

2. **Analytics Processing**
   - Data retrieved from database
   - Metrics computed
   - Results cached
   - Visualizations generated

3. **Prediction Generation**
   - ML models loaded
   - Historical data prepared
   - Predictions computed
   - Results stored and returned

## Deployment Architecture

```
GitHub Repository
       |
       | Push to main
       |
 GitHub Actions CI/CD
       |
       ├─> Build Backend Docker Image
       |       |
       |       ├─> Push to GCR
       |       |
       |       └─> Deploy to Cloud Run
       |
       └─> Build Frontend Docker Image
               |
               ├─> Push to GCR
               |
               └─> Deploy to Cloud Run
```

## Security Architecture

- **Authentication**: JWT tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS/SSL for all traffic
- **Secrets Management**: GCP Secret Manager
- **Database Security**: VPC Service Controls
- **API Security**: Rate limiting, input validation

## Scalability Features

- **Horizontal Scaling**: Cloud Run auto-scaling
- **Load Balancing**: Built into Cloud Run
- **Caching**: Redis for session/data caching
- **Database Connection Pooling**: Managed by SQLAlchemy
- **Asynchronous Processing**: Background jobs with Cloud Tasks

## Technologies Stack

| Layer | Technology | Purpose |
|-------|-----------|----------|
| Frontend | Streamlit | Interactive dashboard |
| Backend | FastAPI | REST API framework |
| Database | PostgreSQL | Data persistence |
| ORM | SQLAlchemy | Object-relational mapping |
| Auth | JWT | Token-based authentication |
| Containerization | Docker | Application packaging |
| CI/CD | GitHub Actions | Automated deployment |
| Cloud Platform | Google Cloud Platform | Infrastructure |
| Container Registry | GCR | Docker image storage |
| Runtime | Cloud Run | Serverless compute |

## Performance Considerations

- API response time: < 200ms for 95th percentile
- Database query optimization: Indexed columns
- Frontend load time: < 3 seconds
- Prediction generation: Cached results
- Data upload: Async processing
