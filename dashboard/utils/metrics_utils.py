"""Metrics calculation utilities for enhanced dashboard functionality."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional


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
        if value >= excellent:
            return 100
        elif value >= good:
            return 70 + ((value - good) / (excellent - good)) * 30
        elif value >= 10:
            return 50 + ((value - 10) / (good - 10)) * 20
        else:
            return max(0, value * 5)
    
    def normalize_positive(value, excellent=1.5, good=1.0):
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
    efficiency_score = normalize_positive(metrics.get('roas', 1) / 10)  # Normalize ROAS
    
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
    if 'customers' in df.columns:
        metrics['total_customers'] = df['customers'].iloc[-1] if len(df) > 0 else 0
        
        # Simple churn calculation (if we have customer change data)
        if len(df) > 30:
            start_customers = df['customers'].iloc[-31]
            end_customers = df['customers'].iloc[-1]
            new_customers = df['new_customers'].sum() if 'new_customers' in df.columns else 0
            churned = start_customers + new_customers - end_customers
            metrics['churn_rate'] = (churned / start_customers * 100) if start_customers > 0 else 0
    
    # CAC calculation
    if 'marketing_spend' in df.columns and 'new_customers' in df.columns:
        total_marketing = df['marketing_spend'].sum()
        total_new_customers = df['new_customers'].sum()
        metrics['cac'] = total_marketing / total_new_customers if total_new_customers > 0 else 0
    
    # LTV calculation (simplified)
    if 'revenue' in df.columns and 'customers' in df.columns:
        avg_revenue_per_customer = df['revenue'].sum() / df['customers'].mean() if df['customers'].mean() > 0 else 0
        avg_lifespan_months = 24  # Assumption
        metrics['ltv'] = avg_revenue_per_customer * avg_lifespan_months
    
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
    
    # Growth rates
    if 'revenue' in df.columns and len(df) > 30:
        current_30d = df['revenue'].tail(30).sum()
        previous_30d = df['revenue'].iloc[-60:-30].sum()
        metrics['revenue_growth'] = ((current_30d - previous_30d) / previous_30d * 100) if previous_30d > 0 else 0
    
    if 'customers' in df.columns and len(df) > 30:
        current_customers = df['customers'].iloc[-1]
        month_ago_customers = df['customers'].iloc[-31]
        metrics['customer_growth'] = ((current_customers - month_ago_customers) / month_ago_customers * 100) if month_ago_customers > 0 else 0
    
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
