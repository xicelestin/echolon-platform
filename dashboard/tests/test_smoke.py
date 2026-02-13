"""Smoke tests for Echolon Dashboard.

Verifies core modules load and key logic works without starting Streamlit.
Run: python -m pytest dashboard/tests/test_smoke.py -v
Or: cd dashboard && python -c "from tests.test_smoke import run_all; run_all()"
"""

import sys
from pathlib import Path

# Add dashboard dir to path so "from auth", "from utils.X" work
_dashboard = Path(__file__).resolve().parent.parent
if str(_dashboard) not in sys.path:
    sys.path.insert(0, str(_dashboard))


def test_user_data_storage_import():
    """User data storage module loads."""
    from utils.user_data_storage import save_user_data, load_user_data, has_stored_data
    assert callable(save_user_data)
    assert callable(load_user_data)
    assert callable(has_stored_data)


def test_user_data_storage_sanitize():
    """Username sanitization works."""
    from utils.user_data_storage import _sanitize_username
    assert _sanitize_username("demo") == "demo"
    assert _sanitize_username("user@email.com") != "user@email.com"
    assert "/" not in _sanitize_username("bad/user")


def test_data_model_import():
    """Data model utilities load."""
    from utils.data_model import normalize_to_canonical, detect_and_map_columns
    assert callable(normalize_to_canonical)
    assert callable(detect_and_map_columns)


def test_data_model_normalize():
    """Canonical normalization works."""
    import pandas as pd
    from utils.data_model import normalize_to_canonical
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "revenue": [1000, 1200],
        "orders": [10, 12],
    })
    out = normalize_to_canonical(df)
    assert "date" in out.columns
    assert "revenue" in out.columns
    assert len(out) == 2


def test_auth_import():
    """Auth module loads."""
    from auth import require_authentication, get_current_user
    assert callable(require_authentication)
    assert callable(get_current_user)


def run_all():
    """Run all smoke tests."""
    tests = [
        test_user_data_storage_import,
        test_user_data_storage_sanitize,
        test_data_model_import,
        test_data_model_normalize,
        test_auth_import,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
    return passed == len(tests)


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
