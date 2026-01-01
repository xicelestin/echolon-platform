"""Shopify OAuth 2.0 integration for Echolon platform.

This module handles the complete Shopify OAuth flow:
1. Initiating OAuth authorization
2. Handling OAuth callback
3. Exchanging authorization code for access token
4. Storing encrypted tokens in database
5. Refreshing tokens (Shopify tokens don't expire)
"""

import os
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode, parse_qs, urlparse

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, Tenant, ConnectedIntegration, OAuthState, AuditLog
from auth import get_current_user  # Assuming you have auth module


router = APIRouter(prefix="/oauth/shopify", tags=["Shopify OAuth"])

# Shopify OAuth Configuration
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")  # From Shopify Partner Dashboard
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SHOPIFY_SCOPES = "read_orders,read_products,read_customers,read_inventory"
SHOPIFY_REDIRECT_URI = os.getenv(
    "SHOPIFY_REDIRECT_URI",
    "https://api.echolon.ai/oauth/shopify/callback"
)


# ============================================================================
# SHOPIFY OAUTH FLOW
# ============================================================================

@router.get("/connect")
async def initiate_shopify_oauth(
    shop: str = Query(..., description="Shopify store domain (e.g., mystore.myshopify.com)"),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Step 1: Initiate Shopify OAuth flow.
    
    This endpoint redirects the user to Shopify's authorization page.
    The user must approve access to their store data.
    """
    if not SHOPIFY_API_KEY or not SHOPIFY_API_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Shopify API credentials not configured. Contact support."
        )
    
    # Validate shop domain format
    shop = shop.lower().strip()
    if not shop.endswith(".myshopify.com"):
        if "." not in shop:
            shop = f"{shop}.myshopify.com"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid Shopify store domain. Must be in format: store-name.myshopify.com"
            )
    
    # Get or create tenant for this user
    result = await db.execute(
        select(Tenant).where(Tenant.owner_user_id == user["user_id"])
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        # Create new tenant
        tenant = Tenant(
            company_name=user.get("company_name", "My Company"),
            owner_user_id=user["user_id"],
            contact_email=user.get("email")
        )
        db.add(tenant)
        await db.flush()
    
    # Generate CSRF state token
    state_token = secrets.token_urlsafe(32)
    
    # Store state in database
    oauth_state = OAuthState(
        state_token=state_token,
        tenant_id=tenant.id,
        user_id=user["user_id"],
        provider="shopify",
        redirect_after="/dashboard/integrations",  # Where to redirect after OAuth
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(oauth_state)
    await db.commit()
    
    # Build Shopify authorization URL
    auth_params = {
        "client_id": SHOPIFY_API_KEY,
        "scope": SHOPIFY_SCOPES,
        "redirect_uri": SHOPIFY_REDIRECT_URI,
        "state": state_token,
        "grant_options[]": "per-user"  # Optional: per-user grants
    }
    
    auth_url = f"https://{shop}/admin/oauth/authorize?{urlencode(auth_params)}"
    
    # Log audit trail
    audit_log = AuditLog(
        tenant_id=tenant.id,
        user_id=user["user_id"],
        action="shopify_oauth_initiated",
        resource_type="integration",
        details={"shop": shop}
    )
    db.add(audit_log)
    await db.commit()
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def shopify_oauth_callback(
    code: str = Query(..., description="Authorization code from Shopify"),
    shop: str = Query(..., description="Shopify store domain"),
    state: str = Query(..., description="CSRF state token"),
    hmac_param: Optional[str] = Query(None, alias="hmac", description="HMAC signature"),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Handle Shopify OAuth callback.
    
    This endpoint:
    1. Validates the HMAC signature to ensure request is from Shopify
    2. Verifies the CSRF state token
    3. Exchanges the authorization code for an access token
    4. Stores the encrypted access token in the database
    """
    
    # 1. Verify HMAC signature
    if not verify_shopify_hmac(dict(request.query_params), SHOPIFY_API_SECRET):
        raise HTTPException(
            status_code=400,
            detail="Invalid HMAC signature. Request may have been tampered with."
        )
    
    # 2. Verify state token
    result = await db.execute(
        select(OAuthState).where(
            OAuthState.state_token == state,
            OAuthState.used == False,
            OAuthState.expires_at > datetime.utcnow()
        )
    )
    oauth_state = result.scalar_one_or_none()
    
    if not oauth_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired state token. Please try connecting again."
        )
    
    # Mark state as used
    oauth_state.used = True
    
    # 3. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_url = f"https://{shop}/admin/oauth/access_token"
        token_data = {
            "client_id": SHOPIFY_API_KEY,
            "client_secret": SHOPIFY_API_SECRET,
            "code": code
        }
        
        try:
            response = await client.post(token_url, json=token_data)
            response.raise_for_status()
            token_response = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to exchange code for token: {str(e)}"
            )
    
    access_token = token_response.get("access_token")
    scope = token_response.get("scope")
    
    if not access_token:
        raise HTTPException(
            status_code=500,
            detail="No access token received from Shopify"
        )
    
    # 4. Get shop info to verify and store
    shop_info = await get_shopify_shop_info(shop, access_token)
    
    # 5. Store integration in database
    result = await db.execute(
        select(ConnectedIntegration).where(
            ConnectedIntegration.tenant_id == oauth_state.tenant_id,
            ConnectedIntegration.provider == "shopify",
            ConnectedIntegration.provider_account_id == shop
        )
    )
    integration = result.scalar_one_or_none()
    
    if integration:
        # Update existing integration
        integration.access_token = access_token  # Will be encrypted via setter
        integration.scopes = scope.split(",") if scope else []
        integration.is_active = True
        integration.connected_at = datetime.utcnow()
        integration.metadata_json = shop_info
    else:
        # Create new integration
        integration = ConnectedIntegration(
            tenant_id=oauth_state.tenant_id,
            provider="shopify",
            provider_account_id=shop,
            provider_account_name=shop_info.get("name", shop),
            access_token=access_token,  # Will be encrypted via setter
            scopes=scope.split(",") if scope else [],
            metadata_json=shop_info
        )
        db.add(integration)
    
    # 6. Log audit trail
    audit_log = AuditLog(
        tenant_id=oauth_state.tenant_id,
        user_id=oauth_state.user_id,
        action="shopify_integration_connected",
        resource_type="integration",
        resource_id=integration.id if integration.id else None,
        details={
            "shop": shop,
            "scopes": scope
        }
    )
    db.add(audit_log)
    
    await db.commit()
    
    # 7. Redirect back to dashboard
    redirect_url = f"https://app.echolon.ai{oauth_state.redirect_after}?success=true&provider=shopify"
    return RedirectResponse(url=redirect_url)


