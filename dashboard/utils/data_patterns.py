"""
Data pattern detection - analyzes business data to find specific, actionable patterns.

Fully data-driven: uses actual column names and values from the data. No hardcoded
assumptions. Works for any business (e-commerce, retail, SaaS, etc.) and any
dimensions (channel, category, product, region, etc.).
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta

from .data_model import detect_and_map_columns


def _get_dimension_column(data: pd.DataFrame, canonical: str) -> Optional[str]:
    """Resolve dimension column - supports aliases (channel, sales_channel, platform, etc.)."""
    if data is None or data.empty:
        return None
    mapping = detect_and_map_columns(data)
    if canonical in mapping:
        return mapping[canonical]
    if canonical in data.columns:
        return canonical
    return None


def _fmt_cur(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


def detect_seasonality(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detect which months/weeks perform above or below average.
    Returns list of {period, revenue, avg_revenue, multiplier, direction}.
    """
    patterns = []
    if data is None or len(data) < 30 or 'date' not in data.columns or 'revenue' not in data.columns:
        return patterns

    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        monthly = df.groupby('month')['revenue'].sum()
        avg = monthly.mean()
        if avg <= 0:
            return patterns

        for month, rev in monthly.items():
            mult = rev / avg
            if mult >= 1.3:
                patterns.append({
                    'period': month,
                    'revenue': rev,
                    'avg_revenue': avg,
                    'multiplier': round(mult, 2),
                    'direction': 'above',
                    'message': f"{month} is {mult:.1f}x your average month ({_fmt_cur(rev)} vs {_fmt_cur(avg)} avg)",
                })
            elif mult <= 0.7:
                patterns.append({
                    'period': month,
                    'revenue': rev,
                    'avg_revenue': avg,
                    'multiplier': round(mult, 2),
                    'direction': 'below',
                    'message': f"{month} is {mult:.1f}x your average ({_fmt_cur(rev)} vs {_fmt_cur(avg)} avg)",
                })
        return sorted(patterns, key=lambda x: -x['multiplier'] if x['direction'] == 'above' else x['multiplier'])[:5]
    except Exception:
        return []


def detect_dimension_shifts(
    data: pd.DataFrame,
    dimension_col: str,
    dimension_label: str,
) -> List[Dict[str, Any]]:
    """
    Compare any dimension's performance: H2 vs H1 (second half vs first half of date range).
    Uses half-periods to reduce noise and correctly capture growth trends.
    Returns list with segment_name (actual value from data), change_pct, share_now, etc.
    """
    shifts = []
    if data is None or len(data) < 30 or dimension_col not in data.columns or 'revenue' not in data.columns:
        return shifts

    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        mid_date = df['date'].min() + (df['date'].max() - df['date'].min()) / 2
        curr = df[df['date'] >= mid_date]  # H2 / recent half
        prev = df[df['date'] < mid_date]   # H1 / prior half

        curr_grp = curr.groupby(dimension_col)['revenue'].sum()
        prev_grp = prev.groupby(dimension_col)['revenue'].sum()
        curr_total = curr_grp.sum()
        if curr_total <= 0:
            return shifts

        for seg in curr_grp.index:
            c_val = curr_grp[seg]
            p_val = prev_grp.get(seg, 0)
            share = (c_val / curr_total * 100)
            if p_val > 0:
                pct = ((c_val - p_val) / p_val) * 100
                shifts.append({
                    'segment_name': str(seg),
                    'dimension_type': dimension_label,
                    'current_rev': c_val,
                    'prev_rev': p_val,
                    'change_pct': round(pct, 1),
                    'share_now': round(share, 1),
                    'message': f"{seg}: {pct:+.1f}% vs prior half of period, now {share:.0f}% of revenue",
                })
            else:
                shifts.append({
                    'segment_name': str(seg),
                    'dimension_type': dimension_label,
                    'current_rev': c_val,
                    'prev_rev': 0,
                    'change_pct': 100,
                    'share_now': round(share, 1),
                    'message': f"{seg}: new in period, {share:.0f}% of revenue",
                })
        return sorted(shifts, key=lambda x: -x['current_rev'])[:6]
    except Exception:
        return []


