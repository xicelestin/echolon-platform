"""Business Owner Fixes Module

Critical UX improvements to make Echolon AI valuable for non-technical business owners.
These fixes transform the app from a data tool into a business coaching platform.

Fixes:
1. Personalized onboarding message (replaces generic "no data" message)
2. Prominent demo banner (encourages first-time user engagement)
3. Health status badges (green/yellow/red) for KPI metrics
4. Context tooltips ("Why this matters" + action items)
5. Personalized insights (specific to user's data, not generic)
6. Tactical recommendations (HOW to implement, not just WHAT to do)
"""

import streamlit as st
import pandas as pd


def show_personalized_onboarding():
    """Replace generic 'no data' message with actionable onboarding."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 25px; border-radius: 12px; margin: 20px 0;'>
    <h2 style='color: white; margin: 0 0 15px 0;'>👋 Welcome to Echolon AI!</h2>
    <p style='color: white; font-size: 16px; margin: 0 0 20px 0;'>
    Get actionable business insights in 2 minutes. Choose one:
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 See It First (30 seconds)
        Load sample data to explore all features risk-free.
        Perfect for understanding what Echolon can do.
        
        **What you'll see:**
        - Real-time business metrics
        - Revenue forecasts
        - AI recommendations
        - What-if scenarios
        """)
        if st.button("📊 Load Demo Data", use_container_width=True, key="demo_btn_left"):
            st.session_state['load_demo'] = True
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 📤 Analyze Your Business (2 minutes)
        Upload your CSV to get personalized insights.
        
        **Required columns:**
        - `date` - When the sale happened
        - `value` - Revenue amount
        - `customer_id` (optional) - For segmentation
        
        [👉 **Scroll down to upload your CSV file**]
        """)


def get_health_badge(current_value, benchmark, metric_name=""):
    """Generate color-coded health status badge.
    
    Args:
        current_value: Current metric value
        benchmark: Target/benchmark value
        metric_name: Name of metric (for customization)
    
    Returns:
        Tuple of (emoji_badge, color, status_text)
    """
    if benchmark == 0:
        return "⚪ No Benchmark", "gray", "unknown"
    
    ratio = current_value / benchmark
    
    if ratio >= 0.8:
        return "🟢 Healthy", "green", "above_target"
    elif ratio >= 0.6:
        return "🟡 Warning", "orange", "below_target"
    else:
        return "🔴 Critical", "red", "far_below_target"


def render_kpi_with_context(metric_name, value, delta, benchmark, help_text):
    """Render KPI metric with health badge and contextual help.
    
    Example:
        render_kpi_with_context(
            metric_name="Total Revenue",
            value="$2.4M",
            delta="+12.5%",
            benchmark=2200000,
            help_text="..."
        )
    """
    col_badge, col_metric = st.columns([1, 4])
    
    with col_badge:
        try:
            numeric_value = float(value.replace('$', '').replace('M', '000000').replace('k', '000'))
            badge, color, status = get_health_badge(numeric_value, benchmark)
            st.markdown(f"<p style='font-size: 24px; margin: 0;'>{badge}</p>", unsafe_allow_html=True)
        except:
            st.markdown("<p style='font-size: 24px; margin: 0;'>⚪</p>", unsafe_allow_html=True)
    
    with col_metric:
        st.metric(metric_name, value, delta=delta, help=help_text)


def personalize_insights(df):
    """Generate personalized insights based on user's actual data.
    
    NOT generic - specific recommendations based on patterns in their data.
    """
    if df is None or len(df) == 0:
        return None
    
    insights = []
    
    # Calculate metrics
    total_revenue = df['value'].sum()
    avg_revenue = df['value'].mean()
    if len(df) >= 7:
        recent = df['value'].tail(7).mean()
        historical = df['value'].iloc[:-7].mean() if len(df) > 7 else recent
        recent_growth = ((recent - historical) / historical * 100) if historical > 0 else 0
    else:
        recent_growth = 0
    
    # Personalized insight 1: Revenue trend
    if recent_growth > 15:
        insights.append({
            'priority': '🔥 TOP PRIORITY',
            'title': 'Revenue is Growing Fast - Capitalize on It',
            'description': f'Your revenue grew {recent_growth:.1f}% week-over-week. This is EXCELLENT.',
            'action': 'Identify what caused this spike and replicate it. Document the strategy so you can repeat it.'
        })
    elif recent_growth < -10:
        insights.append({
            'priority': '🔴 URGENT',
            'title': 'Revenue Declining - Take Immediate Action',
            'description': f'Your revenue dropped {abs(recent_growth):.1f}% week-over-week.',
            'action': 'Emergency review: Did something change? Check marketing, competitors, customer feedback.'
        })
    
    # Personalized insight 2: Opportunity
    if total_revenue > 100000:
        insights.append({
            'priority': '⏰ DO NEXT',
            'title': f'You\'re at ${total_revenue:,.0f} Revenue - Time to Scale',
            'description': f'At your current growth rate, you\'re ready for expansion.',
            'action': f'Hire or outsource to handle {avg_revenue * 1.2:,.0f}/day volume without burning out.'
        })
    
    return insights


def show_tactical_recommendation(title, why_now, options, your_recommendation):
    """Display a tactical, specific recommendation (not generic advice).
    
    Example:
        show_tactical_recommendation(
            title="Market Expansion",
            why_now="Your market is saturated (3.8% conversion = market avg)",
            options=[
                {
                    'name': 'Dallas',
                    'budget': '$5k',
                    'timeline': '8 weeks',
                    'revenue': '+$60k/month',
                    'roi': '12x'
                },
                {...}
            ],
            your_recommendation="Dallas (best ROI + market size)"
        )
    """
    st.markdown(f"""
    ## {title}
    
    **Why now?**
    {why_now}
    
    ### Your Options (Pick 1):
    """)
    
    for i, option in enumerate(options, 1):
        cols = st.columns([2, 1, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{i}. {option['name']}**")
        with cols[1]:
            st.caption(f"Budget: {option['budget']}")
        with cols[2]:
            st.caption(f"Timeline: {option['timeline']}")
        with cols[3]:
            st.caption(f"Revenue: {option['revenue']}")
        with cols[4]:
            st.caption(f"ROI: {option['roi']}")
        st.divider()
    
    st.markdown(f"""\n💡 **My Recommendation:** {your_recommendation}""")


def render_what_if_presets():
    """Show quick preset scenarios instead of blank sliders."""
    st.subheader("Quick Scenarios")
    
    scenario_cols = st.columns(4)
    
    scenarios = [
        {"name": "🚀 Aggressive Growth", "description": "Spend 50% more on marketing"},
        {"name": "💰 Efficiency Mode", "description": "Cut costs while maintaining revenue"},
        {"name": "📉 Recession Scenario", "description": "Revenue drops 20%"},
        {"name": "🎯 Best Case", "description": "Everything goes perfectly"}
    ]
    
    for i, (col, scenario) in enumerate(zip(scenario_cols, scenarios)):
        with col:
            if st.button(scenario['name'], use_container_width=True, key=f"scenario_{i}"):
                st.session_state[f'selected_scenario'] = scenario['name']
                st.rerun()
            st.caption(scenario['description'])


if __name__ == "__main__":
    st.write("Business Owner Fixes Module Loaded")
    st.write("Import these functions into your dashboard pages.")
