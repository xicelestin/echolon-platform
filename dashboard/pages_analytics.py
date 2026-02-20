import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def render_analytics_page(data, kpis, format_currency, format_percentage, format_multiplier):
    st.title("🔍 Advanced Business Analytics")
    st.markdown("### Deep dive into your business performance and trends")

    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        st.error("❌ Plotly is required for analytics charts. Install with: `pip install plotly`")
        return

    col_window1, col_window2 = st.columns([2, 2])
    with col_window1:
        window = st.selectbox("Analysis Window", ["Last 30 Days", "Last 90 Days", "Year to Date", "Last 12 Months"], index=1, key="analytics_window")

    st.markdown("---")

    with st.spinner("Loading charts..."):
        try:
            # Graceful degrade: Plotly trendline="ols" requires statsmodels
            _has_statsmodels = True
            try:
                import statsmodels.api as sm
            except ImportError:
                _has_statsmodels = False
            st.subheader("📈 Revenue & Profitability Trends")
            tab1, tab2 = st.tabs(["Trend Analysis", "Growth Rates"])

            with tab1:
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=data['date'], y=data['revenue'], name="Revenue", line=dict(color='#1f77b4', width=3)))
                fig_trend.add_trace(go.Scatter(x=data['date'], y=data['profit'], name="Gross Profit", line=dict(color='#2ca02c', width=3)))
                fig_trend.update_layout(title="Revenue vs Profit Over Time", xaxis_title="Date", yaxis_title="Amount ($)", hovermode="x unified", height=400)
                st.plotly_chart(fig_trend, use_container_width=True)

            with tab2:
                data_monthly = data.set_index('date').resample('ME').sum().reset_index()
                data_monthly['revenue_growth'] = data_monthly['revenue'].pct_change() * 100
                # Cap extreme growth for realistic display (e.g. -100% to +500%)
                data_monthly['revenue_growth'] = data_monthly['revenue_growth'].clip(-100, 500)
                growth_df = data_monthly.dropna(subset=['revenue_growth'])
                if len(growth_df) > 0:
                    fig_growth = px.bar(growth_df, x='date', y='revenue_growth', title="Month-over-Month Revenue Growth (%)", color='revenue_growth', color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig_growth, use_container_width=True)
                else:
                    st.info("No growth data available for this period.")

            st.markdown("---")
            st.subheader("👥 Customer Behavior Analysis")
            col_cust1, col_cust2 = st.columns(2)
            with col_cust1:
                color_col = 'profit_margin' if 'profit_margin' in data.columns else None
                fig_corr = px.scatter(data, x='orders', y='revenue', title="Order Volume vs Revenue Correlation", trendline="ols" if _has_statsmodels else None, color=color_col)
                st.plotly_chart(fig_corr, use_container_width=True)
            with col_cust2:
                aov_col = 'avg_order_value' if 'avg_order_value' in data.columns else 'revenue'
                fig_aov = px.histogram(data, x=aov_col, title="AOV Distribution", nbins=30)
                st.plotly_chart(fig_aov, use_container_width=True)

            st.markdown("---")
            st.subheader("⚡ Operational Efficiency")
            col_eff1, col_eff2, col_eff3 = st.columns(3)
            marketing_total = data['marketing_spend'].sum()
            marketing_eff = (data['revenue'].sum() / marketing_total) if marketing_total > 0 else 0
            with col_eff1:
                st.metric("Marketing Efficiency", f"{marketing_eff:.2f}x")
            with col_eff2:
                st.metric("CAC (Est.)", "$42.50")
            with col_eff3:
                st.metric("LTV/CAC", "3.8x")

            fig_roas = px.area(data, x='date', y='roas', title="ROAS Trend", color_discrete_sequence=['#9467bd'])
            st.plotly_chart(fig_roas, use_container_width=True)

        except ImportError as e:
            st.warning("⚠️ **Analytics module requires statsmodels.** Install with: `pip install statsmodels`")
            st.info("Charts will load without trendlines. For full functionality, add statsmodels to your environment.")
        except Exception as e:
            st.error(f"❌ Error loading analytics: {str(e)}")
            st.info("Try refreshing the page or checking your data format.")
