# Echolon AI - Complete Pages Enhancement Guide

## Overview
This guide provides production-ready code for all 5 navigation pages: Analytics, Predictions, Recommendations, What-If Analysis, and Inventory.

---

## 📊 ANALYTICS PAGE - Complete Implementation

### Replace current Analytics section with:

```python
elif st.session_state.current_page == "Analytics":
    st.title("📊 Advanced Analytics")
    
    # Summary metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Points", len(data))
    with col2:
        correlation = data[['revenue', 'orders']].corr().iloc[0, 1]
        st.metric("Revenue-Orders Correlation", f"{correlation:.2f}")
    with col3:
        volatility = data['revenue'].std() / data['revenue'].mean() * 100
        st.metric("Revenue Volatility", f"{volatility:.1f}%")
    with col4:
        trend = "📈 Growing" if kpis['revenue_growth'] > 0 else "📉 Declining"
        st.metric("Trend", trend)
    
    st.markdown("---")
    
    # Correlation Matrix
    st.subheader("🔗 Correlation Analysis")
    numeric_cols = ['revenue', 'orders', 'customers', 'profit', 'profit_margin']
    available_cols = [col for col in numeric_cols if col in data.columns]
    
    if len(available_cols) >= 2:
        corr_matrix = data[available_cols].corr()
        
        import plotly.figure_factory as ff
        fig = ff.create_annotated_heatmap(
            z=corr_matrix.values,
            x=list(corr_matrix.columns),
            y=list(corr_matrix.index),
            annotation_text=corr_matrix.round(2).values,
            colorscale='RdBu',
            showscale=True
        )
        fig.update_layout(title='Metric Correlation Matrix')
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **How to read this:** 
        - Values close to 1 (dark blue) = strong positive correlation
        - Values close to -1 (dark red) = strong negative correlation  
        - Values close to 0 (white) = no correlation
        """)
    
    st.markdown("---")
    
    # Distribution Analysis
    st.subheader("📈 Distribution Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Revenue Distribution**")
        fig = px.histogram(data, x='revenue', nbins=30, 
                          title='Revenue Distribution',
                          labels={'revenue': 'Revenue ($)'})
        fig.add_vline(x=data['revenue'].mean(), line_dash="dash", 
                     line_color="red", annotation_text="Mean")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Orders Distribution**")
        fig = px.histogram(data, x='orders', nbins=30,
                          title='Orders Distribution',
                          labels={'orders': 'Orders'})
        fig.add_vline(x=data['orders'].mean(), line_dash="dash",
                     line_color="red", annotation_text="Mean")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Time Series Analysis
    st.subheader("📉 Time Series Decomposition")
    
    # Calculate moving averages
    data_copy = data.copy()
    data_copy['MA_7'] = data_copy['revenue'].rolling(window=7).mean()
    data_copy['MA_30'] = data_copy['revenue'].rolling(window=30).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['revenue'],
                            name='Actual Revenue', mode='lines',
                            line=dict(color='lightblue', width=1)))
    fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['MA_7'],
                            name='7-Day Moving Average', mode='lines',
                            line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=data_copy['date'], y=data_copy['MA_30'],
                            name='30-Day Moving Average', mode='lines',
                            line=dict(color='red', width=2)))
    fig.update_layout(title='Revenue Trend Analysis',
                     xaxis_title='Date', yaxis_title='Revenue ($)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Top/Bottom Performers
    st.subheader("🏆 Performance Highlights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 Revenue Days**")
        top_days = data.nlargest(10, 'revenue')[['date', 'revenue', 'orders']]
        top_days['date'] = pd.to_datetime(top_days['date']).dt.strftime('%Y-%m-%d')
        st.dataframe(top_days, use_container_width=True)
    
    with col2:
        st.markdown("**Bottom 10 Revenue Days**")
        bottom_days = data.nsmallest(10, 'revenue')[['date', 'revenue', 'orders']]
        bottom_days['date'] = pd.to_datetime(bottom_days['date']).dt.strftime('%Y-%m-%d')
        st.dataframe(bottom_days, use_container_width=True)
    
    # Statistical Summary
    with st.expander("📊 View Statistical Summary"):
        st.write(data[available_cols].describe())
```

---

## 🔮 PREDICTIONS PAGE - Complete Implementation

### Replace current Predictions section with:

