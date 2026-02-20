"""Metrics calculation utilities for enhanced dashboard functionality."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional


def safe_divide(a, b):
    """Divide a by b; return np.nan where b <= 0. No silent fallbacks."""
    if hasattr(a, '__iter__') and hasattr(b, '__iter__'):
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(np.asarray(b) > 0, np.asarray(a) / np.asarray(b), np.nan)
    return (float(a) / float(b)) if b and float(b) > 0 else np.nan


def apply_time_filter(data: pd.DataFrame, date_range: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Apply sidebar date range to data. Returns (filtered_df, window_info).
    window_info: {start_date, end_date, days, months, label}
    """
    if data is None or data.empty or 'date' not in data.columns:
        return data, {'label': 'All data', 'days': 0, 'months': 0}
    df = data.copy()
    df['date'] = pd.to_datetime(df['date'])
    end_date = df['date'].max()
    days_map = {'Last 7 Days': 7, 'Last 30 Days': 30, 'Last 90 Days': 90, 'Last 12 Months': 365, 'All Time': 99999}
    days = days_map.get(date_range, 90)
    start_date = end_date - timedelta(days=days)
    filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
    if filtered.empty:
        filtered = df
    unique_months = filtered['date'].dt.to_period('M').nunique()
    date_range_days = (filtered['date'].max() - filtered['date'].min()).days
    label = f"{filtered['date'].min().strftime('%Y-%m-%d')} → {filtered['date'].max().strftime('%Y-%m-%d')} ({date_range_days} days, {unique_months} months)"
    return filtered, {'start_date': filtered['date'].min(), 'end_date': filtered['date'].max(), 'days': date_range_days, 'months': unique_months, 'label': label}


def calculate_period_comparison(current_value: float, previous_value: float) -> Dict[str, Any]:
    """
    Calculate period-over-period comparison metrics.
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
        
    Returns:
        Dict with change, percent_change, direction, and formatted_change
    """
    if previous_value == 0:
        return {
            'change': current_value,
            'percent_change': 0 if current_value == 0 else 100,
            'direction': 'up' if current_value > 0 else 'neutral',
            'formatted_change': 'N/A',
            'arrow': '→'
        }
    
    change = current_value - previous_value
    percent_change = (change / abs(previous_value)) * 100
    
    if percent_change > 0:
        direction = 'up'
        arrow = '↑'
    elif percent_change < 0:
        direction = 'down'
        arrow = '↓'
    else:
        direction = 'neutral'
        arrow = '→'
    
    return {
        'change': change,
        'percent_change': percent_change,
        'direction': direction,
        'formatted_change': f"{arrow} {abs(percent_change):.1f}%",
        'arrow': arrow
    }


def annualize_dollar_impact(change: float, period_days: int) -> float:
    """Scale a period change to annualized dollar impact. period_days=90 -> *4."""
    if period_days <= 0:
        return change
    return change * (365 / period_days)


def get_period_data(df: pd.DataFrame, date_column: str, period_type: str = 'month') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Get current and previous period data.
    
    Args:
        df: DataFrame with date column
        date_column: Name of date column
        period_type: 'day', 'week', 'month', 'quarter', 'year'
        
    Returns:
        Tuple of (current_period_df, previous_period_df)
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    now = df[date_column].max()
    
    period_mappings = {
        'day': 1,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365
    }
    
    days = period_mappings.get(period_type, 30)
    
    current_start = now - timedelta(days=days)
    previous_start = current_start - timedelta(days=days)
    previous_end = current_start
    
    current_period = df[df[date_column] >= current_start]
    previous_period = df[(df[date_column] >= previous_start) & (df[date_column] < previous_end)]
    
    return current_period, previous_period


