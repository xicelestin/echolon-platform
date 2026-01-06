"""Enhanced metric display components for dashboard."""
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any


def display_business_health_score(health_data: Dict[str, Any]):
    """
    Display Business Health Score with visual breakdown.
    
    Args:
        health_data: Dict from calculate_business_health_score()
    """
    score = health_data['score']
    status = health_data['status']
    emoji = health_data['emoji']
    breakdown = health_data['breakdown']
    color = health_data['color']
    
    # Main score display
    st.markdown(f"### {emoji} Business Health Score")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Large score display
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px;">
            <h1 style="color: white; font-size: 72px; margin: 0;">{score}</h1>
            <p style="color: white; font-size: 24px; margin: 0;">/ 100</p>
            <p style="color: white; font-size: 18px; margin-top: 10px;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Breakdown metrics
        st.markdown("#### Score Breakdown")
        for metric_name, metric_score in breakdown.items():
            # Progress bar for each component
            progress_color = "green" if metric_score >= 70 else ("orange" if metric_score >= 50 else "red")
            st.markdown(f"**{metric_name}**: {metric_score}/100")
            st.progress(metric_score / 100)
        
    # Health insights
    st.markdown("---")
    if score >= 75:
        st.success("🎉 Excellent! Your business is performing very well across all key metrics.")
    elif score >= 50:
        st.info("📈 Good performance. Focus on the lower-scoring areas to reach excellence.")
    else:
        st.warning("⚠️ Your business needs attention in multiple areas. Prioritize improvements in low-scoring metrics.")


def display_metric_with_comparison(label: str, current_value: float, previous_value: float, 
                                  format_as: str = "currency", prefix: str = "", suffix: str = "",
                                  help_text: Optional[str] = None):
    """
    Display a metric with period-over-period comparison.
    
    Args:
        label: Metric name
        current_value: Current period value
        previous_value: Previous period value
        format_as: 'currency', 'percentage', 'number'
        prefix: Optional prefix (e.g., '$')
        suffix: Optional suffix (e.g., '%', 'x')
        help_text: Tooltip text
    """
    from utils import calculate_period_comparison, format_currency, format_percentage
    
    # Calculate comparison
    comparison = calculate_period_comparison(current_value, previous_value)
    
    # Format current value
    if format_as == "currency":
        display_value = format_currency(current_value)
    elif format_as == "percentage":
        display_value = format_percentage(current_value)
    elif format_as == "number":
        if abs(current_value) >= 1000:
            display_value = f"{current_value:,.0f}"
        else:
            display_value = f"{current_value:.1f}"
    else:
        display_value = f"{prefix}{current_value}{suffix}"
    
    # Delta display with color
    delta_color = comparison['direction']
    if delta_color == 'up':
        delta_display = f":{delta_color}[{comparison['formatted_change']}]"
    elif delta_color == 'down':
        delta_display = f":{delta_color}[{comparison['formatted_change']}]"
    else:
        delta_display = comparison['formatted_change']
    
    # Use Streamlit metric with delta
    st.metric(
        label=label,
        value=display_value,
        delta=f"{comparison['arrow']} {abs(comparison['percent_change']):.1f}% vs last period",
        delta_color="normal" if comparison['direction'] == 'up' else ("inverse" if comparison['direction'] == 'down' else "off"),
        help=help_text
    )


def display_goal_progress(label: str, current: float, target: float, 
                         format_as: str = "currency", show_gap: bool = True):
    """
    Display goal progress with visual progress bar.
    
    Args:
        label: Goal name
        current: Current value
        target: Target value
        format_as: 'currency', 'percentage', 'number'
        show_gap: Whether to show remaining gap
    """
    from utils import get_goal_progress, format_currency
    
    progress_data = get_goal_progress(current, target)
    
    # Format values
    if format_as == "currency":
        current_display = format_currency(current)
        target_display = format_currency(target)
        gap_display = format_currency(progress_data['gap'])
    else:
        current_display = f"{current:,.0f}"
        target_display = f"{target:,.0f}"
        gap_display = f"{progress_data['gap']:,.0f}"
    
    # Display header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        st.markdown(f"*{progress_data['percentage']:.0f}%*")
    
    # Progress bar with color
    if progress_data['status'] == 'achieved':
        st.progress(1.0)
        st.success(progress_data['message'])
    elif progress_data['status'] == 'on_track':
        st.progress(progress_data['progress'] / 100)
        st.info(progress_data['message'])
    elif progress_data['status'] == 'at_risk':
        st.progress(progress_data['progress'] / 100)
        st.warning(progress_data['message'])
    else:
        st.progress(progress_data['progress'] / 100)
        st.error(progress_data['message'])
    
    # Show details
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    with detail_col1:
        st.caption(f"Current: {current_display}")
    with detail_col2:
        st.caption(f"Target: {target_display}")
    with detail_col3:
        if show_gap and progress_data['gap'] > 0:
            st.caption(f"Gap: {gap_display}")


