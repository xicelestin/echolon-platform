import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from advanced_components import WhatIfAnalysis

def render_whatif_page():
    """Render What-If Scenario Planner page"""
    
    # Page header
    st.markdown("""
    <div style='margin-bottom: 32px;'>
        <h1 style='font-size: 32px; font-weight: 700; margin: 0 0 8px 0; color: #ffffff;'>
            What-If Scenario Planner
        </h1>
        <p style='font-size: 14px; color: #9ca3af; margin: 0;'>
            Model different business scenarios and understand financial impact
        </p>
        <div style='margin-top: 16px; padding: 12px 16px; background: #1f2937; border-radius: 8px; border-left: 3px solid #3b82f6;'>
            <span style='color: #3b82f6; font-weight: 600; font-size: 12px;'>LIVE DATA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Scenario Controls
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Scenario Parameters</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        revenue_growth = st.slider(
            "Revenue Growth (%)",
            -20, 50, 15,
            help="Expected monthly revenue growth rate"
        )
    with col2:
        churn_rate = st.slider(
            "Churn Rate (%)",
            0, 10, 3,
            help="Customer monthly churn rate"
        )
    with col3:
        cac_change = st.slider(
            "CAC Change (%)",
            -30, 50, 0,
            help="Customer acquisition cost adjustment"
        )
    
    col4, col5, col6 = st.columns(3)
    with col4:
        ltv_multiplier = st.slider(
            "LTV Multiplier",
            0.5, 2.0, 1.0,
            step=0.1,
            help="Adjust lifetime value assumptions"
        )
    with col5:
        opex_growth = st.slider(
            "OpEx Growth (%)",
            -10, 40, 5,
            help="Operating expense growth rate"
        )
    with col6:
        market_expansion = st.slider(
            "Market Expansion (%)",
            0, 100, 20,
            help="New market penetration rate"
        )
    
    # Generate scenarios
    scenarios = WhatIfAnalysis.generate_scenarios(
        revenue_growth=revenue_growth,
        churn_rate=churn_rate,
        cac_change=cac_change,
        ltv_multiplier=ltv_multiplier,
        opex_growth=opex_growth,
        market_expansion=market_expansion
    )
    
    # Scenario comparison metrics
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Scenario Comparison</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Best case
    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
            <p style='color: rgba(255,255,255,0.8); font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>BEST CASE</p>
            <p style='color: #ffffff; font-size: 24px; margin: 0 0 4px 0; font-weight: 700;'>${scenarios['best_case']['revenue']:,.0f}</p>
            <p style='color: rgba(255,255,255,0.7); font-size: 12px; margin: 0; font-weight: 500;'>12-Month Revenue</p>
            <p style='color: rgba(255,255,255,0.6); font-size: 11px; margin: 8px 0 0 0;'>+ {scenarios['best_case']['growth']:.1f}% growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Expected case
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
            <p style='color: rgba(255,255,255,0.8); font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>EXPECTED</p>
            <p style='color: #ffffff; font-size: 24px; margin: 0 0 4px 0; font-weight: 700;'>${scenarios['expected']['revenue']:,.0f}</p>
            <p style='color: rgba(255,255,255,0.7); font-size: 12px; margin: 0; font-weight: 500;'>12-Month Revenue</p>
            <p style='color: rgba(255,255,255,0.6); font-size: 11px; margin: 8px 0 0 0;'>+ {scenarios['expected']['growth']:.1f}% growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Worst case
    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
            <p style='color: rgba(255,255,255,0.8); font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>WORST CASE</p>
            <p style='color: #ffffff; font-size: 24px; margin: 0 0 4px 0; font-weight: 700;'>${scenarios['worst_case']['revenue']:,.0f}</p>
            <p style='color: rgba(255,255,255,0.7); font-size: 12px; margin: 0; font-weight: 500;'>12-Month Revenue</p>
            <p style='color: rgba(255,255,255,0.6); font-size: 11px; margin: 8px 0 0 0;'>+ {scenarios['worst_case']['growth']:.1f}% growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Break-even analysis
    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
            <p style='color: rgba(255,255,255,0.8); font-size: 12px; margin: 0 0 8px 0; font-weight: 600;'>PROFITABILITY</p>
            <p style='color: #ffffff; font-size: 24px; margin: 0 0 4px 0; font-weight: 700;'>{scenarios['profitability_months']:.0f} Mo</p>
            <p style='color: rgba(255,255,255,0.7); font-size: 12px; margin: 0; font-weight: 500;'>To Break Even</p>
            <p style='color: rgba(255,255,255,0.6); font-size: 11px; margin: 8px 0 0 0;'>Expected scenario</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='border-top: 1px solid #374151; margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Revenue projection chart
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Revenue Projection</h3>", unsafe_allow_html=True)
    
    months = np.arange(1, 13)
    base_revenue = 50000
    
    best_projection = [base_revenue * (1 + revenue_growth/100 * 0.8) ** m for m in months]
    expected_projection = [base_revenue * (1 + revenue_growth/100 * 0.5) ** m for m in months]
    worst_projection = [base_revenue * (1 + revenue_growth/100 * 0.2) ** m for m in months]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=best_projection, mode='lines+markers',
                             name='Best Case', line=dict(color='#10b981', width=3),
                             fill='tozeroy', fillcolor='rgba(16,185,129,0.1)'))
    fig.add_trace(go.Scatter(x=months, y=expected_projection, mode='lines+markers',
                             name='Expected', line=dict(color='#3b82f6', width=3),
                             fill='tozeroy', fillcolor='rgba(59,130,246,0.1)'))
    fig.add_trace(go.Scatter(x=months, y=worst_projection, mode='lines+markers',
                             name='Worst Case', line=dict(color='#ef4444', width=3),
                             fill='tozeroy', fillcolor='rgba(239,68,68,0.1)'))
    
    fig.update_layout(
        title=None,
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        plot_bgcolor='rgba(31,41,55,0.5)',
        paper_bgcolor='rgba(31,41,55,0)',
        font=dict(color='#ffffff'),
        height=400,
        margin=dict(t=20, b=50, l=50, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div style='border-top: 1px solid #374151; margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Impact analysis
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Financial Impact Analysis</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Profitability impact
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>Profitability Impact</h4>", unsafe_allow_html=True)
        
        impact_data = pd.DataFrame({
            'Scenario': ['Best Case', 'Expected', 'Worst Case'],
            'Annual Revenue': [scenarios['best_case']['revenue'], scenarios['expected']['revenue'], scenarios['worst_case']['revenue']],
            'Net Margin': [scenarios['best_case'].get('margin', 38), scenarios['expected'].get('margin', 28), scenarios['worst_case'].get('margin', 15)],
            'Annual Profit': [scenarios['best_case']['revenue'] * 0.38, scenarios['expected']['revenue'] * 0.28, scenarios['worst_case']['revenue'] * 0.15]
        })
        
        st.dataframe(impact_data, use_container_width=True, hide_index=True)
    
    with col2:
        # Customer impact
        st.markdown("<h4 style='color: #ffffff; margin-bottom: 16px;'>Customer Metrics</h4>", unsafe_allow_html=True)
        
        customer_data = pd.DataFrame({
            'Scenario': ['Best Case', 'Expected', 'Worst Case'],
            'LTV': [450, 380, 280],
            'CAC': [85 * (1 + cac_change/100), 95 * (1 + cac_change/100), 105 * (1 + cac_change/100)],
            'LTV/CAC': [
                450 / (85 * (1 + cac_change/100)),
                380 / (95 * (1 + cac_change/100)),
                280 / (105 * (1 + cac_change/100))
            ]
        })
        
        st.dataframe(customer_data, use_container_width=True, hide_index=True)
    
    st.markdown("<div style='border-top: 1px solid #374151; margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Churn analysis
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Churn Impact Analysis</h3>", unsafe_allow_html=True)
    
    churn_scenarios = {
        0: {'label': 'Optimistic (0% churn)', 'color': '#10b981'},
        churn_rate: {'label': f'Current ({churn_rate}% churn)', 'color': '#3b82f6'},
        churn_rate * 1.5: {'label': f'Pessimistic ({churn_rate*1.5:.1f}% churn)', 'color': '#ef4444'}
    }
    
    months_projection = np.arange(1, 25)
    initial_customers = 1000
    
    fig_churn = go.Figure()
    for churn, scenario_info in churn_scenarios.items():
        customers = [initial_customers * ((1 - churn/100) ** m) for m in months_projection]
        fig_churn.add_trace(go.Scatter(x=months_projection, y=customers, mode='lines',
                                       name=scenario_info['label'], 
                                       line=dict(color=scenario_info['color'], width=2)))
    
    fig_churn.update_layout(
        title=None,
        xaxis_title="Month",
        yaxis_title="Active Customers",
        hovermode='x unified',
        plot_bgcolor='rgba(31,41,55,0.5)',
        paper_bgcolor='rgba(31,41,55,0)',
        font=dict(color='#ffffff'),
        height=400,
        margin=dict(t=20, b=50, l=50, r=20)
    )
    st.plotly_chart(fig_churn, use_container_width=True)
    
    st.markdown("<div style='border-top: 1px solid #374151; margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Key insights
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Key Insights & Recommendations</h3>", unsafe_allow_html=True)
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown(f"""
        <div style='background: rgba(59,130,246,0.1); border-radius: 8px; padding: 20px; border-left: 3px solid #3b82f6;'>
            <h4 style='color: #3b82f6; margin-top: 0;'>Revenue Opportunity</h4>
            <p style='color: #ffffff; margin: 0; font-size: 14px;'>
                By optimizing parameters with {revenue_growth}% growth and managing churn at {churn_rate}%, 
                your expected 12-month revenue reaches <strong>${scenarios['expected']['revenue']:,.0f}</strong>.
            </p>
            <p style='color: #9ca3af; margin: 8px 0 0 0; font-size: 12px;'>
                This represents a potential upside of <strong>${scenarios['best_case']['revenue'] - scenarios['expected']['revenue']:,.0f}</strong> 
                in best-case scenario.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: rgba(239,68,68,0.1); border-radius: 8px; padding: 20px; border-left: 3px solid #ef4444; margin-top: 16px;'>
            <h4 style='color: #ef4444; margin-top: 0;'>Risk Mitigation</h4>
            <p style='color: #ffffff; margin: 0; font-size: 14px;'>
                Downside scenario with {churn_rate*1.5:.1f}% churn yields <strong>${scenarios['worst_case']['revenue']:,.0f}</strong> revenue.
            </p>
            <p style='color: #9ca3af; margin: 8px 0 0 0; font-size: 12px;'>
                Implement retention programs to keep churn below {churn_rate}% and secure profitability.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with insights_col2:
        st.markdown(f"""
        <div style='background: rgba(16,185,129,0.1); border-radius: 8px; padding: 20px; border-left: 3px solid #10b981;'>
            <h4 style='color: #10b981; margin-top: 0;'>Profitability Timeline</h4>
            <p style='color: #ffffff; margin: 0; font-size: 14px;'>
                Expected case reaches break-even profitability by month {scenarios['profitability_months']:.0f}.
            </p>
            <p style='color: #9ca3af; margin: 8px 0 0 0; font-size: 12px;'>
                Cumulative profit by end of year: <strong>${scenarios['expected']['revenue'] * 0.28 / 12 * (12 - scenarios['profitability_months']):,.0f}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: rgba(245,158,11,0.1); border-radius: 8px; padding: 20px; border-left: 3px solid #f59e0b; margin-top: 16px;'>
            <h4 style='color: #f59e0b; margin-top: 0;'>CAC Optimization</h4>
            <p style='color: #ffffff; margin: 0; font-size: 14px;'>
                Current CAC adjustment: {cac_change:+.0f}%. Optimal LTV/CAC ratio maintained at {(380 / (95 * (1 + cac_change/100))):.1f}x.
            </p>
            <p style='color: #9ca3af; margin: 8px 0 0 0; font-size: 12px;'>
                Target ratio of 3.0x+ achievable with cost optimization initiatives.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='border-top: 1px solid #374151; margin: 32px 0;'></div>", unsafe_allow_html=True)
    
    # Action items
    st.markdown("<h3 style='margin-top: 32px; margin-bottom: 20px; color: #ffffff;'>Recommended Actions</h3>", unsafe_allow_html=True)
    
    actions = pd.DataFrame({
        'Action': [
            'Implement retention program',
            'Optimize acquisition channels',
            'Launch premium tier',
            'Expand to new markets',
            'Reduce operational costs'
        ],
        'Priority': ['Critical', 'High', 'High', 'Medium', 'Medium'],
        'Timeline': ['Immediate', 'Q1', 'Q1', 'Q2', 'Q3'],
        'Expected Impact': ['+5-8% revenue', '+3-5% customers', '+12-15% ARPU', '+20% market reach', '+8-10% margin']
    })
    
    st.dataframe(actions, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render_whatif_page()
