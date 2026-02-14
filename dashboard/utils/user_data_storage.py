"""
Persistent user data storage - keeps uploaded data and preferences tied to each account.

Data is stored per username in local files. When a user logs in, their data is loaded.
When they upload data or change preferences, it's saved. Data persists across logouts.
"""
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st


def _sanitize_username(username: str) -> str:
    """Convert username to safe filesystem path (no slashes, special chars)."""
    if not username:
        return "anonymous"
    safe = re.sub(r'[^\w\-.]', '_', str(username).lower())
    return safe[:64] or "anonymous"


def _get_user_data_dir(username: str) -> Path:
    """Get the directory for a user's stored data."""
    base = Path(__file__).resolve().parent.parent / "data" / "user_data"
    user_dir = base / _sanitize_username(username)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def save_user_data(username: str) -> bool:
    """
    Save current session state. Uses Supabase if configured, else local files.
    Persists: uploaded_data, connected_sources, upload_history, goals, preferences.
    """
    if not username:
        return False
    metadata = {
        "connected_sources": st.session_state.get("connected_sources", {}),
        "upload_history": st.session_state.get("upload_history", []),
        "goals": st.session_state.get("goals"),
        "industry": st.session_state.get("industry", "ecommerce"),
        "company_name": st.session_state.get("company_name", "Your Business"),
        "date_range": st.session_state.get("date_range", "Last 90 Days"),
        "api_keys": st.session_state.get("api_keys", {}),
        "uploaded_data_provided_columns": st.session_state.get("uploaded_data_provided_columns", []),
    }
    df = st.session_state.get("uploaded_data")
    data_csv = df.to_csv(index=False) if df is not None and not df.empty else ""
    try:
        from .supabase_storage import save_user_data_supabase
        meta_safe = {k: v for k, v in metadata.items() if k != "api_keys"}
        if save_user_data_supabase(username, data_csv, meta_safe):
            pass
    except Exception:
        pass
    try:
        user_dir = _get_user_data_dir(username)
        if df is not None and not df.empty:
            (user_dir / "data.csv").write_text(df.to_csv(index=False))
        else:
            path = user_dir / "data.csv"
            if path.exists():
                path.unlink()
        (user_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        return True
    except Exception as e:
        st.warning(f"Could not save data: {e}")
        return False


def load_user_data(username: str) -> bool:
    """
    Load stored data for the given user into session state.
    Tries Supabase first if configured, else local files.
    Returns True if data was loaded, False if none existed.
    """
    if not username:
        return False
    try:
        from .supabase_storage import load_user_data_supabase
        row = load_user_data_supabase(username)
        if row and row.get("data_csv"):
            from io import StringIO
            df = pd.read_csv(StringIO(row["data_csv"]))
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            st.session_state.uploaded_data = df
            meta = row.get("metadata") or {}
            _apply_metadata(meta)
            return True
    except Exception:
        pass
    try:
        user_dir = _get_user_data_dir(username)
        path = user_dir / "data.csv"
        if path.exists():
            df = pd.read_csv(path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            st.session_state.uploaded_data = df
            meta_path = user_dir / "metadata.json"
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                _apply_metadata(meta)
            return True
    except Exception as e:
        st.warning(f"Could not load saved data: {e}")
    return False


def _apply_metadata(meta: dict) -> None:
    """Apply metadata dict to session state."""
    st.session_state.connected_sources = meta.get("connected_sources", {})
    st.session_state.upload_history = meta.get("upload_history", [])
    if meta.get("goals"):
        st.session_state.goals = meta["goals"]
    if meta.get("industry"):
        st.session_state.industry = meta["industry"]
    if meta.get("company_name"):
        st.session_state.company_name = meta["company_name"]
    if meta.get("date_range"):
        st.session_state.date_range = meta["date_range"]
    if meta.get("api_keys"):
        st.session_state.api_keys = meta["api_keys"]
    provided = meta.get("uploaded_data_provided_columns")
    st.session_state.uploaded_data_provided_columns = (
        provided if provided is not None else ["date", "revenue", "orders", "customers"]
    )


def has_stored_data(username: str) -> bool:
    """Check if the user has any stored data."""
    if not username:
        return False
    user_dir = _get_user_data_dir(username)
    return (user_dir / "data.csv").exists()
