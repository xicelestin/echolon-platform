"""FastAPI authentication routes for Echolon AI Platform.

Provides REST API endpoints for:
- User signup/registration
- User login
- Token refresh
- Admin user management
- RBAC verification
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.responses import JSONResponse

from auth import (
    AuthService,
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserRole,
    verify_token,
    TokenPayload,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
auth_service = AuthService()

# ============================================================================
# DEPENDENCY: Get current user from token
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> TokenPayload:
    """Extract and verify JWT from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    return TokenPayload(**payload)

async def require_role(required_role: UserRole):
    """Factory to create RBAC dependency for specific roles."""
    async def check_role(user: TokenPayload = Depends(get_current_user)):
        # Admin can access everything
        if user.role == UserRole.ADMIN.value:
            return user
        
        # Analyst can access non-admin endpoints
        if required_role == UserRole.ANALYST and user.role == UserRole.ANALYST.value:
            return user
        
        # Viewer can only access read-only endpoints (handled in route level)
        if required_role == UserRole.VIEWER and user.role in [UserRole.VIEWER.value, UserRole.ANALYST.value]:
            return user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires {required_role.value} role",
        )
    
    return check_role

# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

@router.post("/signup", response_model=dict)
async def signup(request: SignupRequest):
    """Register a new user.
    
    - **email**: User email address
    - **full_name**: User's full name
    - **password**: Password (min 8 characters)
    - **company_name**: Optional company name
    
    Returns user_id and confirmation message.
    """
    success, user_id, message = auth_service.signup(request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    
    return {
        "user_id": user_id,
        "message": message,
        "status": "success",
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT tokens.
    
    - **email**: User email
    - **password**: User password
    
    Returns access_token, refresh_token, and expiration info.
    """
    success, token_response, message = auth_service.login(request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    
    return token_response

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token from login
    
    Returns new access_token.
    """
    success, access_token, message = auth_service.refresh_access_token(refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "status": "success",
    }

# ============================================================================
# PROTECTED ENDPOINTS (Authentication required)
# ============================================================================

@router.get("/me", response_model=dict)
async def get_current_user_info(
    user: TokenPayload = Depends(get_current_user),
):
    """Get current authenticated user info.
    
    Requires valid JWT token in Authorization header.
    """
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "status": "success",
    }

@router.post("/logout", response_model=dict)
async def logout(
    user: TokenPayload = Depends(get_current_user),
):
    """Logout user (client-side: discard tokens).
    
    In production, you might want to:
    - Blacklist the token
    - Invalidate refresh tokens
    - Log the logout event
    """
    logger.info(f"User {user.email} logged out")
    
    return {
        "message": "Logged out successfully",
        "status": "success",
    }

# ============================================================================
# ADMIN ENDPOINTS (Admin only)
# ============================================================================

@router.get("/admin/users", response_model=dict)
async def list_all_users(
    limit: int = 100,
    offset: int = 0,
    user: TokenPayload = Depends(get_current_user),
):
    """List all users (Admin only).
    
    - **limit**: Number of users to return (default: 100)
    - **offset**: Pagination offset (default: 0)
    """
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list users",
        )
    
    users = auth_service.db.list_users(limit=limit, offset=offset)
    
    return {
        "users": users,
        "count": len(users),
        "status": "success",
    }

@router.put("/admin/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    user: TokenPayload = Depends(get_current_user),
):
    """Update user role (Admin only).
    
    - **user_id**: User ID to update
    - **new_role**: New role (admin, analyst, viewer)
    """
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can modify user roles",
        )
    
    success = auth_service.db.update_user_role(user_id, new_role)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role",
        )
    
    return {
        "user_id": user_id,
        "new_role": new_role.value,
        "message": f"User role updated to {new_role.value}",
        "status": "success",
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for auth service."""
    return {
        "status": "healthy",
        "service": "authentication",
    }

if __name__ == "__main__":
    print("Auth routes registered successfully")
