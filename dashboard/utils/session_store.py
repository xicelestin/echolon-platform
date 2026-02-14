"""
Persistent session store - keeps users logged in across page refreshes.

Uses a file-based token store. On login, a session token is generated and stored.
The token is passed via query params so it survives refresh. On logout, the token is removed.
"""
import json
import secrets
import time
from pathlib import Path
from typing import Optional

# Sessions expire after 7 days
SESSION_EXPIRY_DAYS = 7


def _get_sessions_path() -> Path:
    """Path to sessions file."""
    base = Path(__file__).resolve().parent.parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "sessions.json"


def _load_sessions() -> dict:
    """Load sessions from file."""
    path = _get_sessions_path()
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_sessions(sessions: dict) -> None:
    """Save sessions to file."""
    path = _get_sessions_path()
    with open(path, "w") as f:
        json.dump(sessions, f, indent=2)


def create_session(username: str) -> str:
    """Create a new session for username. Returns the session token."""
    token = secrets.token_urlsafe(32)
    expiry = time.time() + (SESSION_EXPIRY_DAYS * 24 * 3600)
    # Try Supabase first
    try:
        from .supabase_storage import save_session_supabase
        if save_session_supabase(token, username, expiry):
            return token
    except Exception:
        pass
    # Fallback to file
    sessions = _load_sessions()
    sessions[token] = {"username": username, "expiry": expiry}
    _save_sessions(sessions)
    return token


def validate_session(token: str) -> Optional[str]:
    """Validate token. Returns username if valid, None otherwise."""
    if not token:
        return None
    # Try Supabase first
    try:
        from .supabase_storage import get_session_supabase
        username = get_session_supabase(token)
        if username:
            return username
    except Exception:
        pass
    # Fallback to file
    sessions = _load_sessions()
    if token not in sessions:
        return None
    sess = sessions[token]
    if sess["expiry"] < time.time():
        del sessions[token]
        _save_sessions(sessions)
        return None
    return sess["username"]


def destroy_session(token: str) -> None:
    """Remove a session token."""
    try:
        from .supabase_storage import delete_session_supabase
        delete_session_supabase(token)
    except Exception:
        pass
    sessions = _load_sessions()
    if token in sessions:
        del sessions[token]
        _save_sessions(sessions)