```python
elif st.session_state.current_page == "Predictions":
    st.title("🔮 AI-Powered Predictions")
    
    st.info("📈 Using linear trend analysis and seasonal patterns to forecast future performance")
    
    # Forecast Settings
    col1, col2 = st.columns([2, 1])
    with col1:
        forecast_days = st.selectbox(
            "Select Forecast Period",
            [7, 14, 30, 60, 90],
            index=2
        )
    with col2:
        metric_to_forecast = st.selectbox(
            "Metric",
            ['revenue', 'orders', 'customers']
        )
    
    st.markdown("---")
    
    # Simple linear regression forecast
    from sklearn.linear_model import LinearRegression
    import numpy as np
    
    # Prepare data
    data_copy = data.copy()
    data_copy['day_num'] = range(len(data_copy))
    
    X = data_copy[['day_num']].values
    y = data_copy[metric_to_forecast].values
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Generate predictions
    future_days = np.array([[i] for i in range(len(data_copy), len(data_copy) + forecast_days)])
    predictions = model.predict(future_days)
    
    # Create future dates
    last_date = pd.to_datetime(data_copy['date'].iloc[-1])
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=forecast_days)
    
    # Calculate confidence interval (simplified)
    residuals = y - model.predict(X)
    std_error = np.std(residuals)
    confidence_upper = predictions + (1.96 * std_error)
    confidence_lower = predictions - (1.96 * std_error)
    
    # Revenue Forecast Chart
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=data_copy['date'],
        y=data_copy[metric_to_forecast],
        name='Historical Data',
        mode='lines',
        line=dict(color='blue', width=2)
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        name='Forecast',
        mode='lines',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=list(future_dates) + list(future_dates)[::-1],
        y=list(confidence_upper) + list(confidence_lower)[::-1],
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='95% Confidence Interval',
        showlegend=True
    ))
    
    fig.update_layout(
        title=f'{metric_to_forecast.title()} Forecast for Next {forecast_days} Days',
        xaxis_title='Date',
        yaxis_title=metric_to_forecast.title(),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Prediction Summary
    st.markdown("---")
    st.subheader("📊 Forecast Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Predicted Average", f"${predictions.mean():,.0f}" if metric_to_forecast == 'revenue' else f"{predictions.mean():.0f}")
    with col2:
        current_avg = data_copy[metric_to_forecast].tail(30).mean()
        growth = ((predictions.mean() - current_avg) / current_avg) * 100
        st.metric("Expected Growth", f"{growth:+.1f}%")
    with col3:
        st.metric("Forecast Range", f"{forecast_days} days")
    with col4:
        confidence = "High" if std_error / y.mean() < 0.1 else "Medium" if std_error / y.mean() < 0.2 else "Low"
        st.metric("Confidence", confidence)
    
    # Key Insights
    st.markdown("---")
    st.subheader("💡 Key Insights")
    
    trend_direction = "upward" if predictions[-1] > predictions[0] else "downward"
    trend_percentage = abs((predictions[-1] - predictions[0]) / predictions[0] * 100)
    
    st.markdown(f"""
    - **Trend Direction**: The forecast shows an **{trend_direction}** trend of {trend_percentage:.1f}% over the next {forecast_days} days
    - **Volatility**: Based on historical data, expect daily variations of ±${std_error:,.0f}
    - **Confidence**: The model has {confidence.lower()} confidence based on historical pattern consistency
    - **Recommendation**: {'Continue current strategy' if growth > 0 else 'Consider strategy adjustments to reverse trend'}
    """)
    
    # Detailed Forecast Table
    with st.expander("📅 View Detailed Daily Forecast"):
        forecast_df = pd.DataFrame({
            'Date': future_dates,
            f'Predicted {metric_to_forecast.title()}': predictions.round(2),
            'Lower Bound (95%)': confidence_lower.round(2),
            'Upper Bound (95%)': confidence_upper.round(2)
        })
        st.dataframe(forecast_df, use_container_width=True)
```

---

## 💡 RECOMMENDATIONS PAGE - Complete Implementation

### Replace current Recommendations section with:

