"""RFM-style segmentation for customer insights. Works with aggregated data when customer-level data is unavailable."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple


def compute_retention_from_data(df: pd.DataFrame) -> Optional[float]:
    """
    Compute retention rate from available columns. Handles daily, weekly, or sparse data.
    Retention = 100 - churn_rate, or derived from customer trend.
    """
    if df is None or df.empty:
        return None
    # Method 1: explicit new_customers and churn
    if 'new_customers' in df.columns and 'customers' in df.columns and len(df) >= 30:
        df = df.sort_values('date' if 'date' in df.columns else df.index[0])
        df = df.reset_index(drop=True)
        start_cust = df['customers'].iloc[0]
        end_cust = df['customers'].iloc[-1]
        new = df['new_customers'].sum()
        if start_cust > 0 and new > 0:
            # Simplified: retained = end - new (approx). Retention = retained / (start + new) * 100
            churned = max(0, start_cust + new - end_cust)
            retention = 100 - (churned / start_cust * 100) if start_cust > 0 else 75
            return max(0, min(100, retention))
    # Method 2: customer growth implies retention (if growing, retention is healthy)
    if 'customers' in df.columns and len(df) >= 14:
        df = df.sort_values('date' if 'date' in df.columns else df.index[0]).reset_index(drop=True)
        # Compare first half vs second half
        mid = len(df) // 2
        first_half_avg = df['customers'].iloc[:mid].mean()
        second_half_avg = df['customers'].iloc[mid:].mean()
        if first_half_avg > 0:
            growth = (second_half_avg - first_half_avg) / first_half_avg * 100
            # Map growth to retention: positive growth -> high retention (80-95), negative -> lower
            retention = 75 + min(20, max(-30, growth))  # 45-95 range
            return max(0, min(100, retention))
    return None


def compute_rfm_segments_from_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute RFM-style segments from aggregated data. When customer-level data is unavailable,
    segments by revenue-contributing dimension (channel, category, or time period).
    
    Returns DataFrame with: Segment, Count, Avg Revenue, Retention (estimated), Lifetime Value
    """
    if df is None or df.empty:
        return _fallback_segments()
    
    df = df.copy()
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Prefer channel/category for segmentation (true RFM-like)
    dim_col = None
    for col in ['channel', 'category', 'product', 'segment']:
        if col in df.columns and df[col].nunique() >= 2:
            dim_col = col
            break
    
    if dim_col:
        agg = df.groupby(dim_col).agg(
            revenue=('revenue', 'sum'),
            orders=('orders', 'sum') if 'orders' in df.columns else ('revenue', 'count'),
            count=('revenue', 'count')
        ).reset_index()
        agg['avg_revenue'] = agg['revenue'] / agg['count'].clip(lower=1)
        total_rev = agg['revenue'].sum()
        if total_rev > 0:
            agg['share'] = agg['revenue'] / total_rev * 100
            # Quintiles: High = top 20%, Medium = next 50%, Low = bottom 30%
            agg = agg.sort_values('revenue', ascending=False).reset_index(drop=True)
            cumshare = agg['share'].cumsum()
            agg['Segment'] = np.where(cumshare <= 20, 'High Value',
                            np.where(cumshare <= 70, 'Medium Value',
                            np.where(cumshare <= 95, 'Low Value', 'At Risk')))
            seg_agg = agg.groupby('Segment').agg(
                Count=('orders', 'sum') if 'orders' in agg.columns else ('count', 'sum'),
                Avg_Revenue=('avg_revenue', 'mean'),
                share=('share', 'sum')
            ).reset_index()
            seg_agg['Retention'] = seg_agg['Segment'].map({
                'High Value': 92, 'Medium Value': 78, 'Low Value': 58, 'At Risk': 35
            })
            seg_agg['Lifetime Value'] = seg_agg['Avg_Revenue'] * 3  # Segment-level value multiple
            out = seg_agg[['Segment', 'Count', 'Avg_Revenue', 'Retention', 'Lifetime Value']].copy()
            out = out.rename(columns={'Avg_Revenue': 'Avg Revenue'})
            return out
    
    # Fallback: segment by time period (weekly)
    if 'date' in df.columns and 'revenue' in df.columns and len(df) >= 7:
        df['week'] = df['date'].dt.to_period('W').astype(str)
        weekly = df.groupby('week').agg(
            revenue=('revenue', 'sum'),
            orders=('orders', 'sum') if 'orders' in df.columns else ('revenue', 'count')
        ).reset_index()
        weekly['avg_revenue'] = weekly['revenue'] / weekly['orders'].clip(lower=1)
        total_rev = weekly['revenue'].sum()
        if total_rev > 0:
            weekly = weekly.sort_values('revenue', ascending=False).reset_index(drop=True)
            weekly['share'] = weekly['revenue'] / total_rev * 100
            cumshare = weekly['share'].cumsum()
            weekly['Segment'] = np.where(cumshare <= 25, 'High Value',
                                np.where(cumshare <= 70, 'Medium Value',
                                np.where(cumshare <= 95, 'Low Value', 'At Risk')))
            seg_agg = weekly.groupby('Segment').agg(
                Count=('orders', 'sum'),
                Avg_Revenue=('avg_revenue', 'mean'),
                Retention=('Segment', lambda x: 75)  # Placeholder
            ).reset_index()
            seg_agg['Retention'] = seg_agg['Segment'].map({
                'High Value': 90, 'Medium Value': 75, 'Low Value': 55, 'At Risk': 30
            })
            seg_agg['Lifetime Value'] = seg_agg['Avg Revenue'] * 3
            return seg_agg[['Segment', 'Count', 'Avg Revenue', 'Retention', 'Lifetime Value']]
    
    return _fallback_segments()


def _fallback_segments() -> pd.DataFrame:
    """Minimal fallback when data cannot support segmentation."""
    return pd.DataFrame({
        'Segment': ['High Value', 'Medium Value', 'Low Value'],
        'Count': [0, 0, 0],
        'Avg Revenue': [0, 0, 0],
        'Retention': [90, 75, 55],
        'Lifetime Value': [0, 0, 0]
    })
