"""Authentication module for Echolon AI Platform.

Handles user authentication, JWT tokens, role-based access control (RBAC),
and session management.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
import psycopg2
from psycopg2 import sql

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS & MODELS
# ============================================================================

class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class SignupRequest(BaseModel):
    """Signup request model."""
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)
    company_name: str = ""

class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User response model (safe, no password)."""
    user_id: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: str
    company_name: str

class TokenPayload(BaseModel):
    """JWT token payload."""
    user_id: str
    email: str
    role: UserRole
    exp: int
    iat: int

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_access_token(user_id: str, email: str, role: UserRole) -> str:
    """Create JWT access token."""
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token (longer-lived)."""
    now = datetime.utcnow()
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class UserDB:
    """User database operations."""
    
    def __init__(self):
        self.conn_str = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/echolon"
        )
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.conn_str)
    
    def create_user(self, email: str, password: str, full_name: str,
                   company_name: str = "", role: UserRole = UserRole.VIEWER) -> Optional[str]:
        """Create new user in database."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Check if user exists
            cur.execute(
                sql.SQL("SELECT user_id FROM users WHERE email = %s"),
                (email,)
            )
            if cur.fetchone():
                logger.error(f"User {email} already exists")
                return None
            
            # Create new user
            user_id = f"user_{datetime.utcnow().timestamp()}"
            hashed_pwd = hash_password(password)
            
            cur.execute(
                sql.SQL("""
                    INSERT INTO users 
                    (user_id, email, password_hash, full_name, role, status, company_name, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """),
                (user_id, email, hashed_pwd, full_name, role.value, UserStatus.ACTIVE.value, company_name, datetime.utcnow())
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"User {email} created successfully")
            return user_id
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    SELECT user_id, email, password_hash, full_name, role, status, company_name, created_at
                    FROM users WHERE email = %s
                """),
                (email,)
            )
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if not result:
                return None
            
            return {
                "user_id": result[0],
                "email": result[1],
                "password_hash": result[2],
                "full_name": result[3],
                "role": result[4],
                "status": result[5],
                "company_name": result[6],
                "created_at": result[7]
            }
        
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role (admin only)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("UPDATE users SET role = %s WHERE user_id = %s"),
                (new_role.value, user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"User {user_id} role updated to {new_role.value}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False
    
    def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all users (admin only)."""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute(
                sql.SQL("""
                    SELECT user_id, email, full_name, role, status, company_name, created_at
                    FROM users
                    ORDER BY created_at DESC
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
                    "email": r[1],
                    "full_name": r[2],
                    "role": r[3],
                    "status": r[4],
                    "company_name": r[5],
                    "created_at": str(r[6])
                }
                for r in results
            ]
        
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

# ============================================================================
# AUTHENTICATION SERVICE
# ============================================================================

class AuthService:
    """High-level authentication service."""
    
    def __init__(self):
        self.db = UserDB()
    
    def signup(self, request: SignupRequest) -> tuple[bool, Optional[str], str]:
        """Register new user."""
        # Validate password strength
        if len(request.password) < 8:
            return False, None, "Password must be at least 8 characters"
        
        # Create user
        user_id = self.db.create_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            company_name=request.company_name,
            role=UserRole.VIEWER  # Default role
        )
        
        if not user_id:
            return False, None, "Failed to create user (may already exist)"
        
        return True, user_id, "User created successfully"
    
    def login(self, request: LoginRequest) -> tuple[bool, Optional[TokenResponse], str]:
        """Authenticate user and return tokens."""
        # Get user from database
        user = self.db.get_user(request.email)
        
        if not user:
            return False, None, "Invalid email or password"
        
        # Check status
        if user["status"] != UserStatus.ACTIVE.value:
            return False, None, "User account is not active"
        
        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            return False, None, "Invalid email or password"
        
        # Create tokens
        access_token = create_access_token(
            user_id=user["user_id"],
            email=user["email"],
            role=UserRole(user["role"])
        )
        refresh_token = create_refresh_token(user_id=user["user_id"])
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        logger.info(f"User {request.email} logged in successfully")
        return True, token_response, "Login successful"
    
    def refresh_access_token(self, refresh_token: str) -> tuple[bool, Optional[str], str]:
        """Create new access token from refresh token."""
        payload = verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return False, None, "Invalid refresh token"
        
        user_id = payload["user_id"]
        # In production, fetch user from DB to verify status
        # For now, just create new token
        
        # Note: We need user email and role, would need to fetch from DB
        # This is a simplified version
        return True, None, "Refresh token valid (need to fetch user details)"

if __name__ == "__main__":
    print("Auth module loaded successfully")
