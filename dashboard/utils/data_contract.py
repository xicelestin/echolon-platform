"""
Data Contract — validates data and proves what the app can/can't compute.
Required columns by feature, validation checks, and metadata for UI.
"""
import pandas as pd
from utils.telemetry import log_validation_failure
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta

# --- Required columns by feature/module ---
REQUIRED_BY_FEATURE = {
    'executive': {
        'required': ['date', 'revenue'],
        'optional': ['cost', 'marketing_spend', 'ad_spend', 'marketing_cost', 'profit_margin'],
    },
    'roas': {
        'required': [],  # needs one of: marketing_spend OR ad_spend
        'optional': ['marketing_spend', 'ad_spend', 'marketing_cost'],
    },
    'customer_analytics': {
        'required': [],  # needs customer_id OR customers column
        'optional': ['customer_id', 'customers'],
    },
    'inventory': {
        'required': ['inventory_units', 'orders'],
        'optional': ['unit_cost'],
    },
}

# Columns that must be numeric
NUMERIC_COLUMNS = [
    'revenue', 'cost', 'profit', 'profit_margin', 'marketing_spend', 'ad_spend',
    'marketing_cost', 'orders', 'inventory_units', 'customers', 'roas',
]

# Columns where negative values are impossible
NON_NEGATIVE_COLUMNS = ['revenue', 'orders', 'inventory_units', 'marketing_spend', 'ad_spend', 'marketing_cost']


def _is_roas_available(data: pd.DataFrame) -> bool:
    return any(c in data.columns for c in ['marketing_spend', 'ad_spend', 'marketing_cost']) and \
           'revenue' in data.columns and \
           any(data[c].sum() > 0 for c in ['marketing_spend', 'ad_spend', 'marketing_cost'] if c in data.columns)


def _is_customers_cumulative(data: pd.DataFrame) -> Optional[bool]:
    """Heuristic: if customers column is monotonic increasing in window → cumulative."""
    if data is None or data.empty or 'customers' not in data.columns:
        return None
    col = data['customers'].dropna()
    if len(col) < 2:
        return None
    col = pd.to_numeric(col, errors='coerce').dropna()
    if len(col) < 2:
        return None
    col = col.sort_index()
    diffs = col.diff()
    # If all diffs >= 0 (allowing small float noise), treat as cumulative
    return bool((diffs.dropna() >= -0.01).all())


