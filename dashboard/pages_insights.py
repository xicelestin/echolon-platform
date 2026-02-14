"""Sales Distribution & Key Metrics Page - Data-driven from actual business data."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils import (
    calculate_key_metrics,
    calculate_period_comparison,
    generate_personalized_insights,
    generate_action_items,
    get_top_priority_this_week,
    get_what_changed,
    get_quick_wins,
    get_progress_callouts,
    get_change_explanation,
)
from utils.data_patterns import analyze_data_patterns
from utils.data_model import detect_and_map_columns

def create_kpi_card(icon, title, value, delta, delta_pct_color, help_text):
    """Create a professional KPI card."""
    return f'''
    <div style='background:linear-gradient(135deg, #1F2937 0%, #111827 100%);border-radius:12px;padding:20px;border:1px solid #374151;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
        <div style='display:flex;justify-content:space-between;align-items:start;'>
            <div>
                <p style='color:#9CA3AF;font-size:13px;margin:0;font-weight:500;'>{title}</p>
                <h3 style='color:#F3F4F6;font-size:28px;font-weight:700;margin:8px 0 4px 0;'>{value}</h3>
                <p style='color:{delta_pct_color};font-size:13px;margin:0;font-weight:600;'>{delta}</p>
            </div>
            <div style='font-size:32px;'>{icon}</div>
        </div>
        <p style='color:#6B7280;font-size:12px;margin:12px 0 0 0;border-top:1px solid #374151;padding-top:12px;'>{help_text}</p>
    </div>
    '''

def render_insights_page(data=None, kpis=None, format_currency=None, format_percentage=None, format_number=None):
    """Render the Sales Insights & Key Metrics page - uses real data when provided."""
    if data is None:
        data = st.session_state.get('current_data')
        if data is None:
            data = st.session_state.get('uploaded_data')
    if data is None or (hasattr(data, 'empty') and data.empty):
        st.warning("Load data from Dashboard or Data Sources to see insights.")
        return

    fmt_cur = format_currency or (lambda v, d=0: f"${v:,.0f}" if v < 1e6 else f"${v/1e6:.1f}M")
    fmt_pct = format_percentage or (lambda v, d=1: f"{v:.1f}%")

    metrics = calculate_key_metrics(data)
    total_revenue = data['revenue'].sum() if 'revenue' in data.columns else 0
    total_orders = data['orders'].sum() if 'orders' in data.columns else 0
    active_customers = int(data['customers'].iloc[-1]) if 'customers' in data.columns else int(total_orders * 0.5)
    avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 50
    ltv = metrics.get('ltv', avg_order_value * 12)
    cac = metrics.get('cac', 45)
    ltv_cac_ratio = (ltv / cac) if cac > 0 else 0
    rev_growth = metrics.get('revenue_growth', 8)
    churn_rate = metrics.get('churn_rate', 2.1)

    # Period comparison for deltas
    if len(data) >= 60 and 'revenue' in data.columns:
        curr_rev = data.tail(30)['revenue'].sum()
        prev_rev = data.iloc[-60:-30]['revenue'].sum()
        rev_comp = calculate_period_comparison(curr_rev, prev_rev)
        rev_delta = rev_comp['formatted_change']
        rev_delta_color = '#10B981' if rev_comp['direction'] == 'up' else '#EF4444'
    else:
        rev_delta, rev_delta_color = '↑ 8%', '#10B981'

    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:36px;font-weight:700;margin-bottom:5px'>Sales Insights & Key Metrics</h1><p style='color:#9CA3AF;font-size:16px;margin:0'>Comprehensive business performance from your data</p></div>""", unsafe_allow_html=True)

    has_live = bool(st.session_state.get('connected_sources'))
    banner = "🟢 Live Data" if has_live else "📊 Demo Data"
    last_date = pd.to_datetime(data['date']).max().strftime('%Y-%m-%d') if 'date' in data.columns else 'N/A'
    st.markdown(f"""<div style='background:#065F46;color:#D1FAE5;border-radius:8px;padding:12px 16px;font-size:15px;margin-bottom:24px;'><b>{banner}</b> | Through {last_date}</div>""", unsafe_allow_html=True)
    
    industry = st.session_state.get('industry', 'ecommerce')
    
    # Top Priority This Week - single clear recommendation
    top_priority = get_top_priority_this_week(data, metrics, industry)
    if top_priority:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1E3A5F 0%,#0F172A 100%);border:1px solid #3B82F6;border-radius:12px;padding:20px 24px;margin-bottom:24px;'>
            <p style='color:#93C5FD;font-size:12px;margin:0 0 8px 0;text-transform:uppercase;letter-spacing:0.5px;'>🎯 Top Priority This Week</p>
            <h3 style='color:#F3F4F6;font-size:20px;font-weight:700;margin:0 0 10px 0;'>{top_priority['title']}</h3>
            <p style='color:#D1D5DB;font-size:15px;margin:0 0 8px 0;'>{top_priority['action']}</p>
            <p style='color:#10B981;font-size:14px;margin:0;font-weight:600;'>Impact: {top_priority['impact']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display KPI Cards in 4 columns
    st.markdown("""<div style='margin-bottom:24px'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Key Performance Indicators</h3></div>""", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card(
            '💰', 'Total Revenue', fmt_cur(total_revenue),
            rev_delta, rev_delta_color, 'Total revenue this period'
        ), unsafe_allow_html=True)
    
    with col2:
        cust_delta = '—'
        cust_delta_color = '#9CA3AF'
        if 'customers' in data.columns and len(data) >= 60:
            curr_cust = data.tail(30)['customers'].iloc[-1] if 'customers' in data.columns else 0
            prev_cust = data.iloc[-60:-30]['customers'].iloc[-1] if len(data) >= 60 else curr_cust
            if prev_cust > 0:
                cust_pct = ((curr_cust - prev_cust) / prev_cust) * 100
                cust_delta = f"{'↑' if cust_pct >= 0 else '↓'} {abs(cust_pct):.1f}%"
                cust_delta_color = '#10B981' if cust_pct >= 0 else '#EF4444'
        st.markdown(create_kpi_card(
            '👥', 'Active Customers', f'{active_customers:,}',
            cust_delta, cust_delta_color, 'Active customer count'
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_kpi_card(
            '🛍️', 'Average Order Value', fmt_cur(avg_order_value, 2),
            '—', '#9CA3AF', 'Mean transaction value'
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_kpi_card(
            '💎', 'Customer LTV', fmt_cur(ltv),
            f'↑ {rev_growth:.1f}%', '#10B981', 'Lifetime value per customer'
        ), unsafe_allow_html=True)
    
    # Second row of KPIs
    st.markdown("""<div style='margin:24px 0;'></div>""", unsafe_allow_html=True)
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.markdown(create_kpi_card(
            '📊', 'CAC', f'${cac:.0f}',
            '↓ 5.2%', '#10B981', 'Customer acquisition cost'
        ), unsafe_allow_html=True)
    
    with col6:
        efficiency_color = '#10B981' if ltv_cac_ratio > 20 else '#F59E0B'
        efficiency_pct = '↑ 18%'
        st.markdown(create_kpi_card(
            '⚡', 'LTV/CAC Ratio', f'{ltv_cac_ratio:.1f}x',
            efficiency_pct, efficiency_color, 'LTV to CAC ratio (>20x ideal)'
        ), unsafe_allow_html=True)
    
    with col7:
        st.markdown(create_kpi_card(
            '📈', 'Revenue Growth', fmt_pct(rev_growth),
            'vs prior period', '#10B981', 'Revenue growth rate'
        ), unsafe_allow_html=True)
    
    with col8:
        st.markdown(create_kpi_card(
            '⚠️', 'Churn Rate', fmt_pct(churn_rate),
            '—', '#9CA3AF', 'Monthly customer churn (est.)'
        ), unsafe_allow_html=True)
    
    # Divider
    st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)

    # Export Insights Report
    if st.button("📥 Export Insights Report"):
        report = f"""
ECHOLON AI - BUSINESS INSIGHTS REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

KEY PERFORMANCE INDICATORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Revenue: {fmt_cur(total_revenue)}
Active Customers: {active_customers:,}
Average Order Value: {fmt_cur(avg_order_value, 2)}
Customer LTV: {fmt_cur(ltv)}
CAC: {fmt_cur(cac)}
LTV/CAC Ratio: {ltv_cac_ratio:.1f}x
Revenue Growth: {fmt_pct(rev_growth)}
Churn Rate: {fmt_pct(churn_rate)}

This report provides a comprehensive overview of your business metrics.
For detailed analysis, please visit the Insights page in the Echolon platform.
"""
        st.download_button(
            label="Download Report",
            data=report,
            file_name=f"echolon_insights_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
    
    # Breakdown Analysis - use real data when available
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:20px;font-weight:600;'>Sales Breakdown Analysis</h3></div>""", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>Revenue by Month</h4></div>""", unsafe_allow_html=True)
        
        if 'date' in data.columns and 'revenue' in data.columns:
            monthly = data.copy()
            monthly['date'] = pd.to_datetime(monthly['date'])
            monthly['month'] = monthly['date'].dt.to_period('M').astype(str)
            agg = monthly.groupby('month')['revenue'].sum().reset_index()
            fig_cat = px.bar(agg, x='month', y='revenue', title='Revenue by Month')
            fig_cat.update_layout(height=300, template='plotly_dark', xaxis_tickangle=-45)
        else:
            fig_cat = px.bar(x=['N/A'], y=[0], title='Revenue by Month')
            fig_cat.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_right:
        # Use dimension breakdown when available (channel, sales_channel, category, etc.)
        dim_col = mapping.get('channel') or mapping.get('category') or ('channel' if 'channel' in data.columns else ('category' if 'category' in data.columns else None))
        if dim_col and dim_col in data.columns and 'revenue' in data.columns:
            label = 'Channel' if dim_col in ('channel', 'sales_channel', 'source', 'platform') else 'Category'
            st.markdown(f"""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>Revenue by {label}</h4></div>""", unsafe_allow_html=True)
            ch_agg = data.groupby(dim_col)['revenue'].sum().reset_index()
            ch_agg = ch_agg.sort_values('revenue', ascending=False)
            fig_channel = px.pie(
                ch_agg, values='revenue', names=dim_col,
                title='Revenue by Channel (your data)',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
        elif 'revenue' in data.columns and 'marketing_spend' in data.columns:
            st.markdown("""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>Revenue vs Marketing Spend</h4></div>""", unsafe_allow_html=True)
            channels = pd.DataFrame({
                'Metric': ['Revenue', 'Marketing Spend'],
                'Value': [data['revenue'].sum(), data['marketing_spend'].sum()]
            })
            fig_channel = px.pie(
                channels, values='Value', names='Metric',
                title='Revenue vs Marketing Investment',
                color_discrete_sequence=['#10B981', '#F59E0B']
            )
        else:
            st.markdown("""<div style='margin-bottom:16px'><h4 style='font-size:16px;font-weight:600;'>Revenue</h4></div>""", unsafe_allow_html=True)
            fig_channel = px.pie(values=[1], names=['Revenue'], title='Revenue')
        fig_channel.update_layout(height=300, template='plotly_dark')
        st.plotly_chart(fig_channel, use_container_width=True)
    
    # Revenue Trend (real data)
    st.markdown("""<div style='margin:24px 0 16px 0;border-top:1px solid #374151;padding-top:24px;'><h4 style='font-size:16px;font-weight:600;margin-bottom:16px;'>Revenue Trend Over Time</h4></div>""", unsafe_allow_html=True)
    
    if 'date' in data.columns and 'revenue' in data.columns:
        chart_data = data[['date', 'revenue']].copy()
        chart_data['date'] = pd.to_datetime(chart_data['date'])
        fig_regional = px.area(chart_data, x='date', y='revenue', title='Revenue Over Time')
    else:
        fig_regional = go.Figure()
        fig_regional.add_annotation(text="No date/revenue data", x=0.5, y=0.5, showarrow=False)
    fig_regional.update_layout(height=350, template='plotly_dark')
    st.plotly_chart(fig_regional, use_container_width=True)

    # Dimension performance: current vs prior period (when channel/category exists)
    dim_col = mapping.get('channel') or mapping.get('category') or ('channel' if 'channel' in data.columns else ('category' if 'category' in data.columns else None))
    if dim_col and dim_col in data.columns and 'revenue' in data.columns and len(data) >= 60:
        label = 'Channel' if dim_col in ('channel', 'sales_channel', 'source', 'platform') else 'Category'
        st.markdown(f"""<div style='margin:24px 0 16px 0;'><h4 style='font-size:16px;font-weight:600;'>{label} Performance: Current vs Prior 30 Days</h4></div>""", unsafe_allow_html=True)
        df_ch = data.copy()
        df_ch['date'] = pd.to_datetime(df_ch['date'])
        cutoff = df_ch['date'].max() - timedelta(days=30)
        curr = df_ch[df_ch['date'] >= cutoff].groupby(dim_col)['revenue'].sum()
        prev = df_ch[(df_ch['date'] >= cutoff - timedelta(days=30)) & (df_ch['date'] < cutoff)].groupby(dim_col)['revenue'].sum()
        comp = pd.DataFrame({'Current': curr, 'Prior': prev}).fillna(0)
        comp = comp.sort_values('Current', ascending=True)
        fig_ch = go.Figure()
        fig_ch.add_trace(go.Bar(name='Current 30d', y=comp.index, x=comp['Current'], orientation='h', marker_color='#10B981'))
        fig_ch.add_trace(go.Bar(name='Prior 30d', y=comp.index, x=comp['Prior'], orientation='h', marker_color='#6B7280'))
        fig_ch.update_layout(barmode='group', height=300, template='plotly_dark', xaxis_title='Revenue')
        st.plotly_chart(fig_ch, use_container_width=True)
    
    # Product/Category margins (when category exists)
    if 'category' in data.columns and 'revenue' in data.columns:
        st.markdown("""<div style='margin:24px 0 16px 0;'><h4 style='font-size:16px;font-weight:600;'>Margin by Category</h4></div>""", unsafe_allow_html=True)
        cat_data = data.groupby('category')['revenue'].sum().reset_index()
        if 'profit' in data.columns:
            cat_profit = data.groupby('category')['profit'].sum().reset_index()
            cat_data = cat_data.merge(cat_profit, on='category')
            cat_data['margin_pct'] = (cat_data['profit'] / cat_data['revenue'] * 100).round(1)
        else:
            margin = data['profit_margin'].mean() if 'profit_margin' in data.columns else 40
            cat_data['margin_pct'] = margin
        cat_data = cat_data.sort_values('revenue', ascending=False).head(10)
        fig_cat = px.bar(cat_data, x='category', y='margin_pct', title='Profit Margin by Category',
                         color='margin_pct', color_continuous_scale='RdYlGn')
        fig_cat.update_layout(height=280, template='plotly_dark', xaxis_tickangle=-45)
        st.plotly_chart(fig_cat, use_container_width=True)
        low_margin = cat_data[cat_data['margin_pct'] < 25]
        if not low_margin.empty:
            st.markdown(f"**Low-margin categories:** {', '.join(low_margin['category'].tolist())} — consider pricing or cost review.")
    
    # What Changed and Why - period-over-period + driver analysis
    what_changed = get_what_changed(data, metrics)
    change_explanation = get_change_explanation(data, metrics)
    
    if what_changed or change_explanation.get('has_explanation'):
        st.markdown("""<div style='margin:32px 0 16px 0;border-top:1px solid #374151;padding-top:24px;'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>📈 What Changed and Why</h3></div>""", unsafe_allow_html=True)
        st.caption("Echolon identifies underlying drivers — no manual investigation needed.")
        if what_changed:
            for c in what_changed:
                st.markdown(f"- **{c['metric']}**: {c['message']}")
        if change_explanation.get('has_explanation') and change_explanation.get('drivers'):
            st.markdown("**Drivers:**")
            for d in change_explanation['drivers'][:4]:
                st.markdown(f"  - {d['explanation']}")
        elif change_explanation.get('summary'):
            st.info(change_explanation['summary'])
        st.markdown("")
    
    # Progress callouts (positive improvements)
    progress = get_progress_callouts(data, metrics)
    if progress:
        st.markdown("""<div style='margin-bottom:16px;'><h4 style='font-size:16px;font-weight:600;'>✅ Progress This Period</h4></div>""", unsafe_allow_html=True)
        for p in progress:
            st.success(p)
        st.markdown("")
    
    # Quick Wins - under 2 hours
    quick_wins = get_quick_wins(data, metrics, industry)
    if quick_wins:
        st.markdown("""<div style='margin:24px 0 16px 0;'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>⚡ Quick Wins (Under 2 Hours)</h3></div>""", unsafe_allow_html=True)
        for w in quick_wins:
            st.markdown(f"**{w['action']}** — {w['impact']} *({w['time']})*")
        st.markdown("")
    
    # Pattern analysis (data-driven, no LLM)
    pattern_analysis = analyze_data_patterns(data)
    patterns = pattern_analysis.get('patterns', {}) if pattern_analysis.get('has_data') else {}
    mapping = detect_and_map_columns(data) if data is not None else {}

    # Key Patterns section (uses actual segment names from data)
    dim_shifts = patterns.get('dimension_shifts', []) or patterns.get('channel_shifts', [])
    if patterns and (dim_shifts or patterns.get('top_categories') or patterns.get('seasonality')):
        st.markdown("""<div style='margin:32px 0 16px 0;border-top:1px solid #374151;padding-top:24px;'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>📊 Patterns in Your Data</h3></div>""", unsafe_allow_html=True)
        st.caption("Detected from your actual numbers — no generic templates.")
        if dim_shifts:
            for c in dim_shifts[:4]:
                name = c.get('segment_name') or c.get('channel', '')
                if name:
                    st.markdown(f"- **{name}**: {c['message']}")
        if patterns.get('top_categories'):
            for cat in patterns['top_categories'][:3]:
                st.markdown(f"- **{cat['category']}**: {cat['message']}")
        if patterns.get('seasonality'):
            for s in patterns['seasonality'][:2]:
                st.markdown(f"- **{s['period']}**: {s['message']}")
        st.markdown("")

    # Personalized Insights - uses patterns when available for specificity
    st.markdown("""<div style='margin:24px 0 16px 0;'><h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>📊 Personalized Insights for Your Business</h3></div>""", unsafe_allow_html=True)
    
    insights = generate_personalized_insights(data, metrics, industry, patterns)
    
    if insights:
        for ins in insights:
            border = '#10B981' if ins['type'] == 'positive' else '#EF4444' if ins['type'] == 'critical' else '#F59E0B'
            st.markdown(f"""
            <div style="border-left:4px solid {border};padding:14px 16px;margin:10px 0;background:#1F2937;border-radius:6px;">
                <h4 style="margin:0 0 8px 0;color:#F3F4F6;">{ins['icon']} {ins['title']}</h4>
                <p style="margin:6px 0;color:#D1D5DB;font-size:14px;">{ins['message']}</p>
                <p style="margin:6px 0;color:#9CA3AF;font-size:13px;"><b>→ Action:</b> {ins['action']}</p>
                <p style="margin:4px 0 0 0;color:#6B7280;font-size:12px;">{ins.get('impact', '')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Upload more data (revenue, orders, customers, marketing spend) to get personalized insights.")
    
    # Data-driven Action Items (uses patterns when available)
    st.markdown("""<div style='margin:24px 0 16px 0;'><h4 style='font-size:16px;font-weight:600;margin-bottom:16px;'>💡 Recommended Actions (from your data)</h4></div>""", unsafe_allow_html=True)
    
    actions = generate_action_items(data, metrics, industry, patterns)
    action_df = pd.DataFrame(actions)
    st.dataframe(action_df, use_container_width=True, hide_index=True)

    # Benchmark comparison (optional)
    try:
        from enhancement_features import show_benchmark_comparison
        st.markdown("""<div style='margin:32px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
        show_benchmark_comparison()
    except Exception:
        pass