def display_top_actions(actions: list, max_display: int = 3):
    """
    Display top priority actions box.
    
    Args:
        actions: List of action dicts with 'priority', 'title', 'description', 'impact'
        max_display: Maximum number of actions to show
    """
    st.markdown("### ⚡ Top Priority Actions")
    st.markdown("*Ranked by business impact*")
    
    for i, action in enumerate(actions[:max_display], 1):
        priority = action.get('priority', 'Medium')
        title = action.get('title', 'Action')
        description = action.get('description', '')
        impact = action.get('impact', 'Medium')
        
        # Priority badge color
        if priority == 'High':
            badge_color = "red"
            badge_emoji = "🔴"
        elif priority == 'Medium':
            badge_color = "orange"
            badge_emoji = "🟡"
        else:
            badge_color = "gray"
            badge_emoji = "⚪"
        
        # Display action card
        with st.expander(f"{badge_emoji} {i}. {title}", expanded=(i==1)):
            st.markdown(f"**Priority:** {priority} | **Impact:** {impact}")
            st.markdown(description)
            
            # Action button
            if st.button(f"Mark as Done #{i}", key=f"action_{i}"):
                st.success(f"✅ Action marked as complete!")


def display_key_metrics_grid(metrics: Dict[str, float]):
    """
    Display grid of key business metrics with labels.
    
    Args:
        metrics: Dict of metric_name: value pairs
    """
    st.markdown("### 📊 Key Business Metrics")
    
    # Define metric categories and formatting
    metric_config = {
        'cac': {'label': 'Customer Acquisition Cost', 'format': 'currency', 'help': 'Average cost to acquire a new customer'},
        'ltv': {'label': 'Customer Lifetime Value', 'format': 'currency', 'help': 'Average revenue per customer over their lifetime'},
        'churn_rate': {'label': 'Monthly Churn Rate', 'format': 'percentage', 'help': 'Percentage of customers lost per month'},
        'dso': {'label': 'Days Sales Outstanding', 'format': 'number', 'help': 'Average days to collect payment'},
        'ltv_cac_ratio': {'label': 'LTV:CAC Ratio', 'format': 'ratio', 'help': 'Ratio of lifetime value to acquisition cost'},
    }
    
    # Calculate LTV:CAC ratio if both exist
    if 'ltv' in metrics and 'cac' in metrics and metrics['cac'] > 0:
        metrics['ltv_cac_ratio'] = metrics['ltv'] / metrics['cac']
    
    # Display in 3-column grid
    cols = st.columns(3)
    col_idx = 0
    
    for metric_key, config in metric_config.items():
        if metric_key in metrics:
            with cols[col_idx % 3]:
                value = metrics[metric_key]
                label = config['label']
                help_text = config.get('help', '')
                
                if config['format'] == 'currency':
                    from utils import format_currency
                    display_val = format_currency(value)
                elif config['format'] == 'percentage':
                    display_val = f"{value:.1f}%"
                elif config['format'] == 'ratio':
                    display_val = f"{value:.1f}x"
                else:
                    display_val = f"{value:.0f}"
                
                st.metric(label=label, value=display_val, help=help_text)
            col_idx += 1


def display_period_selector():
    """
    Display period comparison selector.
    
    Returns:
        Selected period type
    """
    period = st.selectbox(
        "Compare to:",
        options=["Last Month", "Last Quarter", "Last Year", "Last Week"],
        index=0,
        key="period_selector"
    )
    
    period_map = {
        "Last Month": "month",
        "Last Quarter": "quarter",
        "Last Year": "year",
        "Last Week": "week"
    }
    
    return period_map.get(period, "month")
