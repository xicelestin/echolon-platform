"""
Background sync utilities - sync connected sources when data is stale.

Used for "sync on visit": when user opens the dashboard, auto-sync if last sync
was more than STALE_HOURS ago. No backend required - runs in Streamlit.
"""
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional

# Sync when data is older than this
STALE_HOURS = 6


def _parse_last_sync(last_sync: str) -> Optional[datetime]:
    """Parse last_sync string to datetime."""
    if not last_sync:
        return None
    try:
        return datetime.strptime(last_sync, "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return None


def is_source_stale(source_key: str) -> bool:
    """Check if a connected source's data is stale (> STALE_HOURS old)."""
    connected = st.session_state.get("connected_sources", {})
    if source_key not in connected:
        return False
    last = connected[source_key].get("last_sync")
    parsed = _parse_last_sync(last)
    if parsed is None:
        return True  # Never synced
    return datetime.now() - parsed > timedelta(hours=STALE_HOURS)


def get_sources_needing_sync() -> List[str]:
    """Return list of connected sources that are stale and have credentials."""
    connected = st.session_state.get("connected_sources", {})
    needing = []
    for source_key in connected:
        if not is_source_stale(source_key):
            continue
        # Only auto-sync sources we have credentials for (Stripe has persisted api_key)
        if source_key == "stripe" and st.session_state.get("api_keys", {}).get("stripe"):
            needing.append(source_key)
        # CSV is manual - no auto-sync
        # Shopify, QuickBooks, Google Sheets need OAuth - skip for now
    return needing


def get_syncable_sources() -> List[str]:
    """Return all connected sources that can be synced (have credentials). For manual Sync Now."""
    connected = st.session_state.get("connected_sources", {})
    syncable = []
    for source_key in connected:
        if source_key == "stripe" and st.session_state.get("api_keys", {}).get("stripe"):
            syncable.append(source_key)
    return syncable


def sync_source_quiet(source_key: str) -> bool:
    """
    Sync a source without UI feedback or rerun. Returns True if successful.
    Used for auto-sync on app load.
    """
    from data_source_apis import fetch_data_from_api
    from auth import get_current_user
    from utils.user_data_storage import save_user_data

    connected = st.session_state.get("connected_sources", {})
    if source_key not in connected:
        return False

    credentials = {}
    if source_key == "stripe":
        key = st.session_state.get("api_keys", {}).get("stripe")
        if not key:
            return False
        credentials = {"api_key": key}

    try:
        data_df = fetch_data_from_api(source_key, credentials, silent=True)
        if data_df is not None and not data_df.empty:
            st.session_state.uploaded_data = data_df
            st.session_state.connected_sources[source_key]["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_user_data(get_current_user())
            return True
    except Exception:
        pass
    return False


def sync_all_if_stale() -> None:
    """
    Sync all stale connected sources. Call at app load.
    Runs quietly - no spinners or reruns.
    """
    for source_key in get_sources_needing_sync():
        sync_source_quiet(source_key)


def get_most_recent_sync() -> Optional[str]:
    """Return the most recent last_sync across all connected sources."""
    connected = st.session_state.get("connected_sources", {})
    most_recent_dt: Optional[datetime] = None
    for info in connected.values():
        last = info.get("last_sync")
        if not last:
            continue
        parsed = _parse_last_sync(last)
        if parsed and (most_recent_dt is None or parsed > most_recent_dt):
            most_recent_dt = parsed
    return most_recent_dt.strftime("%Y-%m-%d %H:%M") if most_recent_dt else None


def format_last_sync_ago(last_sync: str) -> str:
    """Format last_sync as 'X hours ago' or 'X minutes ago'."""
    parsed = _parse_last_sync(last_sync)
    if parsed is None:
        return "Never"
    delta = datetime.now() - parsed
    if delta.total_seconds() < 60:
        return "Just now"
    if delta.total_seconds() < 3600:
        mins = int(delta.total_seconds() / 60)
        return f"{mins} min ago"
    if delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f"{hours} hr ago"
    days = int(delta.total_seconds() / 86400)
    return f"{days} days ago"