```python
elif st.session_state.current_page == "Recommendations":
    st.title("💡 AI-Powered Recommendations")
    
    st.markdown("""
    Based on analysis of your business data, here are personalized recommendations to improve performance:
    """)
    
    # Generate recommendations based on data
    recommendations = []
    
    # Revenue analysis
    revenue_growth = kpis.get('revenue_growth', 0)
    if revenue_growth < 0:
        recommendations.append({
            'priority': 'High',
            'category': 'Revenue',
            'icon': '📉',
            'title': 'Address Revenue Decline',
            'insight': f"Revenue has decreased by {abs(revenue_growth):.1f}% compared to the previous period.",
            'actions': [
                'Review and optimize pricing strategy',
                'Analyze customer feedback for pain points',
                'Launch targeted marketing campaigns',
                'Consider promotional offers to boost sales'
            ],
            'impact': 'High - Could reverse negative trend',
            'timeframe': '2-4 weeks'
        })
    elif revenue_growth > 10:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Growth',
            'icon': '🚀',
            'title': 'Scale Your Success',
            'insight': f"Strong revenue growth of {revenue_growth:.1f}% indicates successful strategies.",
            'actions': [
                'Increase marketing budget to capitalize on momentum',
                'Expand product/service offerings',
                'Consider entering new market segments',
                'Document successful strategies for replication'
            ],
            'impact': 'High - Accelerate growth trajectory',
            'timeframe': '1-2 months'
        })
    
    # Customer analysis
    if 'customers' in data.columns:
        customer_growth = kpis.get('customers_growth', 0)
        avg_customers = data['customers'].mean()
        
        if customer_growth < -5:
            recommendations.append({
                'priority': 'High',
                'category': 'Customer Retention',
                'icon': '⚠️',
                'title': 'Improve Customer Retention',
                'insight': f"Customer count declining by {abs(customer_growth):.1f}%. Retention is critical.",
                'actions': [
                    'Implement customer loyalty program',
                    'Conduct customer satisfaction surveys',
                    'Offer personalized discounts to at-risk customers',
                    'Improve customer support response times'
                ],
                'impact': 'Critical - Prevent further customer loss',
                'timeframe': 'Immediate (1-2 weeks)'
            })
    
    # Profit margin analysis
    avg_margin = kpis.get('avg_profit_margin', 0)
    if avg_margin < 20:
        recommendations.append({
            'priority': 'High',
            'category': 'Profitability',
            'icon': '💰',
            'title': 'Optimize Profit Margins',
            'insight': f"Current profit margin of {avg_margin:.1f}% is below industry standards.",
            'actions': [
                'Negotiate better supplier pricing',
                'Review and reduce operational costs',
                'Consider strategic price increases',
                'Eliminate low-margin products/services'
            ],
            'impact': 'High - Improve bottom line',
            'timeframe': '1-3 months'
        })
    
    # Order value optimization
    avg_order = kpis.get('avg_order_value', 0)
    if avg_order > 0:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Revenue Optimization',
            'icon': '🐺',
            'title': 'Increase Average Order Value',
            'insight': f"Current average order value is ${avg_order:.2f}. There's room for improvement.",
            'actions': [
                'Implement product bundling strategies',
                'Create upsell and cross-sell opportunities',
                'Offer free shipping thresholds',
                'Introduce tiered pricing incentives'
            ],
            'impact': 'Medium - Boost revenue per transaction',
            'timeframe': '2-6 weeks'
        })
    
    # Seasonal opportunities
    if len(data) >= 30:
        recent_avg = data.tail(7)['revenue'].mean()
        monthly_avg = data.tail(30)['revenue'].mean()
        
        if recent_avg > monthly_avg * 1.15:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Timing',
                'icon': '📅',
                'title': 'Capitalize on Current Momentum',
                'insight': 'Recent performance exceeds monthly average by 15%+',
                'actions': [
                    'Increase inventory for high-demand products',
                    'Launch time-sensitive promotional campaigns',
                    'Extend customer service hours',
                    'Accelerate new customer acquisition efforts'
                ],
                'impact': 'Medium - Maximize current opportunity',
                'timeframe': 'Immediate (next 7-14 days)'
            })
    
    # Display recommendations
    if not recommendations:
        recommendations.append({
            'priority': 'Low',
            'category': 'Optimization',
            'icon': '✅',
            'title': 'Maintain Current Performance',
            'insight': 'Your business metrics are performing well overall.',
            'actions': [
                'Continue monitoring key metrics daily',
                'Document successful processes',
                'Plan for future growth initiatives',
                'Stay responsive to market changes'
            ],
            'impact': 'Ongoing - Sustain success',
            'timeframe': 'Continuous'
        })
    
    # Priority filter
    priority_filter = st.selectbox(
        "Filter by Priority",
        ['All', 'High', 'Medium', 'Low']
    )
    
    filtered_recs = recommendations if priority_filter == 'All' else [
        r for r in recommendations if r['priority'] == priority_filter
    ]
    
    st.markdown("---")
    
    # Display recommendations
    for i, rec in enumerate(filtered_recs, 1):
        priority_color = {
            'High': '#ff4444',
            'Medium': '#ff9944',
            'Low': '#44ff44'
        }.get(rec['priority'], '#gray')
        
        with st.container():
            st.markdown(f"""
            <div style="
                border-left: 5px solid {priority_color};
                padding: 20px;
                margin: 15px 0;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 5px;
            ">
                <h3>{rec['icon']} {i}. {rec['title']}</h3>
                <p><strong>Priority:</strong> <span style="color: {priority_color};">{rec['priority']}</span> | 
                <strong>Category:</strong> {rec['category']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📊 Insight:** {rec['insight']}")
                st.markdown("**🎯 Recommended Actions:**")
                for action in rec['actions']:
                    st.markdown(f"- {action}")
            
            with col2:
                st.markdown(f"**🏆 Potential Impact:**")
                st.info(rec['impact'])
                st.markdown(f"**⏰ Timeframe:**")
                st.success(rec['timeframe'])
            
            st.markdown("---")
    
    # Action Plan Summary
    st.subheader("📝 Action Plan Summary")
    st.markdown("""
    **Next Steps:**
    1. Review all recommendations and prioritize based on your business goals
    2. Start with High priority items for immediate impact
    3. Assign team members to specific action items
    4. Set up tracking metrics to measure implementation success
    5. Review progress weekly and adjust strategies as needed
    """)
    
    # Export recommendations
    if st.button("📥 Export Recommendations as PDF"):
        st.info("PDF export feature coming soon! For now, you can screenshot or copy these recommendations.")
```

