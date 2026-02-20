import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from utils.industry_utils import INDUSTRIES, get_industry_config, get_industry_benchmarks

# Load benchmark data from CSV
@st.cache_data
def load_benchmark_data(industry: str = 'general'):
    """Load industry benchmark data - filter by industry if CSV has industry column."""
    csv_path = os.path.join(os.path.dirname(__file__), 'benchmark_catalog.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if 'industry' in df.columns:
            filtered = df[df['industry'] == industry]
            if not filtered.empty:
                return filtered
            # Fallback to general
            filtered = df[df['industry'] == 'general']
            if not filtered.empty:
                return filtered
        return df
    # Fallback
    return pd.DataFrame({
        'metric': ['Profit Margin', 'ROAS', 'Customer Retention', 'Conversion Rate', 'LTV/CAC Ratio'],
        'industry_avg': [35.0, 4.0, 75.0, 3.5, 3.0],
        'top_quartile': [45.0, 6.0, 85.0, 5.0, 5.0],
        'best_in_class': [55.0, 8.0, 90.0, 7.0, 7.0],
        'unit': ['%', 'x', '%', '%', 'x'],
            'description': [
                'Net profit as percentage of revenue',
                'Return on advertising spend',
                'Percentage of customers retained year-over-year',
                'Percentage of visitors who make a purchase',
                'Lifetime value to customer acquisition cost ratio'
            ]
        })

def calculate_percentile_rank(your_value: float, industry_avg: float, top_quartile: float, best_in_class: float) -> str:
    """Estimate percentile rank vs similar businesses."""
    if your_value >= best_in_class:
        return "Top 10%"
    if your_value >= top_quartile:
        return "Top 25%"
    if your_value >= industry_avg:
        return "Above Average"
    if your_value >= industry_avg * 0.7:
        return "Average"
    return "Below Average"

def calculate_dollar_gaps(current_metrics, benchmarks, revenue, margin):
    """Calculate dollar value of gaps to industry benchmarks.
    ROAS opportunity = (Industry_ROAS - Current_ROAS) * Spend = additional revenue.
    """
    gaps = {}
    if benchmarks is None or benchmarks.empty:
        return gaps
    revenue = float(revenue or 0)
    margin = float(margin or 40)
    
    if 'profit_margin' in current_metrics and revenue > 0:
        row = benchmarks[benchmarks['metric'] == 'Profit Margin']
        if not row.empty:
            target = float(row['top_quartile'].values[0])
            gap = target - float(current_metrics['profit_margin'])
            if gap > 0:
                opp = revenue * (gap / 100)
                gaps['profit_margin'] = {
                    'gap': gap, 'annual_opportunity': opp,
                    'closing_25': opp * 0.25,
                    'closing_50': opp * 0.50
                }
    
    spend = float(current_metrics.get('marketing_spend', 0) or 0)
    if spend <= 0 and revenue > 0:
        spend = revenue * 0.15
    current_roas = current_metrics.get('roas')
    if current_roas is not None and spend > 0:
        row = benchmarks[benchmarks['metric'] == 'ROAS']
        if not row.empty:
            target = float(row['top_quartile'].values[0])
            current_roas = float(current_roas)
            gap = target - current_roas
            if gap > 0:
                add_rev = spend * gap  # (Industry_ROAS - Current_ROAS) * Spend
                opp = add_rev * margin / 100.0  # profit opportunity
                gaps['roas'] = {
                    'gap': gap, 'annual_opportunity': opp,
                    'closing_25': opp * 0.25,
                    'closing_50': opp * 0.50
                }
    
    return gaps

def render_competitive_benchmark_page(data, kpis, format_currency, format_percentage, format_number):
    """Render the competitive benchmark analysis page with industry selector."""
    
    st.title("🏆 Competitive Benchmark Analysis")
    st.markdown("### Compare your performance against businesses like yours")
    
    # Industry selector
    industry_key = st.session_state.get('industry', 'general')
    industry_options = {k: f"{v['icon']} {v['name']}" for k, v in INDUSTRIES.items()}
    selected = st.selectbox(
        "Your Industry",
        options=list(industry_options.keys()),
        format_func=lambda k: industry_options[k],
        key="benchmark_industry"
    )
    st.session_state.industry = selected
    
    benchmarks = load_benchmark_data(selected)
    
    total_revenue = kpis.get('total_revenue', data['revenue'].sum() if 'revenue' in data.columns else 0)
    avg_margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
    avg_roas = kpis.get('roas')
    if avg_roas is None and 'roas' in data.columns:
        avg_roas = data['roas'].mean()
    marketing_spend = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else 0
    spend_is_estimate = False
    if marketing_spend <= 0 and total_revenue > 0:
        marketing_spend = total_revenue * 0.15
        spend_is_estimate = True
    
    current_metrics = {
        'profit_margin': avg_margin,
        'roas': avg_roas,
        'revenue': total_revenue,
        'marketing_spend': marketing_spend,
        'spend_is_estimate': spend_is_estimate,
        'customer_count': kpis.get('total_customers', 0)
    }
    
    st.markdown("---")
    
    # "You vs Similar Businesses" - percentile rank
    st.subheader("📊 Your Performance vs Similar Businesses")
    
    metric_to_key = {'Profit Margin': 'profit_margin', 'ROAS': 'roas', 'Customer Retention': 'retention_rate', 
                     'Conversion Rate': 'conversion_rate', 'LTV/CAC Ratio': 'ltv_cac'}
    
    comparison_data = []
    for _, row in benchmarks.iterrows():
        metric_name = row['metric']
        key = metric_to_key.get(metric_name, metric_name.lower().replace(' ', '_'))
        your_val = current_metrics.get(key, avg_margin if 'margin' in metric_name.lower() else avg_roas)
        if your_val is None:
            your_val = 0
            rank = "N/A (no data)"
        else:
            rank = calculate_percentile_rank(
                your_val, row['industry_avg'], row['top_quartile'], row['best_in_class']
            )
        comparison_data.append({
            'Metric': metric_name,
            'Your Performance': your_val,
            'Industry Avg': row['industry_avg'],
            'Top Quartile': row['top_quartile'],
            'Best in Class': row['best_in_class'],
            'Unit': row.get('unit', '%'),
            'Your Rank': rank
        })
    
    # Show rank badge
    ranks = [r['Your Rank'] for r in comparison_data]
    top_ranks = sum(1 for r in ranks if 'Top' in r or 'Above' in r)
    st.info(f"**You're in the {ranks[0] if ranks else 'N/A'}** for your primary metrics — compared to {get_industry_config(selected)['name']} businesses.")
    
    comparison_df = pd.DataFrame(comparison_data)
    
    col1, col2 = st.columns(2)
    with col1:
        metric_data = comparison_df[comparison_df['Metric'] == 'Profit Margin'].iloc[0] if 'Profit Margin' in comparison_df['Metric'].values else comparison_df.iloc[0]
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=['You', 'Industry Avg', 'Top 25%', 'Best in Class'],
            y=[metric_data['Your Performance'], metric_data['Industry Avg'], 
               metric_data['Top Quartile'], metric_data['Best in Class']],
            marker_color=['#3b82f6', '#94a3b8', '#22c55e', '#eab308'],
            text=[f"{v:.1f}{metric_data['Unit']}" for v in [metric_data['Your Performance'], metric_data['Industry Avg'], 
                                        metric_data['Top Quartile'], metric_data['Best in Class']]],
            textposition='outside'
        ))
        fig1.update_layout(title='Profit Margin vs Industry', yaxis_title='%', showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        roas_row = comparison_df[comparison_df['Metric'] == 'ROAS'].iloc[0] if 'ROAS' in comparison_df['Metric'].values else comparison_df.iloc[1]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=['You', 'Industry Avg', 'Top 25%', 'Best in Class'],
            y=[roas_row['Your Performance'], roas_row['Industry Avg'], 
               roas_row['Top Quartile'], roas_row['Best in Class']],
            marker_color=['#3b82f6', '#94a3b8', '#22c55e', '#eab308'],
            text=[f"{v:.1f}x" for v in [roas_row['Your Performance'], roas_row['Industry Avg'], 
                                        roas_row['Top Quartile'], roas_row['Best in Class']]],
            textposition='outside'
        ))
        fig2.update_layout(title='ROAS vs Industry', yaxis_title='x', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💰 Financial Impact of Closing Gaps")
    
    gaps = calculate_dollar_gaps(current_metrics, benchmarks, total_revenue, avg_margin)
    
    if spend_is_estimate:
        st.warning("⚠️ **Marketing spend estimated** (15% of revenue). Map `ad_spend` in Data Sources for accurate opportunity.")
    
    if gaps:
        for gap_type, gap_data in gaps.items():
            with st.container():
                st.markdown(f"#### {gap_type.replace('_', ' ').title()} Gap")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    unit = '%' if gap_type != 'roas' else 'x'
                    st.metric("Gap to Top Quartile", f"{gap_data['gap']:.1f}{unit}", "")
                with col2:
                    st.metric("Annual Opportunity", format_currency(gap_data['annual_opportunity'], 0), "")
                with col3:
                    st.metric("Close 25% of Gap", format_currency(gap_data['closing_25'], 0), "")
                with col4:
                    st.metric("Close 50% of Gap", format_currency(gap_data['closing_50'], 0), "")
                st.markdown("---")
        
        total_opp = sum(g['annual_opportunity'] for g in gaps.values())
        st.success(f"🎯 **Total opportunity:** {format_currency(total_opp, 0)} annually by closing gaps to top quartile.")
    else:
        st.success("✅ You're at or above industry benchmarks!")
    
    st.markdown("---")
    st.subheader("📋 Full Benchmark Details")
    st.dataframe(benchmarks, use_container_width=True)
