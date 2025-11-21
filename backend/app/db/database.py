import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from google.cloud import secretmanager
import os

Base = declarative_base()
SessionLocal = None

def get_db_url():
    """Retrieve database URL from GCP Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.environ.get('GCP_PROJECT_ID')
        secret_name = os.environ.get('DB_SECRET_NAME', 'DB_CONNECTION_STRING')
        
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error retrieving database URL from Secret Manager: {e}")
        # Fallback for local development
        return os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/echolon')

def init_engine():
    """Initialize SQLAlchemy engine and session"""
    db_url = get_db_url()
    engine = sa.create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

# Initialize engine on module import
engine = init_engine()

def get_db():
    """Dependency for FastAPI routes to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
