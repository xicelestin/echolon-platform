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


# ===================================================================
# BUSINESS OWNER IMPROVEMENTS - Phase 1: Quick Wins
# ===================================================================

def show_tactical_recommendation(title, action, roi, time, priority, why):
    """
    Display actionable business recommendation with specific details.
    
    Args:
        title: Brief title of recommendation
        action: Specific action to take (what exactly to do)
        roi: Expected return on investment
        time: Time investment required
        priority: HIGH, MEDIUM, or LOW
        why: Why this matters for the business owner
    """
    priority_icons = {"HIGH": "🔥", "MEDIUM": "⚡", "LOW": "💡"}
    priority_colors = {"HIGH": "#ff4444", "MEDIUM": "#ffaa00", "LOW": "#4CAF50"}
    
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        border-left: 4px solid {priority_colors[priority]};
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
    ">
        <h4 style="margin: 0 0 12px 0; color: white;">
            {priority_icons[priority]} {title}
            <span style="
                background: {priority_colors[priority]};
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                margin-left: 8px;
            ">{priority}</span>
        </h4>
        
        <p style="margin: 8px 0;"><strong>🎯 Action:</strong> {action}</p>
        <p style="margin: 8px 0;"><strong>💰 Expected ROI:</strong> {roi}</p>
        <p style="margin: 8px 0;"><strong>⏱️ Time Investment:</strong> {time}</p>
        <p style="margin: 8px 0; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 4px;">
            <strong>🤔 Why this matters:</strong> {why}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_with_benchmark(icon, title, value, delta, benchmark_avg, benchmark_top, help_text=""):
    """
    Render KPI card with industry benchmarks for context.
    
    Args:
        icon: Emoji icon for the KPI
        title: Full descriptive title (e.g., "Customer Acquisition Cost (CAC)")
        value: Current value
        delta: Change from previous period
        benchmark_avg: Industry average value
        benchmark_top: Top 25% performance value
        help_text: Additional explanation
    """
    # Determine performance vs benchmarks
    try:
        val_num = float(str(value).replace("$", "").replace("%", "").replace(",", ""))
        avg_num = float(str(benchmark_avg).replace("$", "").replace("%", "").replace(",", ""))
        top_num = float(str(benchmark_top).replace("$", "").replace("%", "").replace(",", ""))
        
        # For metrics where lower is better (churn, CAC)
        if "churn" in title.lower() or "cac" in title.lower() or "cost" in title.lower():
            if val_num <= top_num:
                status = "✅ Excellent"
                color = "#90ee90"
            elif val_num <= avg_num:
                status = "⚠️ Good"
                color = "#ffaa00"
            else:
                status = "❌ Needs Improvement"
                color = "#ff4444"
        else:
            # For metrics where higher is better (revenue, conversion)
            if val_num >= top_num:
                status = "✅ Excellent"
                color = "#90ee90"
            elif val_num >= avg_num:
                status = "⚠️ Good"
                color = "#ffaa00"
            else:
                status = "❌ Needs Improvement"
                color = "#ff4444"
    except:
        status = ""
        color = "#888"
    
    st.markdown(f"""
    <div class="kpi-card" style="position: relative;">
        <div class="icon">{icon}</div>
        <div class="title">{title}</div>
        <div class="metric">{value}</div>
        <div class="delta">{delta}</div>
        
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 11px;">
            <div style="color: {color}; font-weight: 600; margin-bottom: 4px;">{status}</div>
            <div style="color: #888;">vs. Industry Avg: {benchmark_avg}</div>
            <div style="color: #888;">vs. Top 25%: {benchmark_top}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if help_text:
        st.caption(help_text)


def get_priority_score(metric_name, current_value, target_value, impact_dollars):
    """
    Calculate priority score for recommendations.
    
    Returns: "HIGH", "MEDIUM", or "LOW"
    """
    try:
        impact = float(str(impact_dollars).replace("$", "").replace(",", "").replace("K", "000"))
        
        if impact >= 10000:  # $10K+ impact
            return "HIGH"
        elif impact >= 3000:  # $3K+ impact
            return "MEDIUM"
        else:
            return "LOW"
    except:
        return "MEDIUM"


def generate_actionable_insights(kpis):
    """
    Generate insights with specific actions and dollar impact.
    More actionable than generic observations.
    """
    insights = []
    
    # Unit economics analysis
    ltv = kpis['revenue'] / kpis['customers'] if kpis['customers'] > 0 else 0
    ltv_cac_ratio = ltv / kpis['cac'] if kpis['cac'] > 0 else 0
    
    if ltv_cac_ratio < 2:
        monthly_loss = kpis['revenue'] * 0.08
        insights.append({
            'severity': '⚠️ CRITICAL',
            'title': 'Unit Economics Alert',
            'message': f"Your LTV:CAC ratio is {ltv_cac_ratio:.1f}x (Target: 3x+)",
            'impact': f"Losing ${monthly_loss:,.0f}/month on customer acquisition",
            'actions': [
                '🎯 Pause lowest 25% performing ad campaigns immediately',
                '💰 Add $30-50 upsell at checkout',
                '📧 Launch 3-email retention sequence'
            ],
            'timeline': 'Implement this week to improve ratio to 2.5x+ within 30 days'
        })
    elif ltv_cac_ratio < 3:
        insights.append({
            'severity': '⚡ OPPORTUNITY',
            'title': 'Improve Unit Economics',
            'message': f"Your LTV:CAC ratio is {ltv_cac_ratio:.1f}x (Target: 3x+)",
            'impact': f"Potential to save ${kpis['revenue'] * 0.05:,.0f}/month",
            'actions': [
                '📈 Test 10% price increase on new customers',
                '🔁 Implement referral program (15% discount)',
                '📊 Optimize ad targeting to reduce CAC'
            ],
            'timeline': 'Start testing next week'
        })
    else:
        insights.append({
            'severity': '✅ STRENGTH',
            'title': 'Excellent Unit Economics',
            'message': f"Your LTV:CAC ratio is {ltv_cac_ratio:.1f}x - Outstanding!",
            'impact': 'You can afford to invest more in growth',
            'actions': [
                '🚀 Scale up marketing budget by 30-50%',
                '🎯 Expand to new customer segments',
                '💼 Consider raising prices'
            ],
            'timeline': 'Your strong economics support aggressive growth'
        })
    
    # Churn analysis
    if kpis['churn'] > 5:
        annual_revenue_at_risk = kpis['revenue'] * kpis['churn'] / 100 * 12
        insights.append({
            'severity': '🚨 URGENT',
            'title': 'High Churn Rate',
            'message': f"{kpis['churn']:.1f}% monthly churn (Target: < 3%)",
            'impact': f"${annual_revenue_at_risk:,.0f}/year revenue at risk",
            'actions': [
                '📧 Call top 10 customers who churned this month',
                '🎯 Create win-back campaign (25% discount)',
                '📊 Survey all churned customers (find root cause)'
            ],
            'timeline': 'Start today - every day costs money'
        })
    elif kpis['churn'] < 2:
        insights.append({
            'severity': '✅ STRENGTH',
            'title': 'Excellent Retention',
            'message': f"{kpis['churn']:.1f}% churn - You're in the top 25% of SaaS companies!",
            'impact': 'Your customers love you - leverage this',
            'actions': [
                '🗣️ Ask happy customers for testimonials',
                '🤝 Launch referral program',
                '💰 Test price increase (they won\'t leave)'
            ],
            'timeline': 'Capitalize on this strength this month'
        })
    
    return insights


def display_actionable_insight(insight):
    """
    Display an insight in business owner friendly format.
    """
    severity_colors = {
        '🚨 URGENT': '#ff4444',
        '⚠️ CRITICAL': '#ff6600',
        '⚡ OPPORTUNITY': '#ffaa00',
        '✅ STRENGTH': '#4CAF50'
    }
    
    color = severity_colors.get(insight['severity'], '#888')
    
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
    ">
        <h3 style="margin: 0 0 8px 0; color: {color};">{insight['severity']} {insight['title']}</h3>
        <p style="font-size: 16px; margin: 8px 0;"><strong>{insight['message']}</strong></p>
        <p style="color: #ffaa00; margin: 8px 0;"><strong>💰 Impact:</strong> {insight['impact']}</p>
        
        <p style="margin: 16px 0 8px 0; font-weight: 600;">Quick actions to take:</p>
        <ul style="margin: 0; padding-left: 20px;">
    """, unsafe_allow_html=True)
    
    for action in insight['actions']:
        st.markdown(f"<li style='margin: 4px 0;'>{action}</li>", unsafe_allow_html=True)
    
    st.markdown(f"""
        </ul>
        <p style="margin: 16px 0 0 0; font-style: italic; color: #888;">
            ⏱️ {insight['timeline']}
        </p>
    </div>
    """, unsafe_allow_html=True)

