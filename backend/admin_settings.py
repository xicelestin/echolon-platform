"""Admin settings and configuration management for Echolon AI Platform.

Handles:
- Data source connections (API keys, credentials)
- User management and role assignments
- Organization settings
- Feature flags and configurations
- Audit logging for admin actions
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum

import psycopg2
from psycopg2 import sql
from cryptography.fernet import Fernet
import json

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Encryption key for sensitive credentials (load from env in production)
ENCRYPTION_KEY = os.getenv("ADMIN_ENCRYPTION_KEY", "dev-key-change-in-production").encode()
cipher = Fernet(ENCRYPTION_KEY if len(ENCRYPTION_KEY) == 32 else Fernet.generate_key())

# ============================================================================
# ENUMS
# ============================================================================

class DataSourceType(str, Enum):
    """Supported data source types."""
    STRIPE = "stripe"
    SHOPIFY = "shopify"
    GOOGLE_SHEETS = "google_sheets"
    SQL_DATABASE = "sql_database"
    API = "api"
    CSV_UPLOAD = "csv_upload"

class AdminActionType(str, Enum):
    """Types of admin actions for audit logging."""
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    ROLE_UPDATED = "role_updated"
    DATASOURCE_ADDED = "datasource_added"
    DATASOURCE_REMOVED = "datasource_removed"
    CONFIG_CHANGED = "config_changed"
    API_KEY_GENERATED = "api_key_generated"
    API_KEY_REVOKED = "api_key_revoked"

# ============================================================================
# MODELS
# ============================================================================

class DataSourceConfig:
    """Data source configuration model."""
    
    def __init__(
        self,
        source_id: str,
        source_type: DataSourceType,
        name: str,
        credentials: Dict,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ):
        self.source_id = source_id
        self.source_type = source_type
        self.name = name
        self.credentials = credentials
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

class APIKey:
    """API key model for third-party integrations."""
    
    def __init__(
        self,
        key_id: str,
        user_id: str,
        key_hash: str,
        name: str,
        permissions: List[str],
        last_used: Optional[datetime] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
    ):
        self.key_id = key_id
        self.user_id = user_id
        self.key_hash = key_hash
        self.name = name
        self.permissions = permissions
        self.last_used = last_used
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()

# ============================================================================
# ADMIN SETTINGS DATABASE OPERATIONS
# ============================================================================

class AdminSettingsDB:
    """Admin settings database operations."""
    
    def __init__(self):
        self.conn_str = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/echolon"
        )
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.conn_str)
    
    def _encrypt_credentials(self, credentials: Dict) -> str:
        """Encrypt credentials for storage."""
        json_str = json.dumps(credentials)
        encrypted = cipher.encrypt(json_str.encode())
        return encrypted.decode()
    
    def _decrypt_credentials(self, encrypted: str) -> Dict:
        """Decrypt credentials from storage."""
        decrypted = cipher.decrypt(encrypted.encode())
        return json.loads(decrypted.decode())
    
    # ========== DATA SOURCE OPERATIONS ==========
    
    def add_data_source(
        self,
        user_id: str,
        source_type: DataSourceType,
        name: str,
        credentials: Dict,
    ) -> Optional[str]:
        """Add new data source connection."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            source_id = f"src_{datetime.utcnow().timestamp()}"
            encrypted_creds = self._encrypt_credentials(credentials)
            
            cur.execute(
                sql.SQL("""
                    INSERT INTO data_sources
                    (source_id, user_id, source_type, name, encrypted_credentials, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """),
                (source_id, user_id, source_type.value, name, encrypted_creds, True, datetime.utcnow())
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Data source {name} ({source_type.value}) added by user {user_id}")
            self._log_admin_action(user_id, AdminActionType.DATASOURCE_ADDED, {"source_id": source_id})
            return source_id
        
        except Exception as e:
            logger.error(f"Error adding data source: {e}")
            return None
    
    def get_data_sources(self, user_id: str) -> List[Dict]:
        """Get all data sources for a user."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    SELECT source_id, source_type, name, is_active, created_at
                    FROM data_sources
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """),
                (user_id,)
            )
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            return [
                {
                    "source_id": r[0],
                    "source_type": r[1],
                    "name": r[2],
                    "is_active": r[3],
                    "created_at": str(r[4]),
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Error fetching data sources: {e}")
            return []
    
    def remove_data_source(self, source_id: str, user_id: str) -> bool:
        """Remove data source connection."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("DELETE FROM data_sources WHERE source_id = %s AND user_id = %s"),
                (source_id, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Data source {source_id} removed by user {user_id}")
            self._log_admin_action(user_id, AdminActionType.DATASOURCE_REMOVED, {"source_id": source_id})
            return True
        
        except Exception as e:
            logger.error(f"Error removing data source: {e}")
            return False
    
    # ========== API KEY OPERATIONS ==========
    
    def generate_api_key(
        self,
        user_id: str,
        name: str,
        permissions: List[str],
    ) -> Optional[str]:
        """Generate new API key for user."""
        try:
            import secrets
            import hashlib
            
            # Generate random key
            raw_key = secrets.token_urlsafe(32)
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            
            conn = self._get_connection()
            cur = conn.cursor()
            
            key_id = f"key_{datetime.utcnow().timestamp()}"
            
            cur.execute(
                sql.SQL("""
                    INSERT INTO api_keys
                    (key_id, user_id, key_hash, name, permissions, is_active, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """),
                (key_id, user_id, key_hash, name, json.dumps(permissions), True, datetime.utcnow())
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"API key generated for user {user_id}")
            self._log_admin_action(user_id, AdminActionType.API_KEY_GENERATED, {"key_id": key_id})
            
            # Return the full key only once
            return f"{key_id}.{raw_key}"
        
        except Exception as e:
            logger.error(f"Error generating API key: {e}")
            return None
    
    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke API key."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("UPDATE api_keys SET is_active = FALSE WHERE key_id = %s AND user_id = %s"),
                (key_id, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"API key {key_id} revoked for user {user_id}")
            self._log_admin_action(user_id, AdminActionType.API_KEY_REVOKED, {"key_id": key_id})
            return True
        
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False
    
    def list_api_keys(self, user_id: str) -> List[Dict]:
        """List all API keys for user."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    SELECT key_id, name, permissions, is_active, last_used, created_at
                    FROM api_keys
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """),
                (user_id,)
            )
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            return [
                {
                    "key_id": r[0],
                    "name": r[1],
                    "permissions": json.loads(r[2]) if r[2] else [],
                    "is_active": r[3],
                    "last_used": str(r[4]) if r[4] else None,
                    "created_at": str(r[5]),
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []
    
    # ========== AUDIT LOGGING ==========
    
    def _log_admin_action(
        self,
        user_id: str,
        action: AdminActionType,
        details: Dict,
    ) -> None:
        """Log admin action for audit trail."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    INSERT INTO audit_logs
                    (user_id, action, details, timestamp)
                    VALUES (%s, %s, %s, %s)
                """),
                (user_id, action.value, json.dumps(details), datetime.utcnow())
            )
            conn.commit()
            cur.close()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error logging admin action: {e}")
    
    def get_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict]:
        """Get audit logs."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    SELECT user_id, action, details, timestamp
                    FROM audit_logs
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                """),
                (limit, offset)
            )
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            return [
                {
                    "user_id": r[0],
                    "action": r[1],
                    "details": json.loads(r[2]) if r[2] else {},
                    "timestamp": str(r[3]),
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            return []

if __name__ == "__main__":
    print("Admin settings module loaded successfully")
