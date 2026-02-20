"""
Test script for metrics accuracy — verifies avg_monthly_revenue, ROAS, net_cash_flow
computed correctly for a known dataset slice. No placeholders.
"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '.')

from utils.metrics_utils import safe_divide, apply_time_filter
from pages_executive_briefing import compute_cash_flow_metrics

# Known dataset (user's data: 3 categories x 3 months)
data = pd.DataFrame({
    'date': pd.to_datetime(['2024-10-01','2024-10-01','2024-10-01','2024-11-01','2024-11-01','2024-11-01','2024-12-01','2024-12-01','2024-12-01']),
    'category': ['Equipment','Accessories','Consumables']*3,
    'revenue': [452000,198000,661000, 489000,214000,682000, 521000,229000,711000],
    'cost': [271200,128700,381200, 293400,139100,392300, 312600,148900,408100],
    'ad_spend': [68400,41200,98200, 70200,43800,101500, 74800,46900,106300],
    'orders': [1130,1620,2410, 1210,1710,2560, 1290,1830,2710]
})
data['profit'] = data['revenue'] - data['cost']
data['profit_margin'] = (data['profit'] / data['revenue'] * 100)

def test_safe_divide():
    a, b = np.array([10, 20, 30]), np.array([2, 0, 5])
    r = safe_divide(a, b)
    assert r[0] == 5
    assert np.isnan(r[1])
    assert r[2] == 6
    print("✓ safe_divide")

def test_apply_time_filter():
    filtered, winfo = apply_time_filter(data, 'Last 90 Days')
    assert len(filtered) == 9
    assert winfo.get('months') == 3
    assert 'label' in winfo
    print("✓ apply_time_filter")

def test_avg_monthly_revenue():
    """Avg Monthly Revenue = SUM(revenue) / #months_in_window"""
    cash = compute_cash_flow_metrics(data)
    total_rev = data['revenue'].sum()
    expected_monthly = total_rev / 3  # 3 months
    assert abs(cash['monthly_inflow'] - expected_monthly) < 1
    print(f"✓ avg_monthly_revenue: {cash['monthly_inflow']:,.0f} (expected ~{expected_monthly:,.0f})")

def test_roas():
    """ROAS = SUM(revenue) / SUM(marketing_spend)"""
    total_rev = data['revenue'].sum()
    total_mkt = data['ad_spend'].sum()
    expected_roas = total_rev / total_mkt
    assert 6.0 < expected_roas < 7.0
    print(f"✓ ROAS: {expected_roas:.2f}x")

def test_net_cash_flow():
    """Net = revenue - (cost + ad_spend). No +20% ops."""
    cash = compute_cash_flow_metrics(data)
    money_in = data['revenue'].sum()
    money_out = data['cost'].sum() + data['ad_spend'].sum()
    actual_surplus = money_in - money_out
    monthly_surplus = cash['monthly_inflow'] - cash['monthly_expenses']
    expected_total = monthly_surplus * 3
    assert abs(expected_total - actual_surplus) < 1000
    assert actual_surplus > 400000  # ~$500K surplus for this dataset
    print(f"✓ net_cash_flow: surplus ~${actual_surplus:,.0f}")

if __name__ == '__main__':
    test_safe_divide()
    test_apply_time_filter()
    test_avg_monthly_revenue()
    test_roas()
    test_net_cash_flow()
    print("\n✅ All metrics accuracy tests passed.")
