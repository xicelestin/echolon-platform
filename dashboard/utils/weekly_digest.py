"""Weekly Digest - Export summary for email or sharing."""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import json


def generate_weekly_digest(
    data: pd.DataFrame,
    kpis: Dict[str, Any],
    health_score: Dict[str, Any],
    top_opportunities: list = None,
    top_risks: list = None
) -> Dict[str, Any]:
    """
    Generate weekly digest content for email or export.
    
    Returns dict with 'html', 'text', 'json' for different use cases.
    """
    if data is None or data.empty:
        return {'html': '', 'text': '', 'json': '{}'}
    
    # Compute week-over-week changes
    recent_7d = data.tail(7)
    prior_7d = data.iloc[-14:-7] if len(data) >= 14 else data.head(7)
    
    rev_recent = recent_7d['revenue'].sum() if 'revenue' in recent_7d.columns else 0
    rev_prior = prior_7d['revenue'].sum() if 'revenue' in prior_7d.columns else rev_recent
    rev_change = ((rev_recent - rev_prior) / rev_prior * 100) if rev_prior > 0 else 0
    
    orders_recent = recent_7d['orders'].sum() if 'orders' in recent_7d.columns else 0
    orders_prior = prior_7d['orders'].sum() if 'orders' in prior_7d.columns else orders_recent
    orders_change = ((orders_recent - orders_prior) / orders_prior * 100) if orders_prior > 0 else 0
    
    digest = {
        'generated_at': datetime.now().isoformat(),
        'period': f"{recent_7d['date'].min()} to {recent_7d['date'].max()}" if 'date' in recent_7d.columns else 'Last 7 days',
        'metrics': {
            'revenue_7d': rev_recent,
            'revenue_change_pct': round(rev_change, 1),
            'orders_7d': int(orders_recent),
            'orders_change_pct': round(orders_change, 1),
            'health_score': health_score.get('score', 0),
            'health_status': health_score.get('status', 'N/A')
        },
        'top_opportunities': top_opportunities or [],
        'top_risks': top_risks or [],
        'recommended_action': (top_opportunities or [{}])[0].get('action', 'Review dashboard for updates.') if top_opportunities else 'Review dashboard for updates.'
    }
    
    # Build text version
    lines = [
        "ECHOLON AI — WEEKLY DIGEST",
        "=" * 40,
        f"Period: {digest['period']}",
        "",
        "KEY METRICS",
        f"  Revenue (7d): ${rev_recent:,.0f} ({rev_change:+.1f}% vs prior week)",
        f"  Orders (7d): {int(orders_recent)} ({orders_change:+.1f}% vs prior week)",
        f"  Business Health: {health_score.get('score', 0)}/100 ({health_score.get('status', 'N/A')})",
        "",
        "TOP OPPORTUNITY:",
        f"  {(top_opportunities or [{}])[0].get('action', 'Review your dashboard.') if top_opportunities else 'Review your dashboard.'}",
        "",
        "View full dashboard for detailed insights.",
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ]
    digest['text'] = '\n'.join(lines)
    
    # Simple HTML
    digest['html'] = f"""
    <div style="font-family:sans-serif;max-width:600px;">
        <h2>📊 Your Week in Numbers</h2>
        <p><strong>Period:</strong> {digest['period']}</p>
        <table style="border-collapse:collapse;width:100%;">
            <tr><td>Revenue (7d)</td><td>${rev_recent:,.0f}</td><td>{rev_change:+.1f}%</td></tr>
            <tr><td>Orders (7d)</td><td>{int(orders_recent)}</td><td>{orders_change:+.1f}%</td></tr>
            <tr><td>Health Score</td><td>{health_score.get('score', 0)}/100</td><td>{health_score.get('status', '')}</td></tr>
        </table>
        <p><strong>Do This Week:</strong> {(top_opportunities or [{}])[0].get('action', 'Review dashboard') if top_opportunities else 'Review dashboard'}</p>
        <p style="color:#666;font-size:12px;">Echolon AI · {datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
    """
    
    digest['json'] = json.dumps(digest, indent=2)
    
    return digest