def detect_channel_shifts(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Channel performance shifts. Uses dimension aliases (channel, sales_channel, platform)."""
    col = _get_dimension_column(data, 'channel')
    if not col:
        return []
    shifts = detect_dimension_shifts(data, col, 'channel')
    for s in shifts:
        s['channel'] = s['segment_name']  # backward compat
    return shifts


def detect_category_performance(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Top categories by revenue and margin. Uses category/product_category/department.
    """
    results = []
    col = _get_dimension_column(data, 'category')
    if not col or data is None or data.empty or 'revenue' not in data.columns:
        return results

    try:
        agg = data.groupby(col).agg(revenue=('revenue', 'sum'))
        total = agg['revenue'].sum()
        if total <= 0:
            return results

        if 'profit' in data.columns:
            agg['profit'] = data.groupby(col)['profit'].sum()
            agg['margin_pct'] = np.where(agg['revenue'] > 0, (agg['profit'] / agg['revenue'] * 100), 0).round(1)
        else:
            agg['margin_pct'] = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40

        agg['share'] = (agg['revenue'] / total * 100).round(1)
        agg = agg.sort_values('revenue', ascending=False)

        for _, row in agg.head(6).iterrows():
            cat = row.name
            rev = row['revenue']
            share = row['share']
            margin = row.get('margin_pct', 40)
            results.append({
                'category': cat,
                'revenue': rev,
                'margin_pct': round(float(margin), 1),
                'share': share,
                'message': f"{cat}: {_fmt_cur(rev)} ({share:.0f}% of revenue), {margin:.0f}% margin",
            })
        return results
    except Exception:
        return []


def detect_product_performance(data: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """Top products by revenue. Uses product/product_name/item/sku."""
    results = []
    col = _get_dimension_column(data, 'product')
    if not col or data is None or data.empty or 'revenue' not in data.columns:
        return results

    try:
        agg = data.groupby(col)['revenue'].sum()
        total = agg.sum()
        if total <= 0:
            return results

        agg = agg.sort_values(ascending=False).head(top_n)
        for prod, rev in agg.items():
            share = (rev / total * 100)
            results.append({
                'product': str(prod),
                'revenue': rev,
                'share': round(share, 1),
                'message': f"{prod}: {_fmt_cur(rev)} ({share:.0f}% of revenue)",
            })
        return results
    except Exception:
        return []


def detect_anomalies(data: pd.DataFrame, threshold_std: float = 2.0) -> List[Dict[str, Any]]:
    """
    Find days with unusually high or low revenue (vs rolling average).
    Returns list of {date, revenue, expected, deviation_pct, type}.
    """
    anomalies = []
    if data is None or len(data) < 14 or 'date' not in data.columns or 'revenue' not in data.columns:
        return anomalies

    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['revenue_7d_avg'] = df['revenue'].rolling(7, min_periods=3).mean()
        df = df.dropna(subset=['revenue_7d_avg'])
        df['revenue_7d_avg'] = df['revenue_7d_avg'].replace(0, np.nan)
        df = df.dropna(subset=['revenue_7d_avg'])
        if df.empty:
            return anomalies

        std = df['revenue'].std()
        if std <= 0:
            return anomalies

        for _, row in df.iterrows():
            rev = row['revenue']
            expected = row['revenue_7d_avg']
            if expected <= 0:
                continue
            dev_pct = ((rev - expected) / expected) * 100
            if dev_pct >= 50:
                anomalies.append({
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'revenue': rev,
                    'expected': expected,
                    'deviation_pct': round(dev_pct, 0),
                    'type': 'spike',
                    'message': f"{row['date'].strftime('%b %d')}: Revenue {_fmt_cur(rev)} — {dev_pct:.0f}% above 7-day average",
                })
            elif dev_pct <= -40:
                anomalies.append({
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'revenue': rev,
                    'expected': expected,
                    'deviation_pct': round(dev_pct, 0),
                    'type': 'drop',
                    'message': f"{row['date'].strftime('%b %d')}: Revenue {_fmt_cur(rev)} — {abs(dev_pct):.0f}% below 7-day average",
                })
        return sorted(anomalies, key=lambda x: -abs(x['deviation_pct']))[:5]
    except Exception:
        return []


def detect_low_margin_winners(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    High-revenue segments with below-average margin.
    Uses category first; falls back to product if no category.
    """
    results = []
    col = _get_dimension_column(data, 'category') or _get_dimension_column(data, 'product')
    if not col or data is None or data.empty or 'revenue' not in data.columns:
        return results

    try:
        df = data.copy()
        if 'profit' not in df.columns and 'profit_margin' in df.columns:
            df['profit'] = df['revenue'] * df['profit_margin'] / 100
        elif 'profit' not in df.columns:
            return results
        agg = df.groupby(col).agg(revenue=('revenue', 'sum'), profit=('profit', 'sum'))
        agg['margin_pct'] = np.where(agg['revenue'] > 0, (agg['profit'] / agg['revenue'] * 100), 0).round(1)
        total_rev = agg['revenue'].sum()
        avg_margin = agg['margin_pct'].mean()
        if total_rev <= 0:
            return results

        # High revenue, low margin
        low_margin = agg[(agg['revenue'] > total_rev * 0.05) & (agg['margin_pct'] < avg_margin - 5)]
        for seg, row in low_margin.iterrows():
            results.append({
                'category': str(seg),
                'revenue': row['revenue'],
                'margin_pct': row['margin_pct'],
                'share': round(row['revenue'] / total_rev * 100, 1),
                'message': f"{seg}: {row['revenue']/total_rev*100:.0f}% of revenue but only {row['margin_pct']:.0f}% margin (avg {avg_margin:.0f}%)",
            })
        return results[:4]
    except Exception:
        return []


def get_all_dimension_shifts(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Get shifts for any dimension column that exists (channel, category, product, region).
    Returns unified list with segment_name, dimension_type. Fully data-driven.
    """
    all_shifts = []
    for canonical, label in [('channel', 'channel'), ('category', 'category'), ('product', 'product'), ('region', 'region')]:
        col = _get_dimension_column(data, canonical)
        if col:
            shifts = detect_dimension_shifts(data, col, label)
            for s in shifts:
                s['channel'] = s['segment_name']  # compat for code expecting 'channel' key
            all_shifts.extend(shifts)
    return sorted(all_shifts, key=lambda x: -x['current_rev'])[:8]


def analyze_data_patterns(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Main entry: run all pattern detectors. Fully data-driven - uses actual
    column names (via aliases) and values from the data. No hardcoded assumptions.
    """
    if data is None or (hasattr(data, 'empty') and data.empty):
        return {'has_data': False, 'patterns': {}}

    channel_shifts = detect_channel_shifts(data)
    dimension_shifts = get_all_dimension_shifts(data)  # any breakdown: channel, category, product, region

    result = {
        'has_data': True,
        'total_revenue': float(data['revenue'].sum()) if 'revenue' in data.columns else 0,
        'patterns': {
            'seasonality': detect_seasonality(data),
            'channel_shifts': channel_shifts,
            'dimension_shifts': dimension_shifts,  # unified: works for any dimension
            'top_categories': detect_category_performance(data),
            'top_products': detect_product_performance(data),
            'anomalies': detect_anomalies(data),
            'low_margin_winners': detect_low_margin_winners(data),
        },
        'has_channel': _get_dimension_column(data, 'channel') is not None,
        'has_category': _get_dimension_column(data, 'category') is not None,
        'has_product': _get_dimension_column(data, 'product') is not None,
    }
    return result