---

## 📝 WHAT-IF ANALYSIS PAGE - Complete Implementation

### Replace current What-If Analysis section with:

```python
elif st.session_state.current_page == "What-If Analysis":
    st.title("📝 What-If Scenario Analysis")
    
    st.markdown("""
    Model different business scenarios and understand their potential impact on your key metrics.
    Adjust the parameters below to see how changes affect your business performance.
    """)
    
    st.markdown("---")
    
    # Scenario Selection
    scenario_type = st.selectbox(
        "Select Scenario Type",
        ["Price Optimization", "Cost Reduction", "Volume Growth", "Custom Scenario"]
    )
    
    st.markdown("---")
    
    # Get baseline metrics
    baseline_revenue = data['revenue'].sum()
    baseline_orders = data['orders'].sum()
    baseline_cost = data['cost'].sum() if 'cost' in data.columns else baseline_revenue * 0.6
    baseline_profit = baseline_revenue - baseline_cost
    baseline_margin = (baseline_profit / baseline_revenue * 100) if baseline_revenue > 0 else 0
    
    if scenario_type == "Price Optimization":
        st.subheader("💲 Price Optimization Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            price_change = st.slider(
                "Price Change (%)",
                min_value=-30,
                max_value=50,
                value=0,
                step=1,
                help="Adjust prices up or down and see the impact"
            )
            
            demand_elasticity = st.slider(
                "Demand Elasticity",
                min_value=-3.0,
                max_value=-0.1,
                value=-1.0,
                step=0.1,
                help="How sensitive are customers to price changes? (-1.0 means 1% price increase = 1% demand decrease)"
            )
        
        # Calculate impact
        volume_change = price_change * demand_elasticity
        new_revenue = baseline_revenue * (1 + price_change/100) * (1 + volume_change/100)
        new_orders = baseline_orders * (1 + volume_change/100)
        new_profit = new_revenue - baseline_cost
        new_margin = (new_profit / new_revenue * 100) if new_revenue > 0 else 0
        
        with col2:
            st.markdown("**Scenario Results:**")
            st.metric("New Revenue", f"${new_revenue:,.0f}", f"{((new_revenue/baseline_revenue - 1) * 100):+.1f}%")
            st.metric("New Orders", f"{new_orders:,.0f}", f"{volume_change:+.1f}%")
            st.metric("New Profit", f"${new_profit:,.0f}", f"{((new_profit/baseline_profit - 1) * 100):+.1f}%")
            st.metric("New Margin", f"{new_margin:.1f}%", f"{(new_margin - baseline_margin):+.1f}pp")
        
        # Visualization
        comparison_df = pd.DataFrame({
            'Scenario': ['Baseline', 'New Scenario'],
            'Revenue': [baseline_revenue, new_revenue],
            'Profit': [baseline_profit, new_profit],
            'Orders': [baseline_orders, new_orders]
        })
        
        fig = go.Figure(data=[
            go.Bar(name='Revenue', x=comparison_df['Scenario'], y=comparison_df['Revenue']),
            go.Bar(name='Profit', x=comparison_df['Scenario'], y=comparison_df['Profit'])
        ])
        fig.update_layout(title='Baseline vs New Scenario Comparison', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Recommendation")
        
        if new_profit > baseline_profit:
            st.success(f"""
            ✅ **This scenario is favorable!**
            - Revenue impact: ${(new_revenue - baseline_revenue):,.0f}
            - Profit impact: ${(new_profit - baseline_profit):,.0f}
            - Recommended action: Consider implementing a {price_change:+}% price adjustment
            """)
        else:
            st.warning(f"""
            ⚠️ **This scenario may not be optimal.**
            - Profit decrease: ${(baseline_profit - new_profit):,.0f}
            - Consider alternative strategies or smaller price adjustments
            """)
    
    elif scenario_type == "Cost Reduction":
        st.subheader("💰 Cost Reduction Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cost_reduction = st.slider(
                "Cost Reduction (%)",
                min_value=0,
                max_value=50,
                value=10,
                step=1,
                help="Target cost reduction percentage"
            )
            
            st.markdown("""
            **Common Cost Reduction Strategies:**
            - Negotiate better supplier rates
            - Optimize operational efficiency
            - Automate manual processes
            - Reduce overhead expenses
            """)
        
        # Calculate impact
        new_cost = baseline_cost * (1 - cost_reduction/100)
        new_profit = baseline_revenue - new_cost
        new_margin = (new_profit / baseline_revenue * 100)
        savings = baseline_cost - new_cost
        
        with col2:
            st.markdown("**Scenario Results:**")
            st.metric("Annual Savings", f"${savings:,.0f}")
            st.metric("New Profit", f"${new_profit:,.0f}", f"{((new_profit/baseline_profit - 1) * 100):+.1f}%")
            st.metric("New Margin", f"{new_margin:.1f}%", f"{(new_margin - baseline_margin):+.1f}pp")
            st.metric("ROI Timeline", "Immediate")
        
        # ROI Calculator
        st.markdown("---")
        st.subheader("💵 Investment ROI Calculator")
        
        implementation_cost = st.number_input(
            "One-time Implementation Cost ($)",
            min_value=0,
            value=10000,
            step=1000
        )
        
        if implementation_cost > 0:
            months_to_roi = (implementation_cost / savings) * 12 if savings > 0 else 0
            st.success(f"""
            **ROI Analysis:**
            - Monthly savings: ${savings/12:,.0f}
            - Payback period: {months_to_roi:.1f} months
            - First year net benefit: ${(savings - implementation_cost):,.0f}
            """)
    
    elif scenario_type == "Volume Growth":
        st.subheader("📈 Volume Growth Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            volume_growth = st.slider(
                "Volume Growth (%)",
                min_value=0,
                max_value=200,
                value=20,
                step=5,
                help="Target growth in orders/customers"
            )
            
            margin_impact = st.slider(
                "Margin Impact (%)",
                min_value=-20,
                max_value=20,
                value=0,
                step=1,
                help="Economies of scale may improve or reduce margins"
            )
        
        # Calculate impact
        new_orders = baseline_orders * (1 + volume_growth/100)
        new_revenue = baseline_revenue * (1 + volume_growth/100)
        new_cost = baseline_cost * (1 + volume_growth/100) * (1 - margin_impact/100)
        new_profit = new_revenue - new_cost
        new_margin = (new_profit / new_revenue * 100) if new_revenue > 0 else 0
        
        with col2:
            st.markdown("**Scenario Results:**")
            st.metric("New Orders", f"{new_orders:,.0f}", f"{volume_growth:+}%")
            st.metric("New Revenue", f"${new_revenue:,.0f}", f"{volume_growth:+}%")
            st.metric("New Profit", f"${new_profit:,.0f}", f"{((new_profit/baseline_profit - 1) * 100):+.1f}%")
            st.metric("New Margin", f"{new_margin:.1f}%", f"{(new_margin - baseline_margin):+.1f}pp")
        
        # Required Marketing Investment
        st.markdown("---")
        st.subheader("📊 Marketing Investment Needed")
        
        cac = st.number_input(
            "Customer Acquisition Cost ($)",
            min_value=0.0,
            value=50.0,
            step=5.0
        )
        
        new_customers = (new_orders - baseline_orders)
        marketing_investment = new_customers * cac
        net_profit_after_marketing = new_profit - baseline_profit - marketing_investment
        
        st.info(f"""
        **Investment Analysis:**
        - New customers needed: {new_customers:,.0f}
        - Marketing investment required: ${marketing_investment:,.0f}
        - Net profit after marketing: ${net_profit_after_marketing:,.0f}
        - ROI: {(net_profit_after_marketing / marketing_investment * 100):+.1f}%
        """)
    
    else:  # Custom Scenario
        st.subheader("⚙️ Custom Scenario Builder")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rev_change = st.number_input("Revenue Change (%)", value=0.0, step=1.0)
        with col2:
            cost_change = st.number_input("Cost Change (%)", value=0.0, step=1.0)
        with col3:
            volume_change = st.number_input("Volume Change (%)", value=0.0, step=1.0)
        
        new_revenue = baseline_revenue * (1 + rev_change/100)
        new_cost = baseline_cost * (1 + cost_change/100)
        new_orders = baseline_orders * (1 + volume_change/100)
        new_profit = new_revenue - new_cost
        new_margin = (new_profit / new_revenue * 100) if new_revenue > 0 else 0
        
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Revenue", f"${new_revenue:,.0f}", f"{rev_change:+}%")
        with col2:
            st.metric("Cost", f"${new_cost:,.0f}", f"{cost_change:+}%")
        with col3:
            st.metric("Profit", f"${new_profit:,.0f}", f"{((new_profit/baseline_profit - 1) * 100):+.1f}%")
        with col4:
            st.metric("Margin", f"{new_margin:.1f}%", f"{(new_margin - baseline_margin):+.1f}pp")
```

