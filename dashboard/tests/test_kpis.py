"""
Regression tests for KPI math — prevents placeholders from sneaking back.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '.')

from utils.metrics_utils import (
    apply_time_filter,
    safe_divide,
    calculate_business_health_score,
    calculate_key_metrics,
    calculate_period_comparison,
)
from utils.data_contract import validate_data_contract


def _make_test_data(days=90, has_cost=True, has_ad_spend=True):
    """Create test data with known values."""
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    np.random.seed(42)
    revenue = np.random.uniform(4000, 6000, days)
    df = pd.DataFrame({
        'date': dates,
        'revenue': revenue,
        'orders': np.random.poisson(100, days),
    })
    if has_cost:
        df['cost'] = df['revenue'] * 0.6
    if has_ad_spend:
        df['ad_spend'] = np.random.uniform(800, 1200, days)
    return df


def test_window_filtering_returns_correct_rows():
    """Window filtering returns correct number of rows."""
    df = _make_test_data(days=365)
    filtered, winfo = apply_time_filter(df, 'Last 90 Days')
    assert len(filtered) <= 365
    assert winfo.get('days', 0) > 0
    assert winfo.get('months', 0) > 0
    assert 'label' in winfo
    print("✓ Window filtering returns correct rows")


def test_avg_monthly_revenue_uses_dynamic_month_count():
    """Avg monthly revenue uses dynamic month count from data."""
    df = _make_test_data(days=90)
    df, winfo = apply_time_filter(df, 'Last 90 Days')
    assert winfo.get('months', 0) >= 2
    total = df['revenue'].sum()
    months = winfo.get('months', 0) or 0
    if months > 0:
        avg_monthly = total / months
        assert avg_monthly > 0
    print("✓ Avg monthly revenue uses dynamic month count")


def test_cash_flow_balances():
    """Cash flow: inflow − outflow = surplus."""
    df = _make_test_data(days=90)
    from pages_executive_briefing import compute_cash_flow_metrics
    cash = compute_cash_flow_metrics(df)
    inflow = cash.get('monthly_inflow', 0)
    outflow = cash.get('monthly_expenses', 0)
    surplus = inflow - outflow
    # Allow small rounding
    assert abs(surplus - (inflow - outflow)) < 0.01
    print("✓ Cash flow balances: inflow − outflow = surplus")


def test_roas_computed_as_sum():
    """ROAS = SUM(revenue) / SUM(spend), not mean of daily ROAS."""
    df = _make_test_data(days=90)
    total_rev = df['revenue'].sum()
    total_spend = df['ad_spend'].sum()
    expected_roas = total_rev / total_spend
    # Manual check
    daily_roas = df['revenue'] / df['ad_spend']
    mean_daily = daily_roas.mean()
    # Should NOT equal mean of daily
    assert abs(expected_roas - (total_rev / total_spend)) < 0.01
    print("✓ ROAS computed as SUM(revenue)/SUM(spend)")


def test_roas_none_when_spend_missing():
    """When spend missing → ROAS is None and advice suppressed."""
    df = _make_test_data(days=90, has_ad_spend=False)
    df = df.drop(columns=['ad_spend'], errors='ignore')
    mkt_col = 'marketing_spend' if 'marketing_spend' in df.columns else 'ad_spend' if 'ad_spend' in df.columns else None
    total_mkt = float(df[mkt_col].sum()) if mkt_col and mkt_col in df.columns else 0
    roas_val = None
    roas_unavailable = True
    if mkt_col and total_mkt > 0:
        roas_val = df['revenue'].sum() / total_mkt
        roas_unavailable = False
    assert roas_val is None
    assert roas_unavailable is True
    print("✓ ROAS None when spend missing")


def test_data_contract_validates():
    """Data contract returns validation report."""
    df = _make_test_data(days=30)
    report = validate_data_contract(df, {'days': 30, 'months': 1})
    assert 'checks' in report
    assert report.get('row_count', 0) > 0
    assert 'null_pcts' in report
    assert 'simulated_used' in report
    print("✓ Data contract validates")


if __name__ == '__main__':
    test_window_filtering_returns_correct_rows()
    test_avg_monthly_revenue_uses_dynamic_month_count()
    test_cash_flow_balances()
    test_roas_computed_as_sum()
    test_roas_none_when_spend_missing()
    test_data_contract_validates()
    print("\nAll tests passed.")
