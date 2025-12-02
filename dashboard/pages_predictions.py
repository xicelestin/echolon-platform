"""AI Predictions page with advanced forecasting."""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from advanced_components import PredictionMetrics

def render_predictions_page():
    """Render the comprehensive AI Predictions page."""
    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:32px; font-weight:700; margin-bottom:5px'>AI Predictions</h1><p style='color:#9CA3AF; font-size:16px'>Forecast future trends with confidence intervals and trend analysis.</p></div>""", unsafe_allow_html=True)
    
    # Data upload notification
    st.markdown(
        f"""<div style='background:#F59E0B;color:#1F2937;border-radius:8px;padding:12px 16px;font-size:15px;margin-bottom:24px;'><b>📊 Demo Data</b> | Last updated: {datetime.now().strftime('%H:%M on %Y-%m-%d')}</div>""",
        unsafe_allow_html=True
    )
    
    # Forecast Parameters Section
    st.markdown("""<div style='margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>Forecast Parameters</h3></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric = st.selectbox(
            "📈 Select Metric",
            ["Revenue", "Growth Rate", "Churn Rate", "Customer Count", "Inventory"],
            index=0,
            key="pred_metric_select"
        )
    
    with col2:
        window = st.selectbox(
            "⏱️ Forecast Window",
            ["1 Month", "3 Months", "6 Months", "12 Months"],
            index=0,
            key="pred_window_select"
        )
    
    with col3:
        confidence = st.selectbox(
            "🎯 Confidence Level",
            ["80%", "90%", "95%", "99%"],
            index=2,
            key="pred_confidence_select"
        )
    
    # Generate Predictions Button
    st.markdown("""<div style='margin-bottom:20px; margin-top:10px;'></div>""", unsafe_allow_html=True)
    
    if st.button("🔮 Generate Predictions", type="primary", use_container_width=True):
        with st.spinner("Generating advanced forecast with confidence intervals..."):
            # Generate mock historical data
            historical_values = pd.Series(np.random.normal(100000, 15000, 30))
            
            # Generate forecast
            forecast_data = PredictionMetrics.generate_forecast_with_ci(
                historical_values,
                periods=12
            )
            
            # Display forecast chart
            st.markdown("""<div style='margin-top:30px; margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>Forecast Visualization</h3></div>""", unsafe_allow_html=True)
            
            fig = PredictionMetrics.plot_forecast_with_ci(
                historical_values,
                forecast_data,
                title=f"{metric} Forecast - {window}"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast Interpretation Panel
            st.markdown("""<div style='margin-top:30px; margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>📋 Forecast Interpretation</h3></div>""", unsafe_allow_html=True)
            
            # Calculate metrics for display
            current_value = historical_values.iloc[-1]
            forecast_end = forecast_data['forecast'][-1]
            change_pct = ((forecast_end - current_value) / current_value) * 100
            trend_strength = "Strong" if abs(change_pct) > 10 else "Moderate" if abs(change_pct) > 5 else "Weak"
            trend_dir = "upward" if change_pct > 0 else "downward"
            
            interpretation = f"""
            Based on the historical data and current market trends, the forecast indicates a **{trend_strength.lower()} {trend_dir} trend** 
            for {metric.lower()}. 
            
            **Key Findings:**
            - Current {metric.lower()}: **${current_value:,.0f}** (baseline)
            - Forecasted {metric.lower()} (end of {window}): **${forecast_end:,.0f}**
            - Expected change: **{change_pct:+.1f}%**
            - Confidence interval: **{confidence}**
            - Trend direction: **{forecast_data['trend_direction']}**
            
            **What This Means:**
            - The model has identified key drivers affecting your {metric.lower()}
            - Historical patterns suggest momentum will {('continue' if change_pct > 0 else 'reverse')}
            - Consider adjusting marketing, inventory, or pricing strategies accordingly
            """
            
            st.markdown(interpretation)
            
            # Key Metrics Cards
            st.markdown("""<div style='margin-top:30px; margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>Predicted KPIs</h3></div>""", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style='background:#1F2937;border-radius:8px;padding:16px;border:1px solid #374151;'>
                    <p style='color:#9CA3AF; font-size:12px; margin:0;'>Current Value</p>
                    <h3 style='color:#10B981; font-size:24px; font-weight:700; margin:8px 0 0 0;'>${current_value:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background:#1F2937;border-radius:8px;padding:16px;border:1px solid #374151;'>
                    <p style='color:#9CA3AF; font-size:12px; margin:0;'>Forecasted Value</p>
                    <h3 style='color:#3B82F6; font-size:24px; font-weight:700; margin:8px 0 0 0;'>${forecast_end:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                color = '#10B981' if change_pct > 0 else '#EF4444'
                st.markdown(f"""
                <div style='background:#1F2937;border-radius:8px;padding:16px;border:1px solid #374151;'>
                    <p style='color:#9CA3AF; font-size:12px; margin:0;'>Expected Change</p>
                    <h3 style='color:{color}; font-size:24px; font-weight:700; margin:8px 0 0 0;'>{change_pct:+.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style='background:#1F2937;border-radius:8px;padding:16px;border:1px solid #374151;'>
                    <p style='color:#9CA3AF; font-size:12px; margin:0;'>Confidence</p>
                    <h3 style='color:#F59E0B; font-size:24px; font-weight:700; margin:8px 0 0 0;'>{confidence}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Drivers Analysis
            st.markdown("""<div style='margin-top:30px; margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>📊 Drivers Analysis (Month-over-Month)</h3></div>""", unsafe_allow_html=True)
            
            drivers_data = {
                "Driver": ["Marketing Spend", "Customer Retention", "Average Order Value", "Marketing Efficiency", "Product Mix Change"],
                "Change": ["+18%", "+5%", "-2%", "+12%", "+3%"],
                "Impact on Forecast": ["+6%", "+2%", "-1%", "+4%", "+1%"]
            }
            drivers_df = pd.DataFrame(drivers_data)
            st.dataframe(drivers_df, use_container_width=True, hide_index=True)
            
            # Recommendations
            st.markdown("""<div style='margin-top:30px; margin-bottom:20px'><h3 style='font-size:18px; font-weight:600;'>💡 Recommended Actions</h3></div>""", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **✅ What's Working**
                - Marketing campaigns showing positive ROI
                - Customer retention improving
                - Continue current marketing initiatives
                """)
            
            with col2:
                st.markdown("""
                **⚠️ Areas to Monitor**
                - Average order value declining slightly
                - Watch for competitive pressure
                - Consider bundling or upsell strategies
                """)