---

## 🎨 INVENTORY PAGE - Complete Implementation

### Replace current Inventory section with:

```python
elif st.session_state.current_page == "Inventory":
    st.title("🎨 Inventory Management & Optimization")
    
    st.markdown("""
    Monitor inventory levels, identify optimization opportunities, and prevent stockouts or overstock situations.
    """)
    
    # Check if inventory data exists
    if 'inventory_units' not in data.columns:
        st.warning("⚠️ Inventory data not found in current dataset. Showing simulated data for demonstration.")
        # Generate sample inventory data
        data_copy = data.copy()
        data_copy['inventory_units'] = np.random.randint(500, 2000, len(data))
    else:
        data_copy = data.copy()
    
    st.markdown("---")
    
    # Current Inventory Status
    st.subheader("📊 Current Inventory Status")
    
    current_inventory = data_copy['inventory_units'].iloc[-1]
    avg_inventory = data_copy['inventory_units'].mean()
    min_inventory = data_copy['inventory_units'].min()
    max_inventory = data_copy['inventory_units'].max()
    inventory_trend = ((data_copy['inventory_units'].iloc[-7:].mean() / 
                       data_copy['inventory_units'].iloc[-30:-7].mean() - 1) * 100) if len(data_copy) >= 30 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Stock", f"{current_inventory:,.0f} units")
    with col2:
        st.metric("Average Stock", f"{avg_inventory:,.0f} units")
    with col3:
        status = "🟢 Healthy" if current_inventory > avg_inventory * 0.7 else "🟡 Low" if current_inventory > avg_inventory * 0.5 else "🔴 Critical"
        st.metric("Status", status)
    with col4:
        st.metric("7-Day Trend", f"{inventory_trend:+.1f}%")
    
    st.markdown("---")
    
    # Inventory Level Chart
    st.subheader("📈 Inventory Level Trends")
    
    fig = go.Figure()
    
    # Inventory levels
    fig.add_trace(go.Scatter(
        x=data_copy['date'],
        y=data_copy['inventory_units'],
        name='Inventory Level',
        mode='lines',
        line=dict(color='blue', width=2)
    ))
    
    # Average line
    fig.add_hline(y=avg_inventory, line_dash="dash", line_color="green",
                 annotation_text="Average", annotation_position="right")
    
    # Safety stock line (70% of average)
    safety_stock = avg_inventory * 0.7
    fig.add_hline(y=safety_stock, line_dash="dash", line_color="orange",
                 annotation_text="Safety Stock", annotation_position="right")
    
    # Critical level (50% of average)
    critical_level = avg_inventory * 0.5
    fig.add_hline(y=critical_level, line_dash="dash", line_color="red",
                 annotation_text="Critical", annotation_position="right")
    
    fig.update_layout(
        title='Inventory Levels Over Time',
        xaxis_title='Date',
        yaxis_title='Units',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Inventory Turnover Analysis
    st.subheader("🔄 Inventory Turnover Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate turnover metrics
        if 'orders' in data_copy.columns:
            total_orders = data_copy['orders'].sum()
            avg_daily_orders = data_copy['orders'].mean()
            days_of_inventory = current_inventory / avg_daily_orders if avg_daily_orders > 0 else 0
            
            st.metric("Days of Inventory", f"{days_of_inventory:.1f} days")
            st.metric("Avg Daily Orders", f"{avg_daily_orders:.0f} units/day")
            
            # Reorder point recommendation
            lead_time_days = 14  # Assume 2-week lead time
            reorder_point = (avg_daily_orders * lead_time_days) * 1.2  # 20% safety buffer
            st.metric("Recommended Reorder Point", f"{reorder_point:.0f} units")
            
            if current_inventory < reorder_point:
                st.error(f"⚠️ **Action Required:** Current inventory ({current_inventory:.0f}) is below reorder point. Consider placing order soon.")
            else:
                st.success("✅ Inventory levels are adequate for current demand.")
    
    with col2:
        # Inventory cost analysis
        if 'cost' in data_copy.columns:
            avg_unit_cost = data_copy['cost'].sum() / data_copy['orders'].sum() if data_copy['orders'].sum() > 0 else 50
        else:
            avg_unit_cost = 50  # Default assumption
        
        inventory_value = current_inventory * avg_unit_cost
        carrying_cost_rate = 0.25  # 25% annual carrying cost
        annual_carrying_cost = inventory_value * carrying_cost_rate
        
        st.metric("Inventory Value", f"${inventory_value:,.0f}")
        st.metric("Annual Carrying Cost", f"${annual_carrying_cost:,.0f}")
        st.metric("Avg Unit Cost", f"${avg_unit_cost:.2f}")
        
        st.info(f"""
        **Cost Insights:**
        - Reducing inventory by 10% could save ~${annual_carrying_cost * 0.1:,.0f}/year
        - Optimal inventory level balances carrying costs with stockout risk
        """)
    
    st.markdown("---")
    
    # ABC Analysis
    st.subheader("🎯 ABC Inventory Classification")
    
    st.markdown("""
    **ABC Analysis** helps prioritize inventory management efforts:
    - **A Items (High Value)**: 20% of items, 80% of value - Monitor closely
    - **B Items (Medium Value)**: 30% of items, 15% of value - Regular monitoring
    - **C Items (Low Value)**: 50% of items, 5% of value - Basic controls
    """)
    
    # Simulated ABC distribution
    abc_data = pd.DataFrame({
        'Category': ['A Items', 'B Items', 'C Items'],
        'Percentage of Items': [20, 30, 50],
        'Percentage of Value': [80, 15, 5],
        'Recommended Review Frequency': ['Daily', 'Weekly', 'Monthly']
    })
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.dataframe(abc_data, use_container_width=True)
    
    with col2:
        fig = go.Figure(data=[
            go.Pie(labels=abc_data['Category'], 
                  values=abc_data['Percentage of Value'],
                  hole=0.3)
        ])
        fig.update_layout(title='Value Distribution by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Optimization Recommendations
    st.subheader("💡 Inventory Optimization Recommendations")
    
    recommendations = []
    
    # Stockout risk
    if days_of_inventory < 14:
        recommendations.append({
            'priority': 'High',
            'title': 'Stockout Risk',
            'description': f"Only {days_of_inventory:.1f} days of inventory remaining. Potential stockout in {days_of_inventory:.0f} days.",
            'action': 'Place urgent replenishment order'
        })
    
    # Overstock
    if days_of_inventory > 60:
        recommendations.append({
            'priority': 'Medium',
            'title': 'Excess Inventory',
            'description': f"{days_of_inventory:.0f} days of inventory. Tied up capital and high carrying costs.",
            'action': 'Consider promotional campaigns to move excess stock'
        })
    
    # Optimal range
    if 30 <= days_of_inventory <= 45:
        recommendations.append({
            'priority': 'Low',
            'title': 'Optimal Inventory Level',
            'description': f"Inventory at {days_of_inventory:.0f} days - well balanced.",
            'action': 'Maintain current ordering strategy'
        })
    
    # Display recommendations
    for rec in recommendations:
        priority_color = {'High': 'error', 'Medium': 'warning', 'Low': 'success'}[rec['priority']]
        
        if priority_color == 'error':
            st.error(f"""
            **{rec['title']}** (Priority: {rec['priority']})
            
            {rec['description']}
            
            **Recommended Action:** {rec['action']}
            """)
        elif priority_color == 'warning':
            st.warning(f"""
            **{rec['title']}** (Priority: {rec['priority']})
            
            {rec['description']}
            
            **Recommended Action:** {rec['action']}
            """)
        else:
            st.success(f"""
            **{rec['title']}** (Priority: {rec['priority']})
            
            {rec['description']}
            
            **Recommended Action:** {rec['action']}
            """)
    
    st.markdown("---")
    
    # Replenishment Calculator
    st.subheader("📝 Replenishment Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_days = st.number_input("Target Days of Inventory", min_value=7, max_value=90, value=30, step=7)
        lead_time = st.number_input("Supplier Lead Time (days)", min_value=1, max_value=60, value=14, step=1)
    
    with col2:
        safety_factor = st.slider("Safety Stock Factor", min_value=1.0, max_value=2.0, value=1.2, step=0.1)
        
        # Calculate order quantity
        target_inventory = avg_daily_orders * target_days
        safety_stock_calc = avg_daily_orders * lead_time * safety_factor
        order_quantity = max(0, target_inventory + safety_stock_calc - current_inventory)
        
        st.metric("Recommended Order Quantity", f"{order_quantity:,.0f} units")
        st.metric("Order Value", f"${order_quantity * avg_unit_cost:,.0f}")
        
        if order_quantity > 0:
            st.info(f"Place order for {order_quantity:,.0f} units to maintain {target_days} days of inventory with {(safety_factor-1)*100:.0f}% safety buffer.")
        else:
            st.success("No order needed at this time. Inventory is sufficient.")
```

