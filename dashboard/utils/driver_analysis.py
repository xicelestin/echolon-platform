"""
Driver analysis - explains what changed and why.

Identifies underlying drivers (products, channels, time periods, behaviors)
and explains them in direct language. Removes the need for manual investigation.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import timedelta
from .metrics_utils import get_period_data


def _fmt_cur(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


def analyze_revenue_drivers(
    data: pd.DataFrame,
    period_days: int = 30
) -> List[Dict[str, Any]]:
    """
    Identify what drove revenue change - time periods, channels, products.
    Returns plain-language explanations.
    """
    drivers = []
    if data is None or len(data) < period_days * 2 or 'date' not in data.columns or 'revenue' not in data.columns:
        return drivers
    
    try:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        curr, prev = get_period_data(df, 'date', 'month')
        
        if curr.empty or prev.empty:
            return drivers
        
        curr_rev = curr['revenue'].sum()
        prev_rev = prev['revenue'].sum()
        total_change = curr_rev - prev_rev
        pct_change = (total_change / prev_rev * 100) if prev_rev > 0 else 0
        
        # 1. Time-period driver: which week dragged or lifted?
        curr['week'] = curr['date'].dt.isocalendar().week
        prev['week'] = prev['date'].dt.isocalendar().week
        curr_weekly = curr.groupby('week')['revenue'].sum()
        prev_weekly = prev.groupby('week')['revenue'].sum()
        
        if len(curr_weekly) >= 1 and len(prev_weekly) >= 1:
            curr_avg = curr_weekly.mean()
            prev_avg = prev_weekly.mean()
            worst_week = curr_weekly.idxmin()
            best_week = curr_weekly.idxmax()
            worst_val = curr_weekly.min()
            best_val = curr_weekly.max()
            
            if pct_change < -3:
                drivers.append({
                    'type': 'time',
                    'explanation': f"Week {int(worst_week)} underperformed at {_fmt_cur(worst_val)} vs prior period average of {_fmt_cur(prev_avg)}. That week alone accounts for much of the decline.",
                    'driver': f"Week {int(worst_week)}",
                    'impact': worst_val - prev_avg,
                })
            elif pct_change > 5:
                drivers.append({
                    'type': 'time',
                    'explanation': f"Week {int(best_week)} was the strongest at {_fmt_cur(best_val)}, above the prior period average of {_fmt_cur(prev_avg)}. That lift drove most of the growth.",
                    'driver': f"Week {int(best_week)}",
                    'impact': best_val - prev_avg,
                })
        
        # 2. Channel driver (when channel exists)
        if 'channel' in data.columns:
            curr_ch = curr.groupby('channel')['revenue'].sum()
            prev_ch = prev.groupby('channel')['revenue'].sum()
            all_channels = curr_ch.index.union(prev_ch.index)
            
            for ch in all_channels:
                c_val = curr_ch.get(ch, 0)
                p_val = prev_ch.get(ch, 0)
                if p_val > 0:
                    ch_pct = ((c_val - p_val) / p_val) * 100
                    ch_contrib = c_val - p_val
                    if abs(ch_pct) > 15 and abs(ch_contrib) > total_change * 0.1:
                        direction = "up" if ch_pct > 0 else "down"
                        drivers.append({
                            'type': 'channel',
                            'explanation': f"**{ch}** moved {direction} {abs(ch_pct):.0f}% ({_fmt_cur(ch_contrib)}), contributing significantly to the overall change.",
                            'driver': ch,
                            'impact': ch_contrib,
                        })
        
        # 3. Product/Category driver (when exists)
        for dim in ['category', 'product']:
            if dim in data.columns:
                curr_dim = curr.groupby(dim)['revenue'].sum()
                prev_dim = prev.groupby(dim)['revenue'].sum()
                for name in curr_dim.index:
                    c_val = curr_dim.get(name, 0)
                    p_val = prev_dim.get(name, 0)
                    if p_val > 0:
                        dim_pct = ((c_val - p_val) / p_val) * 100
                        if abs(dim_pct) > 20 and c_val > curr_rev * 0.05:
                            direction = "grew" if dim_pct > 0 else "declined"
                            drivers.append({
                                'type': dim,
                                'explanation': f"**{name}** {direction} {abs(dim_pct):.0f}% and represents {c_val/curr_rev*100:.0f}% of revenue.",
                                'driver': name,
                                'impact': c_val - p_val,
                            })
                break  # Only first available dimension
        
        # 4. Orders vs AOV decomposition
        if 'orders' in data.columns:
            curr_orders = curr['orders'].sum()
            prev_orders = prev['orders'].sum()
            curr_aov = curr_rev / curr_orders if curr_orders > 0 else 0
            prev_aov = prev_rev / prev_orders if prev_orders > 0 else 0
            
            if prev_orders > 0 and curr_orders > 0:
                order_pct = ((curr_orders - prev_orders) / prev_orders) * 100
                aov_pct = ((curr_aov - prev_aov) / prev_aov) * 100 if prev_aov > 0 else 0
                
                if abs(order_pct) > 5:
                    drivers.append({
                        'type': 'volume',
                        'explanation': f"Order volume {'increased' if order_pct > 0 else 'decreased'} {abs(order_pct):.1f}% ({int(curr_orders - prev_orders):+d} orders).",
                        'driver': 'orders',
                        'impact': curr_orders - prev_orders,
                    })
                if abs(aov_pct) > 5:
                    drivers.append({
                        'type': 'mix',
                        'explanation': f"Average order value {'increased' if aov_pct > 0 else 'decreased'} {abs(aov_pct):.1f}% (${curr_aov:.0f} vs ${prev_aov:.0f}).",
                        'driver': 'aov',
                        'impact': curr_aov - prev_aov,
                    })
        
        # 5. Marketing correlation
        if 'marketing_spend' in data.columns:
            curr_mkt = curr['marketing_spend'].sum()
            prev_mkt = prev['marketing_spend'].sum()
            if prev_mkt > 0:
                mkt_pct = ((curr_mkt - prev_mkt) / prev_mkt) * 100
                if abs(mkt_pct) > 10 and abs(pct_change) > 3:
                    if (mkt_pct > 0 and pct_change > 0) or (mkt_pct < 0 and pct_change < 0):
                        drivers.append({
                            'type': 'marketing',
                            'explanation': f"Marketing spend moved in the same direction as revenue ({mkt_pct:+.1f}% vs revenue {pct_change:+.1f}%). Changes in ad spend may be driving the shift.",
                            'driver': 'marketing_spend',
                            'impact': curr_mkt - prev_mkt,
                        })
        
        return drivers[:6]  # Cap at 6
        
    except Exception:
        return []


def get_change_explanation(
    data: pd.DataFrame,
    metrics: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Main entry: explain what changed and why in plain language.
    Returns summary + list of driver explanations for display.
    """
    result = {
        'summary': '',
        'drivers': [],
        'has_explanation': False,
    }
    
    drivers = analyze_revenue_drivers(data)
    
    if not drivers:
        if data is not None and len(data) >= 60 and 'revenue' in data.columns:
            df = data.copy()
            df['date'] = pd.to_datetime(df['date'])
            curr = df[df['date'] >= df['date'].max() - timedelta(days=30)]
            prev = df[(df['date'] >= df['date'].max() - timedelta(days=60)) & (df['date'] < df['date'].max() - timedelta(days=30))]
            if not curr.empty and not prev.empty:
                c_rev, p_rev = curr['revenue'].sum(), prev['revenue'].sum()
                pct = ((c_rev - p_rev) / p_rev * 100) if p_rev > 0 else 0
                result['summary'] = f"Revenue {'increased' if pct > 0 else 'decreased'} {abs(pct):.1f}% vs prior 30 days. Add product or channel columns to your data for detailed driver analysis."
        return result
    
    # Build summary from top drivers
    rev_drivers = [d for d in drivers if d['type'] in ('channel', 'category', 'product')]
    time_drivers = [d for d in drivers if d['type'] == 'time']
    other_drivers = [d for d in drivers if d['type'] in ('volume', 'mix', 'marketing')]
    
    parts = []
    if rev_drivers:
        parts.append(rev_drivers[0]['explanation'])
    if time_drivers:
        parts.append(time_drivers[0]['explanation'])
    if other_drivers and len(parts) < 2:
        parts.append(other_drivers[0]['explanation'])
    
    result['summary'] = ' '.join(parts[:2]) if parts else 'Revenue change driven by multiple factors.'
    result['drivers'] = drivers
    result['has_explanation'] = True
    
    return result
