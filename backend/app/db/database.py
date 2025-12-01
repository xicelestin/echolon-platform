import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Optional Google Cloud Secret Manager import
try:
    from google.cloud import secretmanager
    HAS_GCP = True
except ImportError:
    HAS_GCP = False

Base = declarative_base()
SessionLocal = None

def get_db_url():
    """Retrieve database URL from environment or GCP Secret Manager"""
    # Try environment variable first (for local development)
    env_db_url = os.environ.get('DATABASE_URL')
    if env_db_url:
        return env_db_url
    
    # Try GCP Secret Manager if available and credentials are present
    if HAS_GCP:
        try:
            client = secretmanager.SecretManagerServiceClient()
            project_id = os.environ.get('GCP_PROJECT_ID')
            secret_name = os.environ.get('DB_SECRET_NAME', 'DB_CONNECTION_STRING')
            
            if project_id:
                name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                response = client.access_secret_version(name=name)
                return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error retrieving database URL from Secret Manager: {e}")
    
    # Fallback to SQLite for local development
    print("Using SQLite database for local development")
    return 'sqlite:///./echolon.db'

def init_engine():
    """Initialize SQLAlchemy engine and session"""
    db_url = get_db_url()
    
    # If using PostgreSQL but psycopg2 is not available, fall back to SQLite
    if db_url.startswith('postgresql://') or db_url.startswith('postgresql+psycopg2://'):
        try:
            import psycopg2
        except ImportError:
            print("PostgreSQL driver (psycopg2) not found. Falling back to SQLite for local development.")
            db_url = 'sqlite:///./echolon.db'
    
    # Configure engine based on database type
    if db_url.startswith('sqlite'):
        # SQLite-specific configuration
        engine = sa.create_engine(
            db_url,
            connect_args={"check_same_thread": False},  # SQLite requires this
            pool_pre_ping=True
        )
    else:
        # PostgreSQL/other database configuration
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
