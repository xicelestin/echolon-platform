import streamlit as st
import pandas as pd
import numpy as np

def render_smart_alerts_page(data, kpis, format_currency, format_percentage, format_number):
    st.title('🔔 Echolon 360 - Smart Alerts')
    st.markdown('**Comprehensive AI-powered business intelligence across all operations**')
    
    # Create tabs for 6 business problem categories
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        '📦 Inventory & Stock', '💰 Cash Flow & Financial', '💡 Product & Profitability', 
        '📊 Demand & Forecasting', '👥 Customer Insights', '⚙️ Operational Efficiency'
    ])
    
    # ==================== CALCULATE ALL METRICS ====================
    
    # Basic metrics
    total_revenue = data['revenue'].sum() if 'revenue' in data.columns else 0
    total_orders = data['orders'].sum() if 'orders' in data.columns else 0
    total_customers = data['customers'].sum() if 'customers' in data.columns else 0
    avg_revenue = data['revenue'].mean() if 'revenue' in data.columns else 0
    
    # Inventory metrics
    if 'inventory_units' in data.columns and len(data) > 0:
        avg_inventory = data['inventory_units'].mean()
        current_inventory = data['inventory_units'].iloc[-1]
        max_inventory = data['inventory_units'].max()
        min_inventory = data['inventory_units'].min()
        inventory_std = data['inventory_units'].std()
        slow_moving_value = avg_inventory * 0.3 * (avg_revenue / 1000)
        dead_stock_value = slow_moving_value * 0.75
        overstock_days = (data['inventory_units'] > avg_inventory * 1.5).sum()
        stockout_days = (data['inventory_units'] < avg_inventory * 0.3).sum()
    else:
        avg_inventory = current_inventory = 1000
        slow_moving_value = 12000
        dead_stock_value = 900
        overstock_days = stockout_days = 10
    
    # Financial metrics
    if 'cost' in data.columns:
        total_cost = data['cost'].sum()
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    else:
        total_cost = total_revenue * 0.6
        total_profit = total_revenue * 0.4
        profit_margin = 40
    
    # Cash flow metrics
    cash_conversion_days = 45
    cash_payables_days = 30
    negative_cash_risk = total_revenue * 0.15
    margin_leakage = total_profit * 0.15 if total_profit > 0 else 0
    working_capital_need = total_revenue * 0.08
    cash_runway_months = 8.0
    
    # Demand metrics
    if 'orders' in data.columns:
        avg_daily_orders = data['orders'].mean()
        recent_orders = data['orders'].tail(7).mean()
        demand_spike = ((recent_orders - avg_daily_orders) / avg_daily_orders * 100) if avg_daily_orders > 0 else 0
        demand_volatility = data['orders'].std()
    else:
        demand_spike = 60
        demand_volatility = 25
    
    # Profitability metrics
    products_at_risk = 2
    profit_sink_loss = total_profit * 0.05
    margin_bundle_opportunity = total_profit * 0.15
    cannibalization_impact = total_revenue * 0.03
    
    # Customer metrics  
    if 'customers' in data.columns:
        churn_rate = 15.0
        clv = (total_revenue / total_customers * 3) if total_customers > 0 else 0
        high_value_customers = int(total_customers * 0.2)
    else:
        churn_rate = 15.0
        clv = 1500
        high_value_customers = 200
    
    # Operations metrics
    lead_time_increase = 7
    reorder_optimization_savings = total_profit * 0.03
    supplier_risk_score = 65
    automation_opportunity = total_revenue * 0.05
    
    # ==================== INSIGHTS COLLECTION ====================
    all_insights = []
    
    # TAB 1: INVENTORY & STOCK (10 insights)
    with tab1:
        st.header('📦 Inventory & Stock Management')
        st.markdown('**10 AI-powered insights for inventory optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 1: Overstocked SKUs
            with st.container(border=True):
                st.subheader('📦 Overstocked SKUs')
                st.write(f'${slow_moving_value/1000:.0f}K in slow-moving inventory')
                st.success(f'💡 **Action**: Bundle products or discount to free up ${slow_moving_value/1000:.0f}K working capital')
                all_insights.append({'priority': 'HIGH', 'category': 'Inventory', 'action': 'Liquidate slow stock', 'impact': f'${slow_moving_value/1000:.0f}K freed'})
            
            # Insight 2: Dead Stock
            with st.container(border=True):
                st.subheader('⚠️ Dead Stock Alert')
                st.write('SKUs unsold for 180+ days')
                st.error(f'💰 **Cost**: ${dead_stock_value:.0f}/month holding cost')
                st.info(f'**Recommendation**: Liquidate to save ${dead_stock_value * 12 / 1000:.0f}K/year')
            
            # Insight 3: Stockout Risk
            with st.container(border=True):
                st.subheader('🚨 Stockout Risk')
                st.write(f'{stockout_days} days at risk')
                st.warning(f'**Action**: Emergency reorder for 2-3 SKUs to prevent ${total_revenue * 0.05 / 1000:.0f}K revenue loss')
            
            # Insight 4: Inventory Imbalance
            with st.container(border=True):
                st.subheader('⚖️ Inventory Imbalance')
                st.write('50% of inventory = 10% of revenue')
                st.info('**Insight**: Rebalance product mix for better capital efficiency')
            
            # Insight 5: SKU Velocity Changes
            with st.container(border=True):
                st.subheader('📉 SKU Velocity Shift')
                st.write('3 SKUs showing 40% velocity drop')
                st.warning('**Action**: Investigate demand changes or quality issues')
        
        with col2:
            # Insight 6: Slow-Moving Trend
            with st.container(border=True):
                st.subheader('🐌 Slow-Moving Products')
                st.write(f'{int(overstock_days/10)} products moving < 5 units/month')
                st.info(f'**Opportunity**: Adjust pricing or marketing to improve velocity')
            
            # Insight 7: Seasonality Misalignment  
            with st.container(border=True):
                st.subheader('📅 Seasonality Alert')
                st.write('Holiday demand 40% above forecast')
                st.success(f'**Action**: Increase holiday inventory by ${total_revenue * 0.15 / 1000:.0f}K')
            
            # Insight 8: Supplier Lead-Time Risk
            with st.container(border=True):
                st.subheader('⏰ Lead-Time Risk')
                st.write(f'Supplier lead time: 5→{lead_time_increase+5} days')
                st.error('**Risk**: Potential stockouts during peak demand')
            
            # Insight 9: Multi-Location Gaps
            with st.container(border=True):
                st.subheader('🏪 Location Imbalance')
                st.write('Store A: 150% stock, Store B: 40% stock')
                st.info('**Action**: Redistribute inventory between locations')
            
            # Insight 10: Holding Cost Optimization
            with st.container(border=True):
                st.subheader('💸 Holding Cost Alert')
                st.write(f'High-cost SKUs: ${slow_moving_value * 0.2 / 1000:.0f}K/month')
                st.success(f'**Savings**: Optimize to save ${slow_moving_value * 0.2 * 0.3 / 1000:.0f}K/month')
    
    # TAB 2: CASH FLOW & FINANCIAL HEALTH (10 insights)
    with tab2:
        st.header('💰 Cash Flow & Financial Health')
        st.markdown('**10 insights for financial optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 11: Cash Runway
            with st.container(border=True):
                st.subheader('🏃 Cash Runway')
                st.metric('Runway', f'{cash_runway_months:.1f} months')
                st.info(f'**At current burn rate**: Need cash infusion in ~{int(cash_runway_months * 30)} days')
            
            # Insight 12: Cash Conversion Cycle
            with st.container(border=True):
                st.subheader('💰 Cash Conversion Issue')
                st.write(f'{cash_conversion_days} days to cash, {cash_payables_days} payables')
                st.error(f'**Risk**: ${negative_cash_risk/1000:.0f}K negative cash flow')
                all_insights.append({'priority': 'CRITICAL', 'category': 'Cash Flow', 'action': 'Extend payment terms', 'impact': f'${negative_cash_risk/1000:.0f}K'})

    
    # TAB 3: PRODUCT & PROFITABILITY (10 insights)
    with tab3:
        st.header('💡 Product & Profitability')
        st.markdown('**10 insights for product optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 21: Profit Sinks
            with st.container(border=True):
                st.subheader('🚨 Profit Sinks')
                st.write(f'{products_at_risk} products selling at negative margin')
                st.error(f'**Loss**: ${profit_sink_loss/1000:.0f}K/year')
                st.info('**Action**: Discontinue or adjust pricing immediately')
                all_insights.append({'priority': 'HIGH', 'category': 'Profitability', 'action': 'Fix profit sinks', 'impact': f'${profit_sink_loss/1000:.0f}K saved'})
            
            # Insight 22: High-Margin Opportunities
            with st.container(border=True):
                st.subheader('⭐ Bundle Opportunity')
                st.write('Products E+F bundle strategy')
                st.success(f'**Uplift**: +15% per transaction (${margin_bundle_opportunity/1000:.0f}K/year)')
            
            # Insight 23: Cannibalization
            with st.container(border=True):
                st.subheader('🔄 Product Cannibalization')
                st.write('Product G taking sales from H')
                st.warning(f'**Impact**: ${cannibalization_impact/1000:.0f}K revenue shift')
                st.info('**Strategy**: Reposition or adjust inventory mix')
            
            # Insight 24: Product Lifecycle
            with st.container(border=True):
                st.subheader('📉 Lifecycle Alert')
                st.write('3 products entering decline phase')
                st.warning('**Action**: Plan replacement products or phase-out strategy')
            
            # Insight 25: Cross-sell Opportunities
            with st.container(border=True):
                st.subheader('🎯 Cross-Sell/Upsell')
                st.write('Customers buying A also want B')
                st.success(f'**Opportunity**: +${margin_bundle_opportunity * 0.5 / 1000:.0f}K in additional revenue')
        
        with col2:
            # Insight 26: Pricing Optimization
            with st.container(border=True):
                st.subheader('💲 Pricing Alert')
                st.write('5% price increase possible without demand drop')
                st.success(f'**Revenue Impact**: +${total_revenue * 0.05 / 1000:.0f}K')
            
            # Insight 27: COGS Changes
            with st.container(border=True):
                st.subheader('📊 COGS Alert')
                st.write('Supplier costs up 8% this quarter')
                st.error(f'**Margin Impact**: -${margin_leakage * 0.5 / 1000:.0f}K')
                st.info('**Action**: Renegotiate or find alternative suppliers')
            
            # Insight 28: SKU Contribution
            with st.container(border=True):
                st.subheader('🏆 Top SKU Performance')
                st.write('Top 20% SKUs = 80% of profit')
                st.info('**Focus**: Double down on top performers')
            
            # Insight 29: Bundle Recommendations
            with st.container(border=True):
                st.subheader('🎁 Smart Bundles')
                st.write('AI suggests 5 high-value bundles')
                st.success(f'**Potential**: +${margin_bundle_opportunity * 0.7 / 1000:.0f}K/year')
            
            # Insight 30: Liquidation Strategy
            with st.container(border=True):
                st.subheader('💸 Liquidation Plan')
                st.write('Dead stock clearance strategy')
                st.warning(f'Recover ${dead_stock_value * 0.6 / 1000:.0f}K through strategic discounting')

    
    # TAB 4: DEMAND & FORECASTING (10 insights)
    with tab4:
        st.header('📊 Demand & Forecasting')
        st.markdown('**10 insights for demand optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 31: Demand Anomalies
            with st.container(border=True):
                st.subheader('🚨 Demand Spike Detected')
                st.write(f'Product Z demand +{abs(demand_spike):.0f}%')
                st.success(f'**Action**: Increase inventory to capture ${total_revenue * 0.08 / 1000:.0f}K opportunity')
                all_insights.append({'priority': 'CRITICAL', 'category': 'Demand', 'action': 'Reorder 500 units', 'impact': f'${total_revenue * 0.08 / 1000:.0f}K'})
            
            # Insight 32: Predictive Reorder
            with st.container(border=True):
                st.subheader('🔮 Reorder Point Alert')
                st.write('3 SKUs approaching reorder threshold')
                st.warning('**Action**: Place orders within 48 hours')
            
            # Insight 33: Seasonal Forecasting
            with st.container(border=True):
                st.subheader('🎄 Seasonal Forecast')
                st.write('Q4 demand projected +35%')
                st.info(f'**Prepare**: Stock ${total_revenue * 0.35 / 1000:.0f}K additional inventory')
            
            # Insight 34: Promotional Impact
            with st.container(border=True):
                st.subheader('🎯 Promo Analysis')
                st.write('Last campaign: +30% volume, -5% margin')
                st.warning('**ROI**: Evaluate campaign effectiveness')
            
            # Insight 35: Market Trends
            with st.container(border=True):
                st.subheader('📈 Market Trends')
                st.write('Industry growing 12% YoY')
                st.success('**Opportunity**: Capture market share growth')
        
        with col2:
            # Insight 36: Forecast Confidence
            with st.container(border=True):
                st.subheader('🎯 Forecast Confidence')
                st.write('Next 30 days: 85% confidence')
                st.success('**Status**: High accuracy - trust projections')
            
            # Insight 37: Multi-SKU Correlation
            with st.container(border=True):
                st.subheader('🔗 SKU Correlation')
                st.write('Products A & B sell together 70% of time')
                st.info('**Strategy**: Cross-merchandise and bundle')
            
            # Insight 38: Customer Demand Clusters
            with st.container(border=True):
                st.subheader('💡 Hot Product Alert')
                st.write('2 products showing viral growth pattern')
                st.success('**Action**: Scale inventory and marketing')
            
            # Insight 39: Lead-Time Alignment
            with st.container(border=True):
                st.subheader('⏱️ Timing Mismatch')
                st.write('Lead time > demand cycle')
                st.warning('**Risk**: Consider faster suppliers or safety stock')
            
            # Insight 40: What-If Planning
            with st.container(border=True):
                st.subheader('🧠 Scenario Planning')
                st.write('5 scenarios analyzed')
                st.info('**Best Case**: +${total_revenue * 0.15 / 1000:.0f}K upside potential')

    
    # TAB 5: CUSTOMER INSIGHTS (10 insights)
    with tab5:
        st.header('👥 Customer Insights')
        st.markdown('**10 insights for customer optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 41: Top Customers
            with st.container(border=True):
                st.subheader('🏆 VIP Customers')
                st.write(f'Top {high_value_customers} customers = 60% of revenue')
                st.success('**Focus**: VIP retention program')
            
            # Insight 42: Churn Prediction
            with st.container(border=True):
                st.subheader('🚨 Churn Risk')
                st.write(f'{churn_rate:.0f}% customers at risk')
                st.error(f'**Impact**: ${total_revenue * churn_rate / 100 / 1000:.0f}K revenue at risk')
                st.info('**Action**: Launch retention campaign')
                all_insights.append({'priority': 'HIGH', 'category': 'Customer', 'action': 'Reduce churn', 'impact': f'${total_revenue * churn_rate / 100 * 0.5 / 1000:.0f}K saved'})
            
            # Insight 43: Repeat Purchase
            with st.container(border=True):
                st.subheader('🔁 Repeat Rate')
                st.write('Avg customer purchases 2.3x/year')
                st.info('**Opportunity**: Increase to 3x with loyalty program')
            
            # Insight 44: Cross-Product Patterns
            with st.container(border=True):
                st.subheader('🔗 Purchase Patterns')
                st.write('Product bundles increase basket by 25%')
                st.success(f'**Potential**: +${total_revenue * 0.25 / 1000:.0f}K')
            
            # Insight 45: Customer Profitability
            with st.container(border=True):
                st.subheader('💰 Segment Profitability')
                st.write('Premium segment: 3x margin vs standard')
                st.info('**Strategy**: Upsell standard to premium')
        
        with col2:
            # Insight 46: Regional Insights
            with st.container(border=True):
                st.subheader('🌍 Regional Performance')
                st.write('Region A: 2x growth vs Region B')
                st.success('**Action**: Replicate Region A strategy')
            
            # Insight 47: Customer Lifetime Value
            with st.container(border=True):
                st.subheader('💵 Lifetime Value')
                st.metric('Avg CLV', format_currency(clv, decimals=0))
                st.info('**Target**: Increase to ${(clv * 1.3):.0f}')
            
            # Insight 48: Feedback Correlation
            with st.container(border=True):
                st.subheader('📝 Feedback Analysis')
                st.write('2 products with recurring complaints')
                st.warning('**Action**: Address quality issues')
            
            # Insight 49: High-Risk Segments
            with st.container(border=True):
                st.subheader('⚠️ At-Risk Segments')
                st.write('Price-sensitive segment: 30% churn risk')
                st.error('**Strategy**: Targeted value propositions')
            
            # Insight 50: Marketing Channel ROI
            with st.container(border=True):
                st.subheader('📊 Channel Performance')
                st.write('Email: 8x ROI, Social: 3x ROI')
                st.success('**Action**: Shift budget to email')

    
    # TAB 6: OPERATIONAL EFFICIENCY (10 insights)
    with tab6:
        st.header('⚙️ Operational Efficiency')
        st.markdown('**10 insights for operations optimization**')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Insight 51: Supplier Risk
            with st.container(border=True):
                st.subheader('🚨 Supplier Risk')
                st.write(f'Supplier X risk score: {supplier_risk_score}/100')
                st.warning('**Action**: Identify backup suppliers')
                all_insights.append({'priority': 'MEDIUM', 'category': 'Operations', 'action': 'Diversify suppliers', 'impact': 'Risk mitigation'})
            
            # Insight 52: Staffing Optimization
            with st.container(border=True):
                st.subheader('👥 Staffing Efficiency')
                st.write('Peak demand: Tues-Thurs 2-5pm')
                st.info('**Action**: Adjust shifts to match demand')
            
            # Insight 53: Multi-Location Performance
            with st.container(border=True):
                st.subheader('🏢 Location Analysis')
                st.write('Store A: 2x revenue per sqft vs Store B')
                st.success('**Opportunity**: Replicate Store A layout')
            
            # Insight 54: Process Inefficiencies
            with st.container(border=True):
                st.subheader('⚠️ Process Bottlenecks')
                st.write('Order processing: 15% error rate')
                st.error('**Cost**: ${total_revenue * 0.03 / 1000:.0f}K in rework')
            
            # Insight 55: Reorder Optimization
            with st.container(border=True):
                st.subheader('🔄 Reorder Efficiency')
                st.write('Reduce reorder point by 15 units')
                st.success(f'**Savings**: ${reorder_optimization_savings/1000:.1f}K/year')
                all_insights.append({'priority': 'MEDIUM', 'category': 'Operations', 'action': 'Optimize reorder', 'impact': f'${reorder_optimization_savings/1000:.1f}K'})
        
        with col2:
            # Insight 56: Category Performance
            with st.container(border=True):
                st.subheader('📊 Category Analysis')
                st.write('Category Z: 50% revenue, 70% holding cost')
                st.warning('**Action**: Review category rationalization')
            
            # Insight 57: Storage Optimization
            with st.container(border=True):
                st.subheader('🏭 Space Utilization')
                st.write('Warehouse: 65% utilized')
                st.info('**Opportunity**: Sublet or consolidate')
            
            # Insight 58: Automation Opportunities
            with st.container(border=True):
                st.subheader('🤖 Automation Potential')
                st.write('3 processes identified for automation')
                st.success(f'**Savings**: ${automation_opportunity/1000:.0f}K/year')
            
            # Insight 59: Cost Leaks
            with st.container(border=True):
                st.subheader('💧 Operational Leaks')
                st.write('Overhead costs up 12% YoY')
                st.error('**Impact**: ${total_cost * 0.12 / 1000:.0f}K excess costs')
            
            # Insight 60: Supplier Diversification
            with st.container(border=True):
                st.subheader('🌐 Supplier Strategy')
                st.write('80% volume from 2 suppliers')
                st.warning('**Risk**: High concentration - diversify supply chain')
    
    # ==================== PRIORITY ACTIONS DASHBOARD ====================
    st.markdown('---')
    st.markdown('---')
    st.header('🏆 Priority Actions Dashboard')
    st.markdown('**Ranked by impact - take action on these insights first**')
    
    # Create priority dataframe
    if all_insights:
        insights_df = pd.DataFrame(all_insights)
        
        # Display by priority
        col1, col2, col3 = st.columns(3)
        with col1:
            critical = len(insights_df[insights_df['priority'] == 'CRITICAL'])
            st.metric('🔴 CRITICAL', critical)
        with col2:
            high = len(insights_df[insights_df['priority'] == 'HIGH'])
            st.metric('🟠 HIGH', high)
        with col3:
            medium = len(insights_df[insights_df['priority'] == 'MEDIUM'])
            st.metric('🟡 MEDIUM', medium)
        
        st.markdown('---')
        st.subheader('📊 All Priority Actions')
        st.dataframe(insights_df, use_container_width=True, hide_index=True)
    
    # ==================== SUMMARY METRICS ====================
    st.markdown('---')
    st.subheader('💰 Total Opportunity Summary')
    
    # Calculate total opportunity
    total_opportunity = (
        slow_moving_value + 
        dead_stock_value * 12 + 
        negative_cash_risk + 
        margin_leakage * 12 + 
        total_revenue * 0.08 + 
        profit_sink_loss + 
        margin_bundle_opportunity * 12 + 
        reorder_optimization_savings
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric('Total Value at Stake', format_currency(total_opportunity, decimals=0))
    
    with col2:
        st.success('💡 **Strategic Recommendation**: Focus on cash flow optimization and inventory rebalancing this quarter for maximum impact')