def calculate_business_health_score(metrics: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Calculate overall business health score (0-100).
    
    Args:
        metrics: Dict with keys: revenue_growth, profit_margin, cash_flow, customer_growth, roas
        weights: Optional custom weights for each metric
        
    Returns:
        Dict with score, breakdown, color, and status
    """
    default_weights = {
        'revenue_growth': 0.30,
        'profitability': 0.20,
        'cash_flow': 0.20,
        'customer_growth': 0.20,
        'efficiency': 0.10
    }
    
    if weights is None:
        weights = default_weights    
    # Normalize each metric to 0-100 scale
    def normalize_growth(value, excellent=20, good=10, poor=-10):
        # Ensure value is scalar
        if hasattr(value, 'iloc'):
            value = float(value.iloc[0]) if len(value) > 0 else 0
        elif hasattr(value, '__iter__') and not isinstance(value, str):
            value = float(list(value)[0]) if len(list(value)) > 0 else 0
        value = float(value)

        if value >= excellent:
            return 100
        elif value >= good:
            return 70 + ((value - good) / (excellent - good)) * 30
        elif value >= 0:
            return 50 + ((value - 0) / good) * 20
        elif value >= poor:
            return 30 + ((value - poor) / (0 - poor)) * 20
        else:
            return max(0, 30 + (value - poor) * 0.5)
    
    def normalize_margin(value, excellent=40, good=20):
        # Ensure value is scalar
        if hasattr(value, 'iloc'):
            value = float(value.iloc[0]) if len(value) > 0 else 0
        elif hasattr(value, '__iter__') and not isinstance(value, str):
            value = float(list(value)[0]) if len(list(value)) > 0 else 0
        value = float(value)

        if value >= excellent:
            return 100
        elif value >= good:
            return 70 + ((value - good) / (excellent - good)) * 30
        elif value >= 10:
            return 50 + ((value - 10) / (good - 10)) * 20
        else:
            return max(0, value * 5)
    
    def normalize_positive(value, excellent=1.5, good=1.0):
        # Ensure value is scalar
        if hasattr(value, 'iloc'):
            value = float(value.iloc[0]) if len(value) > 0 else 0
        elif hasattr(value, '__iter__') and not isinstance(value, str):
            value = float(list(value)[0]) if len(list(value)) > 0 else 0
        value = float(value)

        if value >= excellent:
            return 100
        elif value >= good:
            return 70 + ((value - good) / (excellent - good)) * 30
        elif value >= 0.5:
            return 50 + ((value - 0.5) / (good - 0.5)) * 20
        else:
            return max(0, value * 100)
    
    # Calculate component scores
    revenue_score = normalize_growth(metrics.get('revenue_growth', 0))
    profit_score = normalize_margin(metrics.get('profit_margin', 0))
    cash_score = normalize_positive(metrics.get('cash_flow_ratio', 1))
    customer_score = normalize_growth(metrics.get('customer_growth', 0))
    efficiency_score = normalize_positive(metrics.get('roas', 1))  # Normalize ROAS
    
    # Calculate weighted score
    total_score = (
        revenue_score * weights['revenue_growth'] +
        profit_score * weights['profitability'] +
        cash_score * weights['cash_flow'] +
        customer_score * weights['customer_growth'] +
        efficiency_score * weights['efficiency']
    )
    
    # Determine color and status
    if total_score >= 75:
        color = 'green'
        status = 'Excellent'
        emoji = '🟢'
    elif total_score >= 50:
        color = 'yellow'
        status = 'Good'
        emoji = '🟡'
    else:
        color = 'red'
        status = 'Needs Attention'
        emoji = '🔴'
    
    return {
        'score': round(total_score, 1),
        'breakdown': {
            'Revenue': round(revenue_score, 1),
            'Profitability': round(profit_score, 1),
            'Cash Flow': round(cash_score, 1),
            'Customer Growth': round(customer_score, 1),
            'Efficiency': round(efficiency_score, 1)
        },
        'color': color,
        'status': status,
        'emoji': emoji
    }


def calculate_ltv(df: pd.DataFrame, lifespan_months: float = 24.0) -> float:
    """
    Single source of truth for Lifetime Value. Uses revenue per customer normalized by period length.
    LTV = (total_revenue / avg_customers) * (lifespan_months / period_months)
    
    Args:
        df: DataFrame with revenue, customers (and optionally date for period normalization)
        lifespan_months: Assumed customer lifespan in months (default 24 = 2 years)
        
    Returns:
        LTV in dollars, or 0 if data insufficient
    """
    if df is None or df.empty:
        return 0.0
    if 'revenue' not in df.columns:
        return 0.0
    total_revenue = df['revenue'].sum()
    if total_revenue <= 0:
        return 0.0
    # Avg customers: use mean over period (handles daily data)
    if 'customers' in df.columns:
        cust_mean = df['customers'].replace(0, np.nan).mean()
        if pd.isna(cust_mean) or cust_mean <= 0:
            cust_mean = df['customers'].iloc[-1] if len(df) > 0 else 0
    else:
        cust_mean = 0
    if cust_mean <= 0:
        # Fallback: AOV * 12 months if we have orders
        if 'orders' in df.columns and df['orders'].sum() > 0:
            aov = total_revenue / df['orders'].sum()
            return float(aov * 12)  # Conservative: 12 months of single-order value
        return 0.0
    revenue_per_customer = total_revenue / cust_mean
    # Period length in months (for normalization)
    if 'date' in df.columns and len(df) >= 2:
        df_dates = pd.to_datetime(df['date'])
        period_days = (df_dates.max() - df_dates.min()).days
        period_months = max(0.25, period_days / 30.44)
    else:
        period_months = 12.0  # Assume annual if no date
    return float(revenue_per_customer * (lifespan_months / period_months))


def calculate_key_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate key business metrics (CAC, LTV, Churn, etc.).
    
    Args:
        df: DataFrame with business data
        
    Returns:
        Dict with calculated metrics
    """
    metrics = {}
    
    # Revenue metrics
    if 'revenue' in df.columns:
        metrics['total_revenue'] = df['revenue'].sum()
        metrics['avg_daily_revenue'] = df['revenue'].mean()
    
    # Customer metrics
    if 'customers' in df.columns and len(df) > 0:
        df_sorted = df.sort_values('date' if 'date' in df.columns else df.index.name or 0).reset_index(drop=True)
        metrics['total_customers'] = df_sorted['customers'].iloc[-1]
        
        # Churn: adapt to data granularity (daily vs weekly vs monthly)
        if 'date' in df.columns and len(df_sorted) >= 2:
            df_sorted['date'] = pd.to_datetime(df_sorted['date'])
            days_span = (df_sorted['date'].max() - df_sorted['date'].min()).days
            # Need at least ~30 days of history for meaningful churn
            if days_span >= 20:
                # Use first third vs last third to handle non-daily data
                n = len(df_sorted)
                first_part = df_sorted.iloc[: max(1, n // 3)]
                last_part = df_sorted.iloc[-max(1, n // 3):]
                start_cust = first_part['customers'].mean()
                end_cust = last_part['customers'].mean()
                new_cust = df_sorted['new_customers'].sum() if 'new_customers' in df_sorted.columns else 0
                if start_cust > 0:
                    churned = max(0, start_cust + new_cust - end_cust) if new_cust > 0 else max(0, start_cust - end_cust)
                    metrics['churn_rate'] = (churned / start_cust * 100)
    
    # CAC calculation
    if 'marketing_spend' in df.columns and 'new_customers' in df.columns:
        total_marketing = df['marketing_spend'].sum()
        total_new_customers = df['new_customers'].sum()
        metrics['cac'] = total_marketing / total_new_customers if total_new_customers > 0 else 0
    
    # LTV - single source of truth
    metrics['ltv'] = calculate_ltv(df)
    
    # DSO (Days Sales Outstanding)
    if 'accounts_receivable' in df.columns and 'revenue' in df.columns:
        avg_ar = df['accounts_receivable'].mean()
        avg_daily_sales = df['revenue'].sum() / len(df)
        metrics['dso'] = avg_ar / avg_daily_sales if avg_daily_sales > 0 else 0
    
    # Profit margins
    if 'revenue' in df.columns and 'cost' in df.columns:
        total_revenue = df['revenue'].sum()
        total_cost = df['cost'].sum()
        metrics['profit_margin'] = ((total_revenue - total_cost) / total_revenue * 100) if total_revenue > 0 else 0
    
    # Growth rates - adapt to data length (works for sparse/non-daily data)
    if 'revenue' in df.columns and len(df) >= 4:
        n = len(df)
        half = max(1, n // 2)
        current_rev = df['revenue'].tail(half).sum()
        previous_rev = df['revenue'].iloc[:half].sum()
        metrics['revenue_growth'] = ((current_rev - previous_rev) / previous_rev * 100) if previous_rev > 0 else 0
    
    if 'customers' in df.columns and len(df) >= 2:
        df_s = df.sort_values('date' if 'date' in df.columns else df.index.name or 0).reset_index(drop=True)
        n = len(df_s)
        half = max(1, n // 2)
        current_customers = df_s['customers'].iloc[-1]
        period_ago_customers = df_s['customers'].iloc[max(0, half - 1)]
        metrics['customer_growth'] = ((current_customers - period_ago_customers) / period_ago_customers * 100) if period_ago_customers > 0 else 0
    
    return metrics


def get_goal_progress(current: float, target: float) -> Dict[str, Any]:
    """
    Calculate progress towards goal.
    
    Args:
        current: Current value
        target: Target value
        
    Returns:
        Dict with progress percentage, status, and alert
    """
    if target == 0:
        return {
            'progress': 0,
            'percentage': 0,
            'status': 'no_target',
            'alert': False,
            'message': 'No target set'
        }
    
    progress = (current / target) * 100
    
    if progress >= 100:
        status = 'achieved'
        alert = False
        message = '🎉 Goal achieved!'
    elif progress >= 90:
        status = 'on_track'
        alert = False
        message = '✅ On track'
    elif progress >= 70:
        status = 'at_risk'
        alert = True
        message = '⚠️ Slightly behind'
    else:
        status = 'off_track'
        alert = True
        message = '🚨 Significantly off track'
    
    return {
        'progress': min(progress, 100),
        'percentage': round(progress, 1),
        'status': status,
        'alert': alert,
        'message': message,
        'gap': target - current
    }


def format_currency(value: float, decimals: int = 0) -> str:
    """Format value as currency with appropriate suffix."""
    abs_value = abs(value)
    sign = '-' if value < 0 else ''
    
    if abs_value >= 1_000_000:
        return f"{sign}${abs_value/1_000_000:.{decimals}f}M"
    elif abs_value >= 1_000:
        return f"{sign}${abs_value/1_000:.{decimals}f}K"
    else:
        return f"{sign}${abs_value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


# --- Trust & Safety: Data Confidence, Unavailable Metrics, Period Diff ---

REQUIRED_COLUMNS_BY_METRIC = {
    'roas': ['revenue', 'marketing_spend'],  # or ad_spend, marketing_cost
    'marketing_spend': ['marketing_spend'],  # or ad_spend
    'revenue': ['revenue'],
    'profit': ['profit'],
    'cost': ['cost'],
}


def check_metric_availability(data: pd.DataFrame, metric: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a metric can be computed from available columns.
    Returns (available, missing_column_message).
    A wrong number is worse than no number.
    """
    if data is None or data.empty:
        return False, "No data"
    required = REQUIRED_COLUMNS_BY_METRIC.get(metric, [])
    if metric == 'roas':
        has_mkt = any(c in data.columns for c in ['marketing_spend', 'ad_spend', 'marketing_cost'])
        if not has_mkt:
            return False, "Required column marketing_spend (or ad_spend) not found."
        if 'revenue' not in data.columns:
            return False, "Required column revenue not found."
        mkt_col = 'marketing_spend' if 'marketing_spend' in data.columns else (
            'ad_spend' if 'ad_spend' in data.columns else 'marketing_cost')
        if data[mkt_col].sum() <= 0:
            return False, "marketing_spend is zero or missing."
        return True, None
    for col in required:
        if col not in data.columns:
            return False, f"Required column {col} not found."
    return True, None


def calculate_data_confidence(data: pd.DataFrame, kpis: Dict, window_info: Dict) -> Dict[str, Any]:
    """
    Compute Data Confidence: High / Medium / Low.
    Inputs: % missing in key columns, use of estimates, window length, fallback assumptions.
    """
    if data is None or data.empty:
        return {'level': 'Low', 'score': 0, 'reasons': ['No data']}
    reasons = []
    score = 100

    # Key columns
    key_cols = ['date', 'revenue', 'revenue', 'revenue']  # revenue weighted
    if 'marketing_spend' in data.columns or 'ad_spend' in data.columns:
        key_cols.extend(['marketing_spend', 'marketing_spend'])
    for col in ['date', 'revenue']:
        if col in data.columns:
            nan_pct = data[col].isna().sum() / len(data) * 100
            if nan_pct > 10:
                score -= 10
                reasons.append(f"{col}: {nan_pct:.0f}% missing")
            elif nan_pct > 10:
                score -= 5
                reasons.append(f"{col}: {nan_pct:.0f}% missing")

    # Window length: <30 days = low confidence
    days = window_info.get('days', 0)
    if days < 30:
        score -= 25
        reasons.append(f"Window <30 days ({days}d)")
    elif days < 60:
        score -= 10
        reasons.append(f"Window <60 days ({days}d)")

    # Use of estimates
    if kpis.get('roas_unavailable'):
        score -= 15
        reasons.append("ROAS unavailable (estimate not used)")
    mkt_col = 'marketing_spend' if 'marketing_spend' in data.columns else 'ad_spend' if 'ad_spend' in data.columns else None
    if not mkt_col:
        score -= 10
        reasons.append("Marketing spend estimated")
    if 'cost' not in data.columns and 'profit_margin' in data.columns:
        score -= 5
        reasons.append("Cost derived from margin")

    score = max(0, min(100, score))
    if score >= 75:
        level = 'High'
    elif score >= 50:
        level = 'Medium'
    else:
        level = 'Low'
    return {'level': level, 'score': score, 'reasons': reasons}


def calculate_period_diff(data: pd.DataFrame, kpis: Dict, format_currency_fn) -> Dict[str, Any]:
    """
    Calculate period-over-period diff for What Changed panel.
    Revenue, ROAS, Marketing Spend, Net Cash Flow between two adjacent windows.
    """
    if data is None or (hasattr(data, 'empty') and data.empty) or 'date' not in data.columns:
        return {'has_data': False}
    df = data.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    n = len(df)
    if n < 14:
        return {'has_data': False}
    mid = n // 2
    curr = df.iloc[mid:]
    prev = df.iloc[:mid]

    result = {'has_data': True, 'changes': []}
    # Revenue
    curr_rev = float(curr['revenue'].sum()) if 'revenue' in curr.columns else 0
    prev_rev = float(prev['revenue'].sum()) if 'revenue' in prev.columns else 0
    rev_delta = curr_rev - prev_rev
    result['changes'].append({'metric': 'Revenue', 'delta': rev_delta, 'fmt': format_currency_fn(rev_delta)})

    # ROAS
    mkt_col = 'marketing_spend' if 'marketing_spend' in data.columns else 'ad_spend' if 'ad_spend' in data.columns else None
    if mkt_col and kpis.get('roas') is not None and not kpis.get('roas_unavailable'):
        curr_mkt = curr[mkt_col].sum()
        prev_mkt = prev[mkt_col].sum()
        curr_roas = curr['revenue'].sum() / curr_mkt if curr_mkt > 0 else None
        prev_roas = prev['revenue'].sum() / prev_mkt if prev_mkt > 0 else None
        if curr_roas is not None and prev_roas is not None and prev_roas > 0:
            roas_delta = curr_roas - prev_roas
            result['changes'].append({'metric': 'ROAS', 'delta': roas_delta, 'fmt': f"{roas_delta:+.1f}x"})
    else:
        result['changes'].append({'metric': 'ROAS', 'delta': None, 'fmt': 'N/A'})

    # Marketing Spend
    if mkt_col:
        curr_mkt = float(curr[mkt_col].sum())
        prev_mkt = float(prev[mkt_col].sum())
        mkt_delta = curr_mkt - prev_mkt
        result['changes'].append({'metric': 'Marketing Spend', 'delta': mkt_delta, 'fmt': format_currency_fn(mkt_delta)})
    else:
        result['changes'].append({'metric': 'Marketing Spend', 'delta': None, 'fmt': 'N/A'})

    # Net Cash Flow
    curr_cost = float(curr['cost'].sum()) if 'cost' in curr.columns else 0
    prev_cost = float(prev['cost'].sum()) if 'cost' in prev.columns else 0
    curr_mkt = float(curr[mkt_col].sum()) if mkt_col and mkt_col in curr.columns else 0
    prev_mkt = float(prev[mkt_col].sum()) if mkt_col and mkt_col in prev.columns else 0
    curr_cf = curr_rev - curr_cost - curr_mkt
    prev_cf = prev_rev - prev_cost - prev_mkt
    cf_delta = curr_cf - prev_cf
    result['changes'].append({'metric': 'Net Cash Flow', 'delta': cf_delta, 'fmt': format_currency_fn(cf_delta)})

    return result


def get_trend_indicator(values: list) -> str:
    """
    Determine trend from list of values.
    
    Returns:
        'up', 'down', or 'flat'
    """
    if len(values) < 2:
        return 'flat'
    
    # Simple linear trend
    x = list(range(len(values)))
    slope = np.polyfit(x, values, 1)[0]
    
    if slope > 0.01:
        return 'up'
    elif slope < -0.01:
        return 'down'
    else:
        return 'flat'



def forecast_revenue(data: pd.DataFrame, days_ahead: int = 30) -> pd.DataFrame:
    """
    Forecast revenue for the next N days using simple time series methods.
    
    Args:
        data: DataFrame with 'date' and 'revenue' columns
        days_ahead: Number of days to forecast ahead
        
    Returns:
        DataFrame with forecasted dates and revenue values
    """
    try:
        # Ensure data is sorted by date
        data = data.sort_values('date').copy()
        
        # Calculate simple moving average for trend
        window = min(30, len(data) // 2)
        data['ma'] = data['revenue'].rolling(window=window, min_periods=1).mean()
        
        # Calculate growth rate from moving average
        recent_data = data.tail(window)
        if len(recent_data) > 1:
            growth_rate = (recent_data['ma'].iloc[-1] - recent_data['ma'].iloc[0]) / len(recent_data)
        else:
            growth_rate = 0
        
        # Generate future dates
        last_date = pd.to_datetime(data['date'].iloc[-1])
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
        
        # Forecast using linear projection
        last_revenue = float(data['revenue'].iloc[-1])
        forecasted_values = []
        
        for i in range(days_ahead):
            # Add growth with some variance based on historical std
            forecast = last_revenue + (growth_rate * (i + 1))
            forecasted_values.append(max(0, forecast))  # Ensure non-negative
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'revenue': forecasted_values
        })
        
        return forecast_df
        
    except Exception as e:
        # Return simple fallback forecast if errors occur
        last_date = pd.to_datetime(data['date'].iloc[-1])
        last_revenue = float(data['revenue'].iloc[-1])
        
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead, freq='D')
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'revenue': [last_revenue] * days_ahead  # Flat forecast as fallback
        })
        
        return forecast_df