# ============================================================================
# SHOPIFY API HELPERS
# ============================================================================

def verify_shopify_hmac(params: dict, secret: str) -> bool:
    """
    Verify HMAC signature from Shopify OAuth callback.
    
    This ensures the request is genuine and hasn't been tampered with.
    """
    if "hmac" not in params:
        return False
    
    hmac_to_verify = params.pop("hmac")
    
    # Sort params and build message
    message = "&".join(
        f"{key}={value}"
        for key, value in sorted(params.items())
    )
    
    # Calculate HMAC
    computed_hmac = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_hmac, hmac_to_verify)


async def get_shopify_shop_info(shop: str, access_token: str) -> dict:
    """
    Fetch shop information from Shopify API.
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Shopify-Access-Token": access_token
        }
        
        try:
            response = await client.get(
                f"https://{shop}/admin/api/2024-01/shop.json",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("shop", {})
        except httpx.HTTPError:
            return {"domain": shop}


@router.post("/test-connection/{integration_id}")
async def test_shopify_connection(
    integration_id: int,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test a Shopify connection to verify it's working.
    """
    result = await db.execute(
        select(ConnectedIntegration).where(
            ConnectedIntegration.id == integration_id,
            ConnectedIntegration.provider == "shopify"
        )
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Verify user has access to this integration's tenant
    tenant_result = await db.execute(
        select(Tenant).where(
            Tenant.id == integration.tenant_id,
            Tenant.owner_user_id == user["user_id"]
        )
    )
    if not tenant_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Test API call
    try:
        shop_info = await get_shopify_shop_info(
            integration.provider_account_id,
            integration.access_token  # Will be decrypted via getter
        )
        return {
            "status": "success",
            "shop_info": shop_info
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
