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
    Save current session state to disk for the given user.
    Persists: uploaded_data, connected_sources, upload_history, goals, preferences.
    """
    if not username:
        return False
    try:
        user_dir = _get_user_data_dir(username)

        # Save main data (DataFrame) - use CSV for portability (no extra deps)
        df = st.session_state.get("uploaded_data")
        if df is not None and not df.empty:
            path = user_dir / "data.csv"
            df.to_csv(path, index=False)
        else:
            path = user_dir / "data.csv"
            if path.exists():
                path.unlink()

        # Save metadata (JSON-serializable)
        # api_keys: persisted per-user for Stripe etc. (stored locally, not in git)
        metadata = {
            "connected_sources": st.session_state.get("connected_sources", {}),
            "upload_history": st.session_state.get("upload_history", []),
            "goals": st.session_state.get("goals"),
            "industry": st.session_state.get("industry", "ecommerce"),
            "company_name": st.session_state.get("company_name", "Your Business"),
            "date_range": st.session_state.get("date_range", "Last 90 Days"),
            "api_keys": st.session_state.get("api_keys", {}),
        }
        meta_path = user_dir / "metadata.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return True
    except Exception as e:
        st.warning(f"Could not save data: {e}")
        return False


def load_user_data(username: str) -> bool:
    """
    Load stored data for the given user into session state.
    Returns True if data was loaded, False if none existed.
    """
    if not username:
        return False
    try:
        user_dir = _get_user_data_dir(username)

        # Load main data
        path = user_dir / "data.csv"
        if path.exists():
            df = pd.read_csv(path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            st.session_state.uploaded_data = df
        else:
            return False

        # Load metadata
        meta_path = user_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
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

        return True
    except Exception as e:
        st.warning(f"Could not load saved data: {e}")
        return False


def has_stored_data(username: str) -> bool:
    """Check if the user has any stored data."""
    if not username:
        return False
    user_dir = _get_user_data_dir(username)
    return (user_dir / "data.csv").exists()