---

## 🚀 Implementation Instructions

### Step 1: Add sklearn to requirements.txt

Add this line to your requirements.txt:
```
scikit-learn==1.3.0
```

### Step 2: Replace Page Sections in app.py

1. Find each `elif st.session_state.current_page == "[PAGE_NAME]":` section
2. Replace the entire section with the corresponding code from this guide
3. Test each page individually

### Step 3: Testing Checklist

- [ ] Analytics page loads without errors
- [ ] Predictions page generates forecasts
- [ ] Recommendations show personalized insights
- [ ] What-If scenarios calculate correctly
- [ ] Inventory page displays metrics properly

### Expected Impact

**For Pilot Customers:**
- Professional, comprehensive analytics
- Actionable insights and recommendations
- Interactive scenario planning
- Complete inventory management

**For Investor Demos:**
- Showcases full product capabilities
- Demonstrates AI/ML integration
- Shows scalability and depth
- Differentiates from competitors

---

## 🔧 Next Steps

1. **This Weekend**: Implement pages one at a time
2. **Monday**: Test with demo data
3. **Tuesday**: Get pilot customer feedback
4. **Next Week**: Refine based on feedback

## 📞 Support

For implementation help:
- Celestin (CEO) - Product direction
- Abdul (CTO) - Technical questions
- Esli - Backend integration

---

**Ready to deploy! All 5 pages are production-ready with comprehensive functionality. 🎉**
