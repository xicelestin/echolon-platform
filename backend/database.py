"""Database connection and ORM models for multi-tenant OAuth system."""

import os
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, ARRAY, JSON,
    ForeignKey, UniqueConstraint, CheckConstraint, Index, func
)
from datetime import datetime
import uuid

from cryptography.fernet import Fernet
import base64


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://echolon:password@localhost:5432/echolon_db"
)

# For Heroku/Cloud SQL, convert postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Encryption key for OAuth tokens (store in environment variable)
ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key if not set (WARNING: This should be persistent in production)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: Generated temporary encryption key. Set TOKEN_ENCRYPTION_KEY env var in production.")

cipher = Fernet(ENCRYPTION_KEY.encode())


# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Test connections before using
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ============================================================================
# ENCRYPTION UTILITIES
# ============================================================================

def encrypt_token(token: str) -> str:
    """Encrypt an OAuth token for storage."""
    if not token:
        return token
    encrypted = cipher.encrypt(token.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an OAuth token for use."""
    if not encrypted_token:
        return encrypted_token
    encrypted = base64.urlsafe_b64decode(encrypted_token.encode())
    return cipher.decrypt(encrypted).decode()


# ============================================================================
# ORM MODELS
# ============================================================================

class Tenant(Base):
    """Organization/Company using Echolon."""
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_uuid: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_tier: Mapped[str] = mapped_column(String(50), default="free")
    
    # PropelAuth or Auth0 user ID
    owner_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    integrations: Mapped[list["ConnectedIntegration"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_tenants_uuid", "tenant_uuid"),
        Index("idx_tenants_owner", "owner_user_id"),
    )


class ConnectedIntegration(Base):
    """OAuth tokens for external services per tenant."""
    __tablename__ = "connected_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    # Provider info
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # shopify, quickbooks, stripe, google_sheets
    provider_account_id: Mapped[Optional[str]] = mapped_column(String(255))
    provider_account_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # OAuth tokens (encrypted)
    _access_token: Mapped[str] = mapped_column("access_token", Text, nullable=False)
    _refresh_token: Mapped[Optional[str]] = mapped_column("refresh_token", Text)
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer")
    scopes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Connection metadata
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sync_status: Mapped[str] = mapped_column(String(50), default="pending")
    sync_error: Mapped[Optional[str]] = mapped_column(Text)
    
    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="integrations")
    sync_jobs: Mapped[list["SyncJob"]] = relationship(
        back_populates="integration",
        cascade="all, delete-orphan"
    )
    
    # Property accessors for encrypted tokens
    @property
    def access_token(self) -> str:
        """Get decrypted access token."""
        return decrypt_token(self._access_token) if self._access_token else ""
    
    @access_token.setter
    def access_token(self, value: str):
        """Set and encrypt access token."""
        self._access_token = encrypt_token(value) if value else ""
    
    @property
    def refresh_token(self) -> Optional[str]:
        """Get decrypted refresh token."""
        return decrypt_token(self._refresh_token) if self._refresh_token else None
    
    @refresh_token.setter
    def refresh_token(self, value: Optional[str]):
        """Set and encrypt refresh token."""
        self._refresh_token = encrypt_token(value) if value else None
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "provider", "provider_account_id", name="unique_tenant_provider"),
        Index("idx_integrations_tenant", "tenant_id"),
        Index("idx_integrations_provider", "provider"),
        Index("idx_integrations_active", "tenant_id", "is_active"),
    )


class SyncJob(Base):
    """Background data synchronization jobs."""
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    integration_id: Mapped[int] = mapped_column(ForeignKey("connected_integrations.id", ondelete="CASCADE"), nullable=False)
    
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)  # full_sync, incremental, manual
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)
    sync_params: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Relationships
    integration: Mapped["ConnectedIntegration"] = relationship(back_populates="sync_jobs")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
            name="valid_status"
        ),
        Index("idx_sync_jobs_integration", "integration_id"),
        Index("idx_sync_jobs_status", "status", "started_at"),
    )


class OAuthState(Base):
    """Temporary OAuth state for CSRF protection."""
    __tablename__ = "oauth_states"

    state_token: Mapped[str] = mapped_column(String(255), primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    redirect_after: Mapped[Optional[str]] = mapped_column(String(500))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (
        Index("idx_oauth_states_expiry", "expires_at"),
    )


class AuditLog(Base):
    """Security audit trail."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tenants.id", ondelete="SET NULL"))
    user_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[int]] = mapped_column(Integer)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 max length
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    details: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_audit_logs_tenant", "tenant_id", "created_at"),
        Index("idx_audit_logs_user", "user_id", "created_at"),
    )


# ============================================================================
# DATABASE SESSION DEPENDENCY
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    print("Database connections closed.")