def validate_data_contract(
    data: pd.DataFrame,
    window_info: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Run full validation and return report for UI.
    Returns: {checks, row_count, month_count, null_pcts, simulated_used, customers_semantics}
    """
    if data is None or (hasattr(data, 'empty') and data.empty):
        return {
            'checks': [],
            'row_count': 0,
            'month_count': 0,
            'null_pcts': {},
            'simulated_used': False,
            'customers_semantics': None,
            'margin_definition': 'Gross',
        }

    checks = []
    winfo = window_info or {}

    # 1. Missing columns
    for feat, spec in REQUIRED_BY_FEATURE.items():
        req = spec['required']
        for col in req:
            if col not in data.columns:
                checks.append({'status': 'error', 'message': f"Missing required: {col} (for {feat})"})
                log_validation_failure(f"missing_{col}", f"Missing required: {col} (for {feat})", "error")
            else:
                checks.append({'status': 'ok', 'message': f"Has {col} ({feat})"})
    if 'roas' in data.columns or _is_roas_available(data):
        checks.append({'status': 'ok', 'message': 'ROAS computable (marketing_spend/ad_spend)'})
    else:
        checks.append({'status': 'warn', 'message': 'ROAS: map marketing_spend or ad_spend'})
    if 'inventory_units' in data.columns and 'orders' in data.columns:
        checks.append({'status': 'ok', 'message': 'Inventory: has inventory_units + orders'})
    else:
        checks.append({'status': 'warn', 'message': 'Inventory: needs inventory_units + orders'})

    # 2. Non-numeric columns that should be numeric
    for col in NUMERIC_COLUMNS:
        if col in data.columns:
            try:
                pd.to_numeric(data[col], errors='coerce')
            except Exception:
                checks.append({'status': 'error', 'message': f"{col} must be numeric"})
            else:
                nan_count = pd.to_numeric(data[col], errors='coerce').isna().sum()
                if nan_count > len(data) * 0.5:
                    checks.append({'status': 'warn', 'message': f"{col}: >50% non-numeric"})

    # 3. Negative values where impossible
    for col in NON_NEGATIVE_COLUMNS:
        if col in data.columns:
            try:
                vals = pd.to_numeric(data[col], errors='coerce').dropna()
                neg = (vals < 0).sum()
                if neg > 0:
                    checks.append({'status': 'warn', 'message': f"{col}: {int(neg)} negative values"})
            except Exception:
                pass

    # 4. Date parsing
    if 'date' in data.columns:
        try:
            parsed = pd.to_datetime(data['date'], errors='coerce')
            fail_count = parsed.isna().sum()
            if fail_count > 0:
                checks.append({'status': 'warn', 'message': f"date: {int(fail_count)} parse failures"})
            else:
                checks.append({'status': 'ok', 'message': 'Dates parse OK'})
        except Exception as e:
            checks.append({'status': 'error', 'message': f"Date parsing failed: {e}"})

    # 5. Duplicates: check primary key (date+channel+category+product_id) if available
    # Duplicate dates alone are normal for segmented data — informational only, not error
    if 'date' in data.columns and len(data) > 0:
        key_cols = [c for c in ['date', 'channel', 'category', 'product_id'] if c in data.columns]
        if len(key_cols) >= 2:
            dupes = data[key_cols].duplicated().sum()
            if dupes > 0:
                checks.append({'status': 'warn', 'message': f"Duplicate rows on key {key_cols}: {int(dupes)}"})
        else:
            dupes = data['date'].duplicated().sum()
            if dupes > 0:
                checks.append({'status': 'info', 'message': "Multiple rows per date detected (expected if segmented). Aggregation will sum."})

    # Row count, month count
    row_count = len(data)
    month_count = 0
    if 'date' in data.columns and len(data) > 0:
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        month_count = df['date'].dt.to_period('M').nunique()

    # % nulls per key metric
    null_pcts = {}
    for col in ['revenue', 'date', 'cost', 'marketing_spend', 'ad_spend', 'orders', 'customers', 'inventory_units']:
        if col in data.columns:
            pct = data[col].isna().sum() / len(data) * 100
            null_pcts[col] = round(pct, 1)

    # Simulated values used
    simulated_used = False
    if 'cost' not in data.columns and 'revenue' in data.columns:
        simulated_used = True
    if not _is_roas_available(data) and 'revenue' in data.columns:
        simulated_used = True
    if 'inventory_units' not in data.columns and 'orders' not in data.columns:
        pass  # inventory not simulated from data
    # Simulated when we use profit_margin to derive cost
    if 'cost' not in data.columns and 'profit_margin' in data.columns:
        simulated_used = True

    # Customers semantics
    customers_semantics = None
    if 'customers' in data.columns:
        is_cum = _is_customers_cumulative(data)
        if is_cum is True:
            customers_semantics = 'cumulative'
        elif is_cum is False:
            customers_semantics = 'per_period'

    return {
        'checks': checks,
        'row_count': row_count,
        'month_count': month_count,
        'null_pcts': null_pcts,
        'simulated_used': simulated_used,
        'customers_semantics': customers_semantics,
        'customers_cumulative': customers_semantics == 'cumulative',
        'margin_definition': 'Gross',  # Will be set by compute_kpis
    }


def get_required_columns_for_feature(feature: str) -> List[str]:
    """Return required columns for a feature."""
    spec = REQUIRED_BY_FEATURE.get(feature, {})
    return spec.get('required', [])
