import streamlit as st

def render_ai_recommendations_page():
    """
    AI Recommendations page with styled note-based interface.
    Shows actionable insights organized by category.
    """
    st.title("🎯 AI-Powered Recommendations")
    st.caption("Get intelligent, data-driven recommendations tailored to your business.")
    st.markdown("---")
    
    # Recommendation data organized by category
    recommendations = {
        "Growth": [
            {"title": "Market Expansion", "icon": "📍", "description": "Identify and expand into new geographic markets with high growth potential based on your current performance data."},
            {"title": "Revenue Optimization", "icon": "💰", "description": "Increase MRR by analyzing pricing strategies, upsell opportunities, and customer segmentation patterns."},
            {"title": "Customer Acquisition", "icon": "👥", "description": "Scale acquisition through channel optimization, referral programs, and partnerships targeting high-LTV segments."},
        ],
        "Retention": [
            {"title": "Churn Prevention", "icon": "🛡️", "description": "Implement early warning systems to identify at-risk customers and proactive retention campaigns."},
            {"title": "Engagement Programs", "icon": "🔗", "description": "Build personalized onboarding, feature adoption, and regular engagement touchpoints to increase NPS."},
            {"title": "Loyalty Incentives", "icon": "⭐", "description": "Create tiered loyalty programs and exclusive benefits for high-value customers to maximize lifetime value."},
        ],
        "Efficiency": [
            {"title": "Cost Reduction", "icon": "💸", "description": "Identify inefficiencies in operations, renegotiate vendor contracts, and optimize resource allocation."},
            {"title": "Process Automation", "icon": "⚙️", "description": "Automate repetitive tasks, streamline workflows, and reduce manual touchpoints to improve throughput."},
            {"title": "Resource Optimization", "icon": "📊", "description": "Right-size teams, eliminate bottlenecks, and reallocate resources to high-impact functions."},
        ],
        "Innovation": [
            {"title": "New Products", "icon": "🚀", "description": "Launch complementary products or services based on customer feedback, market gaps, and competitive analysis."},
            {"title": "Technology Investments", "icon": "🔧", "description": "Invest in tools and infrastructure that enable scalability, improve security, and enhance user experience."},
            {"title": "Strategic Partnerships", "icon": "🤝", "description": "Build partnerships with complementary companies to expand reach, share resources, and create network effects."},
        ]
    }
    
    # Tabs for categories
    tab1, tab2, tab3, tab4 = st.tabs(["Growth", "Retention", "Efficiency", "Innovation"])
    
    tabs = [tab1, tab2, tab3, tab4]
    categories = list(recommendations.keys())
    
    for tab, category in zip(tabs, categories):
        with tab:
            st.subheader(f"{category} Recommendations")
            st.markdown("")
            
            # Display recommendations as styled note cards
            for i, rec in enumerate(recommendations[category]):
                # Create columns for better layout
                col1, col2 = st.columns([0.15, 0.85])
                
                with col1:
                    st.markdown(f"<div style='font-size: 32px; text-align: center;'>{rec['icon']}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(
                        f"""
                        <div style='background-color: #1e3a8a; padding: 16px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 12px;'>
                            <h4 style='margin: 0 0 8px 0; color: #ffffff;'>{rec['title']}</h4>
                            <p style='margin: 0; color: #e0e7ff; font-size: 14px;'>{rec['description']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            st.markdown("")
    
    st.markdown("---")
    
    # Footer note
    st.markdown("""
    💡 **How to use these recommendations:**
    - Review recommendations relevant to your current business priorities
    - Use the What-If Scenario Planner to model the impact of implementing these changes
    - Track progress on implemented recommendations in your analytics dashboard
    """)
