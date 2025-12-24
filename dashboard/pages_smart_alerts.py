import streamlit as st
import pandas as pd

def render_smart_alerts_page(data, kpis, format_currency, format_percentage, format_number):
    st.title('🔔 AI-Powered Smart Alerts')
    st.markdown('**Identify and fix business problems with AI**')
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '📦 Inventory', '💰 Financial', '📈 Demand', '💼 Profit', '⚙️ Operations'
    ])
    
    with tab1:
        st.header('Inventory Problems')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader('🚨 Overstocked SKUs')
                st.write('$12K slow inventory')
                st.success('Free up $12K working capital')
        with col2:
            with st.container(border=True):
                st.subheader('⚠️ Dead Stock')
                st.write('SKU unsold 180 days')
                st.warning('Save $900/month')
    
    with tab2:
        st.header('Financial Risks')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader('💳 Cash Conversion')
                st.write('45 days to cash, 30 payables')
                st.error('Risk: $500K negative cash')
        with col2:
            with st.container(border=True):
                st.subheader('📉 Margin Leakage')
                st.write('Costs up 15%')
                st.warning('Recover $150K/month')
    
    with tab3:
        st.header('Demand Issues')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader('📈 Demand Spike')
                st.write('Product Z demand +60%')
                st.success('Capture $200K revenue')
        with col2:
            with st.container(border=True):
                st.subheader('🎯 Forecast Error')
                st.write('3 SKUs over, 2 under')
                st.info('25% accuracy boost')
    
    with tab4:
        st.header('Profitability')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader('📉 Profit Sinks')
                st.write('Products C&D negative')
                st.error('Stop $30K loss')
        with col2:
            with st.container(border=True):
                st.subheader('⭐ High-Margin Bundle')
                st.write('E+F bundle strategy')
                st.success('+15% transaction value')
    
    with tab5:
        st.header('Operations')
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader('⚡ Supplier Risk')
                st.write('Lead time 5→12 days')
                st.warning('Need backup suppliers')
        with col2:
            with st.container(border=True):
                st.subheader('📊 Reorder Opt')
                st.write('Product Y 120→85 units')
                st.success('Save $2.4K/year')
    
    st.markdown('---')
    st.subheader('🚀 Priority Actions')
    df = pd.DataFrame({
        'Priority': ['🔴 CRITICAL', '🔴 CRITICAL', '🟠 HIGH', '🟠 HIGH', '🟡 MED'],
        'Action': ['Reorder 500 units', 'Extend payment terms', 'Liquidate slow stock', 'Update ML forecast', 'Reorder optimization'],
        'Impact': ['$200K sales', '$500K cash', '$12K freed', '25% accuracy', '$2.4K saved']
    })
    st.dataframe(df, use_container_width=True)
    
    st.metric('Total Opportunity', '$800K')
    st.info('Focus on cash flow + inventory rebalancing this quarter')
