"""AI Recommendations - Data-driven insights with action tracking."""
import streamlit as st
import pandas as pd
from recommendations_engine import generate_data_driven_recommendations
from utils import calculate_business_health_score, calculate_key_metrics


def _init_action_tracking():
    if 'implemented_actions' not in st.session_state:
        st.session_state.implemented_actions = {}
    if 'action_impact_notes' not in st.session_state:
        st.session_state.action_impact_notes = {}


def render_recommendations_page(data=None, kpis=None, format_currency=None, format_percentage=None, format_multiplier=None):
    """Render the AI Recommendations page with data-driven insights."""
    if data is None:
        data = st.session_state.get('current_data') or st.session_state.get('uploaded_data')
    if data is None or (hasattr(data, 'empty') and data.empty):
        st.warning("Load data from Dashboard or Data Sources to get personalized recommendations.")
        return
    
    _init_action_tracking()
    industry = st.session_state.get('industry', 'ecommerce')
    
    st.markdown("""<div style='margin-bottom:30px'><h1 style='font-size:36px;font-weight:700;margin-bottom:5px'>AI Recommendations</h1><p style='color:#9CA3AF;font-size:16px;margin:0'>Personalized insights from your business data</p></div>""", unsafe_allow_html=True)
    
    # Data source badge
    data_source = "Live Data" if st.session_state.get('connected_sources') else "Demo Data"
    badge_color = "#10B981" if data_source == "Live Data" else "#6B7280"
    st.markdown(f"""<div style='background:{badge_color};color:white;border-radius:8px;padding:8px 16px;font-size:14px;margin-bottom:24px;display:inline-block;'><b>📊 {data_source}</b> | Based on your last 90 days</div>""", unsafe_allow_html=True)
    
    # Generate data-driven recommendations
    recs = generate_data_driven_recommendations(data, industry)
    
    category_tabs = {
        'revenue': '🚀 Revenue',
        'retention': '💚 Retention',
        'efficiency': '⚡ Efficiency',
        'innovation': '🎯 Innovation'
    }
    
    # Group by category for tabs
    categories_seen = []
    for r in recs:
        cat = category_tabs.get(r['category'], '📋 Other')
        if cat not in categories_seen:
            categories_seen.append(cat)
    tabs = st.tabs(categories_seen) if categories_seen else [st.container()]
    
    for rec in recs:
        cat_label = category_tabs.get(rec['category'], '📋 Other')
        tab_idx = categories_seen.index(cat_label) if cat_label in categories_seen else 0
        with tabs[tab_idx]:
                rec_key = f"rec_{rec['title'][:20].replace(' ', '_')}"
                with st.container(border=True):
                    col_l, col_r = st.columns([3, 1])
                    with col_l:
                        st.markdown(f"### {rec['title']}")
                        st.markdown(f"**Expected Impact:** {rec['impact']}")
                        st.markdown(f"*{rec['why']}*")
                        st.markdown("**Action Steps:**")
                        for i, step in enumerate(rec['steps'], 1):
                            st.markdown(f"{i}. {step}")
                        st.caption(f"Cost/Benefit: {rec['cost_benefit']}")
                    with col_r:
                        st.metric("Confidence", f"{rec['confidence']}%", rec['impact'][:20] + "..." if len(rec['impact']) > 20 else rec['impact'])
                        
                        # Action tracking
                        if st.button("✓ Mark as Implemented", key=f"impl_{rec_key}"):
                            st.session_state.implemented_actions[rec_key] = True
                            st.rerun()
                        
                        if st.session_state.implemented_actions.get(rec_key):
                            st.success("✅ Implemented")
    
    st.markdown("---")
    
    # Action tracking summary
    implemented_count = sum(1 for v in st.session_state.implemented_actions.values() if v)
    if implemented_count > 0:
        st.subheader("📋 Your Progress")
        st.success(f"You've implemented **{implemented_count}** recommendation(s) this quarter. Keep it up!")
    
    # Total impact summary
    st.subheader("💰 Potential Impact Summary")
    impact_df = pd.DataFrame([
        {'Category': r['category'].title(), 'Recommendation': r['title'][:40], 'Impact': r['impact'], 'Confidence': f"{r['confidence']}%"}
        for r in recs
    ])
    st.dataframe(impact_df, use_container_width=True, hide_index=True)
    
    st.markdown("""
    ### 🎯 Recommended Execution
    **Priority order:** Start with Efficiency (quick wins) → Revenue (scale) → Retention (compound) → Innovation (long-term).  
    Track your progress by marking recommendations as implemented.
    """)
