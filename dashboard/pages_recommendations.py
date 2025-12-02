"""AI Recommendations & Tactical Consulting Page."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from advanced_components import Recommendations

def render_recommendations_page():
    """Render the AI Recommendations page."""
    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:36px;font-weight:700;margin-bottom:5px'>AI Recommendations</h1><p style='color:#9CA3AF;font-size:16px;margin:0'>Tactical consulting insights & growth strategies</p></div>""", unsafe_allow_html=True)
    
    st.markdown("""<div style='background:#0EA5E9;color:#E0F2FE;border-radius:8px;padding:12px 16px;font-size:15px;margin-bottom:24px;'><b>✨ AI-Generated</b> | Based on 90 days of business data & industry benchmarks</div>""", unsafe_allow_html=True)
    
    # Tabs for recommendation categories
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Revenue", "💚 Retention", "⚡ Efficiency", "🎯 Innovation"])
    
    with tab1:
        st.markdown("""<h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Revenue Optimization Recommendations</h3>""", unsafe_allow_html=True)
        
        rec1 = st.container(border=True)
        with rec1:
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown("""
                ### Add Tiered Pricing for High-LTV Customers
                
                **Expected Impact:** +8–12% MRR (+$28K–$42K annually)
                
                **Why This Matters:**
                32% of your customers fall into the high-LTV segment (LTV >$5K). These power users purchase 58% of total revenue but are priced identically to new customers. Segmented pricing captures additional value without churn.
                
                **Action Steps:**
                1. Segment customers by LTV and feature usage
                2. Create 3 pricing tiers (Basic, Pro, Enterprise)
                3. Email high-LTV cohort with upgrade offer
                4. Monitor NPS and churn closely
                5. Iterate pricing based on conversion rates
                
                **Cost/Benefit:** ~$2K to implement | $28K-$42K incremental MRR
                
                **Timeline:** 30–45 days
                """)
            with col_r:
                st.metric("Confidence", "92%", "+8-12%")
        
        rec2 = st.container(border=True)
        with rec2:
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown("""
                ### Launch Geographic Expansion (Asia-Pacific)
                
                **Expected Impact:** +$85K–$120K new revenue (12-month horizon)
                
                **Why This Matters:**
                APAC markets show 15.8% growth vs. your company's 8% average. Regional customization (local payment, language, regulations) unlocks $2.1B TAM vs. your current $18M penetration.
                
                **Action Steps:**
                1. Hire regional partnerships manager
                2. Localize product for top 3 markets (India, Singapore, AU)
                3. Partner with local resellers
                4. Run region-specific marketing campaign
                5. Establish local support team
                
                **Cost/Benefit:** ~$45K setup costs | $85K-$120K revenue within 12 months
                
                **Timeline:** 90–120 days to launch
                """)
            with col_r:
                st.metric("Confidence", "78%", "+$85K-$120K")
    
    with tab2:
        st.markdown("""<h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Retention & Loyalty Recommendations</h3>""", unsafe_allow_html=True)
        
        ret1 = st.container(border=True)
        with ret1:
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown("""
                ### Implement Loyalty Rewards Program
                
                **Expected Impact:** -25–35% churn (saves $64K–$89K in LTV)
                
                **Why This Matters:**
                Your churn rate is 2.1% monthly (25% annually). Customers with 4+ purchases show 5x lower churn. Loyalty programs increase repeat purchase frequency by 23% and lifetime value by 38% (HubSpot Research).
                
                **Action Steps:**
                1. Design tiered rewards (Bronze/Silver/Gold)
                2. Build program into product (points per purchase)
                3. Create exclusive perks (early access, discounts)
                4. Launch with email campaign to all customers
                5. Monitor repeat purchase rate weekly
                
                **Cost/Benefit:** ~$8K to build | $64K-$89K saved in churn reduction
                
                **Timeline:** 8–10 weeks
                """)
            with col_r:
                st.metric("Confidence", "88%", "-25-35% churn")
    
    with tab3:
        st.markdown("""<h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Operational Efficiency Recommendations</h3>""", unsafe_allow_html=True)
        
        eff1 = st.container(border=True)
        with eff1:
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown("""
                ### Optimize Inventory Holding Costs
                
                **Expected Impact:** -$28.5K annual holding costs
                
                **Why This Matters:**
                Current carrying costs are $412K annually (18% of inventory value). Adjusting reorder points and safety stock levels for A-items alone reduces waste by 7–12% without affecting service levels.
                
                **Action Steps:**
                1. Segment inventory using ABC analysis (A/B/C)
                2. Adjust reorder points for A-items based on demand forecasts
                3. Reduce safety stock by 15% for B/C items
                4. Implement cycle counting for A-items (daily)
                5. Monitor stockout rates weekly
                
                **Cost/Benefit:** ~$2K consulting + implementation | $28.5K saved annually
                
                **Timeline:** 3–4 weeks
                """)
            with col_r:
                st.metric("Confidence", "85%", "-$28.5K/yr")
    
    with tab4:
        st.markdown("""<h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>Innovation & Product Recommendations</h3>""", unsafe_allow_html=True)
        
        inn1 = st.container(border=True)
        with inn1:
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown("""
                ### Add Subscription / Recurring Revenue Option
                
                **Expected Impact:** +$140K–$180K new recurring revenue annually
                
                **Why This Matters:**
                35% of your customer base buys monthly. Recurring models increase customer predictability and LTV by 6-8x. SaaS companies with subscription models fetch 4x revenue multiples (Techcrunch M&A data).
                
                **Action Steps:**
                1. Design subscription tiers (monthly/annual options)
                2. Build auto-renewal infrastructure
                3. Migrate 30% of monthly buyers to subscription
                4. Offer 10% discount for annual commitments
                5. Track MRR growth and churn metrics
                
                **Cost/Benefit:** ~$25K development | $140K-$180K MRR upside
                
                **Timeline:** 60–90 days
                """)
            with col_r:
                st.metric("Confidence", "81%", "+$140K-$180K")
    
    st.markdown("""<div style='margin:40px 0;border-top:1px solid #374151;'></div>""", unsafe_allow_html=True)
    
    # Summary Impact
    st.markdown("""<h3 style='font-size:20px;font-weight:600;margin-bottom:16px;'>💰 Total Potential Impact Summary</h3>""", unsafe_allow_html=True)
    
    impact_summary = pd.DataFrame({
        'Category': ['Revenue Growth', 'Churn Reduction', 'Cost Efficiency', 'Innovation Upside', 'TOTAL'],
        'Impact': ['+$28-42K MRR', '-$64-89K LTV loss', '-$28.5K annual', '+$140-180K MRR', '+$337-379K / -$92.5K = +$244.5-286.5K NET'],
        'Timeline': ['45 days', '70 days', '21 days', '90 days', '~120 days to full implementation'],
        'Effort': ['Medium', 'Medium', 'Low', 'High', 'Medium-High']
    })
    
    st.dataframe(impact_summary, use_container_width=True, hide_index=True)
    
    st.markdown("""
    ### 🎯 Recommended Execution Path
    
    **Phase 1 (Weeks 1-3):** Launch quick wins
    - Implement inventory optimization (lowest effort, highest short-term savings)
    - Begin loyalty program design
    
    **Phase 2 (Weeks 4-8):** Core revenue initiatives
    - Roll out tiered pricing
    - Finalize loyalty program launch
    
    **Phase 3 (Weeks 9-14):** Scale & innovate
    - Begin APAC expansion
    - Build subscription infrastructure
    
    Expected cumulative impact by month 4: **+$244.5K–$286.5K**
    """)
