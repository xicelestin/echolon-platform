"""
Log every recommendation trigger for auditability.
Stores: metric value, threshold, window, confidence.
Enables: "Why we suggested this", better models, defensible decisions.
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit as st


def log_recommendation_trigger(
    recommendation_id: str,
    metric: str,
    metric_value: float,
    threshold: float,
    window: str,
    confidence: float,
    category: str,
    title: str,
) -> None:
    """Log a recommendation trigger for audit trail."""
    entry = {
        'ts': datetime.utcnow().isoformat(),
        'recommendation_id': recommendation_id,
        'metric': metric,
        'metric_value': metric_value,
        'threshold': threshold,
        'window': window,
        'confidence': confidence,
        'category': category,
        'title': title,
    }
    if 'recommendation_log' not in st.session_state:
        st.session_state.recommendation_log = []
    st.session_state.recommendation_log.append(entry)


def get_recommendation_log() -> List[Dict[str, Any]]:
    """Return the audit log of recommendation triggers."""
    return st.session_state.get('recommendation_log', [])


def format_log_for_display(entries: List[Dict[str, Any]]) -> str:
    """Format log entries for display in expander."""
    if not entries:
        return "No recommendations triggered this session."
    lines = []
    for e in entries[-20:]:  # Last 20
        lines.append(
            f"[{e['ts'][:19]}] {e['title']}: {e['metric']}={e['metric_value']:.1f} "
            f"(threshold {e['threshold']}), conf={e['confidence']}%, window={e['window']}"
        )
    return "\n".join(lines)
