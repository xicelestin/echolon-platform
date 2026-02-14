"""
Optional Supabase storage for user data and sessions.
When SUPABASE_URL and SUPABASE_KEY are set, use Supabase instead of local files.
Falls back to file-based storage when not configured.
"""
import os
from typing import Optional, Any, Dict


def _get_supabase():
    """Get Supabase client if configured."""
    try:
        import streamlit as st
        url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or st.secrets.get("SUPABASE_KEY")
        if url and key:
            from supabase import create_client
            return create_client(url, key)
    except Exception:
        pass
    return None


def save_user_data_supabase(username: str, data_csv: str, metadata: dict) -> bool:
    """Save user data to Supabase. Returns True if saved."""
    sb = _get_supabase()
    if not sb:
        return False
    try:
        from datetime import datetime, timezone
        sb.table("user_data").upsert({
            "username": username,
            "data_csv": data_csv,
            "metadata": metadata,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="username").execute()
        return True
    except Exception:
        return False


def load_user_data_supabase(username: str) -> Optional[Dict[str, Any]]:
    """Load user data from Supabase. Returns {data_csv, metadata} or None."""
    sb = _get_supabase()
    if not sb:
        return None
    try:
        r = sb.table("user_data").select("*").eq("username", username).execute()
        if r.data and len(r.data) > 0:
            return r.data[0]
    except Exception:
        pass
    return None


def save_session_supabase(token: str, username: str, expiry_ts: float) -> bool:
    """Save session to Supabase."""
    sb = _get_supabase()
    if not sb:
        return False
    try:
        sb.table("sessions").insert({
            "token": token,
            "username": username,
            "expiry": int(expiry_ts),
        }).execute()
        return True
    except Exception:
        return False


def get_session_supabase(token: str) -> Optional[str]:
    """Get username for token from Supabase. Returns None if expired/invalid."""
    sb = _get_supabase()
    if not sb:
        return None
    try:
        import time
        r = sb.table("sessions").select("username, expiry").eq("token", token).execute()
        if r.data and len(r.data) > 0:
            row = r.data[0]
            if row.get("expiry", 0) > time.time():
                return row.get("username")
    except Exception:
        pass
    return None


def delete_session_supabase(token: str) -> bool:
    """Delete session from Supabase."""
    sb = _get_supabase()
    if not sb:
        return False
    try:
        sb.table("sessions").delete().eq("token", token).execute()
        return True
    except Exception:
        return False


def save_subscription_supabase(username: str, tier: str, status: str = "active", stripe_customer_id: str = None, stripe_subscription_id: str = None) -> bool:
    """Save subscription tier for user. Returns True if saved."""
    sb = _get_supabase()
    if not sb:
        return False
    try:
        from datetime import datetime, timezone
        sb.table("subscriptions").upsert({
            "username": username,
            "tier": tier,
            "status": status,
            "stripe_customer_id": stripe_customer_id,
            "stripe_subscription_id": stripe_subscription_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="username").execute()
        return True
    except Exception:
        return False


def get_subscription_supabase(username: str) -> Optional[Dict[str, Any]]:
    """Get subscription for user. Returns {tier, status, ...} or None."""
    sb = _get_supabase()
    if not sb:
        return None
    try:
        r = sb.table("subscriptions").select("*").eq("username", username).execute()
        if r.data and len(r.data) > 0:
            return r.data[0]
    except Exception:
        pass
    return None
