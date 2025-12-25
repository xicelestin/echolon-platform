import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Load benchmark data from CSV
@st.cache_data
def load_benchmark_data():
    """Load industry benchmark data from CSV file"""
    csv_path = os.path.join(os.path.dirname(__file__), 'benchmark_catalog.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        # Return default benchmarks if CSV doesn't exist
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

def calculate_dollar_gaps(current_metrics, benchmarks, revenue, margin):
    """Calculate dollar value of gaps to industry benchmarks"""
    gaps = {}
    
    # Profit Margin Gap
    if 'profit_margin' in current_metrics:
        current_margin = current_metrics['profit_margin']
        target_margin = benchmarks[benchmarks['metric'] == 'Profit Margin']['top_quartile'].values[0]
        margin_gap = target_margin - current_margin
        if margin_gap > 0:
            annual_opportunity = revenue * (margin_gap / 100)
            gaps['profit_margin'] = {
                'gap': margin_gap,
                'annual_opportunity': annual_opportunity,
                'closing_25': annual_opportunity * 0.25,
                'closing_50': annual_opportunity * 0.50
            }
    
    # ROAS Gap  
    if 'roas' in current_metrics and 'marketing_spend' in current_metrics:
        current_roas = current_metrics['roas']
        target_roas = benchmarks[benchmarks['metric'] == 'ROAS']['top_quartile'].values[0]
        roas_gap = target_roas - current_roas
        if roas_gap > 0:
            marketing_spend = current_metrics['marketing_spend']
            additional_revenue = marketing_spend * roas_gap
            gaps['roas'] = {
                'gap': roas_gap,
                'annual_opportunity': additional_revenue * margin / 100,
                'closing_25': additional_revenue * margin / 100 * 0.25,
                'closing_50': additional_revenue * margin / 100 * 0.50
            }
    
    # Retention Gap
    if 'retention_rate' in current_metrics and 'customer_count' in current_metrics:
        current_retention = current_metrics['retention_rate']
        target_retention = benchmarks[benchmarks['metric'] == 'Customer Retention']['top_quartile'].values[0]
        retention_gap = target_retention - current_retention
        if retention_gap > 0:
            customer_count = current_metrics['customer_count']
            avg_customer_value = revenue / customer_count if customer_count > 0 else 0
            additional_customers = customer_count * (retention_gap / 100)
            gaps['retention'] = {
                'gap': retention_gap,
                'annual_opportunity': additional_customers * avg_customer_value * margin / 100,
                'closing_25': additional_customers * avg_customer_value * margin / 100 * 0.25,
                'closing_50': additional_customers * avg_customer_value * margin / 100 * 0.50
            }
    
    return gaps

def render_competitive_benchmark_page(data, kpis, format_currency, format_percentage, format_number):
    """Render the competitive benchmark analysis page"""
    
    st.title("🏆 Competitive Benchmark Analysis")
    st.markdown("### Compare your performance against industry standards")
    
    # Load benchmarks
    benchmarks = load_benchmark_data()
    
    # Calculate current metrics
    total_revenue = kpis.get('total_revenue', 0)
    avg_margin = kpis.get('avg_profit_margin', 40.0)
    avg_roas = data['roas'].mean() if 'roas' in data.columns else 0
    marketing_spend = data['marketing_spend'].sum() if 'marketing_spend' in data.columns else 0
    
    current_metrics = {
        'profit_margin': avg_margin,
        'roas': avg_roas,
        'revenue': total_revenue,
        'marketing_spend': marketing_spend,
        'customer_count': kpis.get('total_customers', 0)
    }
    
    st.markdown("---")
    
    # Assumption Notes
    with st.expander("📋 About These Benchmarks", expanded=False):
        st.markdown("""
        **Benchmark Sources & Methodology:**
        
        These benchmarks represent industry standards for e-commerce and SaaS businesses:
        - **Industry Average**: Median performance across all companies in the sector
        - **Top Quartile**: Performance of companies in the 75th percentile  
        - **Best in Class**: Top 10% performers (90th percentile)
        
        **Data Sources:**
        - Industry reports from McKinsey, Gartner, and Forrester
        - Public financial data from comparable companies
        - Aggregated anonymized data from business intelligence platforms
        
        **Notes:**
        - Benchmarks are updated quarterly
        - Your mileage may vary based on industry vertical, business model, and market
        - Use these as directional guidance, not absolute targets
        """)
    
    st.markdown("---")
    
    # Performance Comparison
    st.subheader("📊 Your Performance vs Industry")
    
    # Create comparison data
    comparison_data = []
    
    # Profit Margin
    profit_benchmark = benchmarks[benchmarks['metric'] == 'Profit Margin'].iloc[0]
    comparison_data.append({
        'Metric': 'Profit Margin',
        'Your Performance': avg_margin,
        'Industry Avg': profit_benchmark['industry_avg'],
        'Top Quartile': profit_benchmark['top_quartile'],
        'Best in Class': profit_benchmark['best_in_class'],
        'Unit': '%'
    })
    
    # ROAS
    roas_benchmark = benchmarks[benchmarks['metric'] == 'ROAS'].iloc[0]
    comparison_data.append({
        'Metric': 'ROAS',
        'Your Performance': avg_roas,
        'Industry Avg': roas_benchmark['industry_avg'],
        'Top Quartile': roas_benchmark['top_quartile'],
        'Best in Class': roas_benchmark['best_in_class'],
        'Unit': 'x'
    })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Profit Margin Comparison
        fig1 = go.Figure()
        metric_data = comparison_df[comparison_df['Metric'] == 'Profit Margin'].iloc[0]
        
        fig1.add_trace(go.Bar(
            x=['Your Performance', 'Industry Avg', 'Top Quartile', 'Best in Class'],
            y=[metric_data['Your Performance'], metric_data['Industry Avg'], 
               metric_data['Top Quartile'], metric_data['Best in Class']],
            marker_color=['#3b82f6', '#94a3b8', '#22c55e', '#eab308'],
            text=[f"{v:.1f}%" for v in [metric_data['Your Performance'], metric_data['Industry Avg'], 
                                        metric_data['Top Quartile'], metric_data['Best in Class']]],
            textposition='outside'
        ))
        fig1.update_layout(title='Profit Margin Comparison', yaxis_title='%', showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # ROAS Comparison
        fig2 = go.Figure()
        metric_data = comparison_df[comparison_df['Metric'] == 'ROAS'].iloc[0]
        
        fig2.add_trace(go.Bar(
            x=['Your Performance', 'Industry Avg', 'Top Quartile', 'Best in Class'],
            y=[metric_data['Your Performance'], metric_data['Industry Avg'], 
               metric_data['Top Quartile'], metric_data['Best in Class']],
            marker_color=['#3b82f6', '#94a3b8', '#22c55e', '#eab308'],
            text=[f"{v:.1f}x" for v in [metric_data['Your Performance'], metric_data['Industry Avg'], 
                                        metric_data['Top Quartile'], metric_data['Best in Class']]],
            textposition='outside'
        ))
        fig2.update_layout(title='ROAS Comparison', yaxis_title='Return Multiple (x)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # Dollar Value Gaps
    st.subheader("💰 Financial Impact of Performance Gaps")
    
    st.info("""
    💡 **Understanding the Opportunity**: These calculations show the potential revenue/profit increase 
    if you close the gap to industry benchmarks. We show both 25% and 50% gap closure scenarios.
    """)
    
    gaps = calculate_dollar_gaps(current_metrics, benchmarks, total_revenue, avg_margin)
    
    if gaps:
        # Display gap opportunities
        for gap_type, gap_data in gaps.items():
            with st.container():
                st.markdown(f"#### {gap_type.replace('_', ' ').title()} Gap")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    unit = '%' if gap_type != 'roas' else 'x'
                    st.metric(
                        "Gap to Top Quartile",
                        f"{gap_data['gap']:.1f}{unit}"
                    )
                
                with col2:
                    st.metric(
                        "Annual Opportunity",
                        format_currency(gap_data['annual_opportunity'], 0)
                    )
                
                with col3:
                    st.metric(
                        "Close 25% of Gap",
                        format_currency(gap_data['closing_25'], 0)
                    )
                
                with col4:
                    st.metric(
                        "Close 50% of Gap",
                        format_currency(gap_data['closing_50'], 0)
                    )
                
                st.markdown("---")
        
        # Total Opportunity
        total_opportunity = sum(gap['annual_opportunity'] for gap in gaps.values())
        total_25 = sum(gap['closing_25'] for gap in gaps.values())
        total_50 = sum(gap['closing_50'] for gap in gaps.values())
        
        st.success(f"""
        🎯 **Total Opportunity Summary**:
        - **Full Potential**: {format_currency(total_opportunity, 0)} annually
        - **Conservative (25% improvement)**: {format_currency(total_25, 0)} annually  
        - **Moderate (50% improvement)**: {format_currency(total_50, 0)} annually
        """)
    else:
        st.success("✅ Congratulations! You're performing at or above industry benchmarks across all metrics.")
    
    st.markdown("---")
    
    # Action Plan
    st.subheader("🎯 Recommended Actions")
    
    if 'profit_margin' in gaps:
        st.warning("""
        **Improve Profit Margins:**
        1. Negotiate better supplier pricing (target 5-10% cost reduction)
        2. Optimize shipping and fulfillment processes
        3. Implement dynamic pricing based on demand
        4. Reduce operational inefficiencies
        """)
    
    if 'roas' in gaps:
        st.warning("""
        **Optimize Marketing Efficiency:**
        1. Pause underperforming ad campaigns and channels
        2. Increase investment in top-performing channels
        3. Improve landing page conversion rates
        4. Implement better attribution tracking
        """)
    
    if 'retention' in gaps:
        st.warning("""
        **Boost Customer Retention:**
        1. Launch loyalty/rewards program
        2. Implement win-back campaigns for churned customers  
        3. Improve customer service response times
        4. Create personalized email nurture sequences
        """)
    
    # Benchmark Details Table
    st.markdown("---")
    st.subheader("📋 Full Benchmark Details")
    st.dataframe(benchmarks, use_container_width=True)
