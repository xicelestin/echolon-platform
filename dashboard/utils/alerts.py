"""
Proactive alerts when metrics deteriorate.
Surfaces risks before revenue is lost — no manual investigation needed.
"""
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import timedelta
from .metrics_utils import get_period_data


def _fmt_cur(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


def get_metric_alerts(data: pd.DataFrame, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Detect when key metrics have deteriorated vs prior period.
    Returns list of {severity, title, message, metric, change}.
    """
    alerts = []
    if data is None or len(data) < 60:
        return alerts

    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        curr, prev = get_period_data(df, 'date', 'month')
        if curr.empty or prev.empty:
            return alerts

        # Revenue decline
        curr_rev = curr['revenue'].sum()
        prev_rev = prev['revenue'].sum()
        if prev_rev > 0:
            rev_pct = ((curr_rev - prev_rev) / prev_rev) * 100
            if rev_pct < -5:
                alerts.append({
                    'severity': 'critical' if rev_pct < -15 else 'warning',
                    'title': 'Revenue Decline',
                    'message': f"Revenue down {abs(rev_pct):.1f}% vs prior 30 days ({_fmt_cur(curr_rev - prev_rev)}).",
                    'metric': 'revenue',
                    'change_pct': rev_pct,
                })

        # Margin decline
        if 'profit_margin' in data.columns:
            curr_m = curr['profit_margin'].mean()
            prev_m = prev['profit_margin'].mean()
            margin_pts = curr_m - prev_m
            if margin_pts < -3:
                alerts.append({
                    'severity': 'warning' if margin_pts > -5 else 'critical',
                    'title': 'Profit Margin Down',
                    'message': f"Margin dropped {abs(margin_pts):.1f} pts ({curr_m:.1f}% vs {prev_m:.1f}%). Check pricing and costs.",
                    'metric': 'profit_margin',
                    'change_pct': margin_pts,
                })

        # ROAS decline
        if 'roas' in data.columns:
            curr_r = curr['roas'].mean()
            prev_r = prev['roas'].mean()
            if prev_r > 0:
                roas_pct = ((curr_r - prev_r) / prev_r) * 100
                if roas_pct < -15:
                    alerts.append({
                        'severity': 'warning',
                        'title': 'Marketing Efficiency Down',
                        'message': f"ROAS dropped {abs(roas_pct):.0f}% ({curr_r:.1f}x vs {prev_r:.1f}x). Review underperforming campaigns.",
                        'metric': 'roas',
                        'change_pct': roas_pct,
                    })

        # Customer decline
        if 'customers' in data.columns:
            curr_c = curr['customers'].iloc[-1] if len(curr) > 0 else 0
            prev_c = prev['customers'].iloc[-1] if len(prev) > 0 else 0
            if prev_c > 0:
                cust_pct = ((curr_c - prev_c) / prev_c) * 100
                if cust_pct < -10:
                    alerts.append({
                        'severity': 'warning',
                        'title': 'Customer Count Down',
                        'message': f"Customers down {abs(cust_pct):.1f}% ({int(curr_c)} vs {int(prev_c)}). Check churn and acquisition.",
                        'metric': 'customers',
                        'change_pct': cust_pct,
                    })

        # Inventory alert (low stock risk)
        if 'inventory_units' in data.columns:
            curr_inv = curr['inventory_units'].mean()
            prev_inv = prev['inventory_units'].mean()
            if prev_inv > 0:
                inv_pct = ((curr_inv - prev_inv) / prev_inv) * 100
                if inv_pct < -25:
                    alerts.append({
                        'severity': 'warning',
                        'title': 'Inventory Declining',
                        'message': f"Inventory down {abs(inv_pct):.0f}%. Consider reordering to avoid stockouts.",
                        'metric': 'inventory',
                        'change_pct': inv_pct,
                    })
                elif inv_pct > 50:
                    alerts.append({
                        'severity': 'info',
                        'title': 'Inventory Building Up',
                        'message': f"Inventory up {inv_pct:.0f}%. Watch for excess holding costs.",
                        'metric': 'inventory',
                        'change_pct': inv_pct,
                    })

        return sorted(alerts, key=lambda a: (0 if a['severity'] == 'critical' else 1 if a['severity'] == 'warning' else 2))

    except Exception:
        return []
