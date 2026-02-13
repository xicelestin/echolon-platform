"""
Unified data model for Echolon - normalizes data from any source into a canonical schema.

Enables driver analysis, forecasting, and insights regardless of where data comes from
(POS, accounting, inventory, spreadsheets, marketing platforms).
"""
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import timedelta

# Canonical schema - columns Echolon expects for full analysis
CANONICAL_COLUMNS = {
    'required': ['date', 'revenue'],
    'core': ['orders', 'customers', 'profit', 'profit_margin'],
    'marketing': ['marketing_spend', 'roas'],
    'operational': ['inventory_units', 'avg_order_value'],
    'dimensional': ['product', 'product_id', 'category', 'channel', 'region'],
}

# Column aliases for mapping from various sources
COLUMN_ALIASES = {
    'date': ['date', 'created_at', 'transaction_date', 'order_date', 'txn_date'],
    'revenue': ['revenue', 'total', 'amount', 'sales', 'total_price', 'totalamt'],
    'orders': ['orders', 'order_count', 'transactions', 'invoice_count'],
    'customers': ['customers', 'customer_count', 'unique_customers'],
    'profit': ['profit', 'net_income', 'gross_profit'],
    'profit_margin': ['profit_margin', 'margin', 'margin_pct'],
    'marketing_spend': ['marketing_spend', 'ad_spend', 'marketing_cost'],
    'roas': ['roas', 'roi', 'return_on_ad_spend'],
    'product': ['product', 'product_name', 'item', 'sku'],
    'category': ['category', 'product_category', 'department'],
    'channel': ['channel', 'sales_channel', 'source', 'platform'],
    'region': ['region', 'location', 'store', 'market'],
}


def detect_and_map_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect which canonical columns exist in df (by exact match or alias).
    Returns mapping of canonical_col -> actual_col.
    """
    mapping = {}
    cols_lower = {c.lower(): c for c in df.columns}
    
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in cols_lower:
                mapping[canonical] = cols_lower[alias.lower()]
                break
    return mapping


def normalize_to_canonical(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Normalize a DataFrame to Echolon's canonical schema.
    
    Args:
        df: Raw data from any source
        column_mapping: Optional explicit mapping {canonical: actual_col}.
                        If None, auto-detects.
    
    Returns:
        DataFrame with canonical column names, date as datetime
    """
    if df is None or df.empty:
        return df
    
    out = df.copy()
    mapping = column_mapping or detect_and_map_columns(df)
    
    for canonical, actual in mapping.items():
        if actual in out.columns and actual != canonical:
            out[canonical] = out[actual]
    
    if 'date' in out.columns:
        out['date'] = pd.to_datetime(out['date'], errors='coerce')
        out = out.dropna(subset=['date'])
    
    # Derive missing core columns where possible
    if 'revenue' in out.columns and 'profit' not in out.columns and 'profit_margin' in out.columns:
        out['profit'] = out['revenue'] * (out['profit_margin'] / 100)
    elif 'revenue' in out.columns and 'profit' not in out.columns:
        out['profit'] = out['revenue'] * 0.4  # Default 40% margin
        out['profit_margin'] = 40.0
    
    if 'revenue' in out.columns and 'orders' in out.columns and 'avg_order_value' not in out.columns:
        out['avg_order_value'] = out['revenue'] / out['orders'].replace(0, 1)
    
    if 'marketing_spend' in out.columns and 'revenue' in out.columns and 'roas' not in out.columns:
        out['roas'] = (out['revenue'] / out['marketing_spend'].replace(0, 1)).clip(0.5, 20)
    
    return out


def get_available_dimensions(df: pd.DataFrame) -> List[str]:
    """Return which dimensional columns exist for driver analysis."""
    dims = []
    for d in CANONICAL_COLUMNS['dimensional']:
        if d in df.columns and df[d].notna().any():
            dims.append(d)
    return dims


def aggregate_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction-level data to daily for analysis.
    Preserves dimensional columns (channel, product, category) for driver analysis.
    """
    if df is None or df.empty or 'date' not in df.columns:
        return df
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date']).dt.normalize()
    
    agg_cols = ['revenue', 'orders', 'profit', 'marketing_spend']
    agg_cols = [c for c in agg_cols if c in df.columns]
    
    if not agg_cols:
        return df
    
    group_cols = ['date']
    dims = [d for d in ['channel', 'category', 'product'] if d in df.columns]
    group_cols.extend(dims)
    
    agg_dict = {c: 'sum' for c in agg_cols if c in df.columns}
    if 'customers' in df.columns:
        agg_dict['customers'] = 'nunique' if 'customer_id' in df.columns else 'sum'
    
    return df.groupby(group_cols, dropna=False).agg(agg_dict).reset_index()
