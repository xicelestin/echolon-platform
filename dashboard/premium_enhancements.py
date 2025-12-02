"""Premium Enhancements for Echolon AI Dashboard
Anomalies, Alerts, Smart Cards, Export, Benchmarks, Cohorts, Churn
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# ANOMALY DETECTION
def detect_anomalies(series, threshold=2.5):
    if len(series) < 2:
        return {'count': 0, 'severity': 'normal'}
    z_scores = np.abs(stats.zscore(series.dropna()))
    anomalies = np.where(z_scores > threshold)[0]
    return {'count': len(anomalies), 'severity': 'critical' if len(anomalies) > 3 else 'warning' if len(anomalies) > 0 else 'normal'}

def render_alert(type_alert, title, msg, icon='i'):
    colors = {'critical': '#ef4444', 'warning': '#f97316', 'success': '#22c55e', 'info': '#38bdf8'}
    c = colors.get(type_alert, colors['info'])
    html = f'<div style="background:{c}22;border-left:4px solid {c};border-radius:8px;padding:16px;margin-bottom:16px"><div style="display:flex;gap:12px"><span>{icon}</span><div><h4 style="margin:0;color:{c}">{title}</h4><p style="margin:0;color:{c};font-size:14px">{msg}</p></div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

# SMART COLORED CARDS
def render_smart_card(title, value, delta=None, status='neutral', icon='chart', helper=None):
    colors = {'good': '#22c55e', 'warning': '#f97316', 'critical': '#ef4444', 'neutral': '#64748b'}
    c = colors.get(status, colors['neutral'])
    delta_html = f'<p style="color:{c}"><b>{delta}</b></p>' if delta else ''
    helper_html = f'<p style="color:#94a3b8;font-size:12px">💡{helper}</p>' if helper else ''
    html = f'<div style="background:linear-gradient(#1e293b,#0f172a);border:2px solid {c};border-radius:12px;padding:20px;margin-bottom:12px"><h4 style="color:#94a3b8;margin:0">{title}</h4><h2 style="color:{c};margin:4px 0">{value}</h2>{delta_html}{helper_html}</div>'
    st.markdown(html, unsafe_allow_html=True)

# EXPORT
def render_exports(df, name):
    c1, c2 = st.columns(2)
    with c1:
        csv = df.to_csv(index=False).encode()
        st.download_button('CSV', csv, f'{name}.csv', 'text/csv')
    with c2:
        j = df.to_json(orient='records').encode()
        st.download_button('JSON', j, f'{name}.json', 'application/json')

# CHURN PREDICTION
def predict_churn():
    return pd.DataFrame({
        'Customer': ['Acme', 'Beta', 'Gamma', 'Delta'],
        'LTV': [25000, 18000, 32000, 15000],
        'Risk': [0.82, 0.78, 0.15, 0.88],
        'Reason': ['Tickets', 'Payment', 'Healthy', 'Tickets']
    })

# COHORT TABLE
def cohort_table():
    return pd.DataFrame({
        'Cohort': ['Jan', 'Feb', 'Mar', 'Apr'],
        'M0': [100, 100, 100, 100],
        'M1': [85, 88, 90, 92],
        'M2': [72, 76, 79, 83],
        'M3': [61, 65, 69, 74],
    })

# BENCHMARKING
def benchmark_chart(your, industry, title):
    fig = go.Figure(data=[
        go.Bar(name='You', x=list(your.keys()), y=list(your.values()), marker_color='#38bdf8'),
        go.Bar(name='Industry', x=list(industry.keys()), y=list(industry.values()), marker_color='#94a3b8')
    ])
    fig.update_layout(title=title, template='plotly_dark', plot_bgcolor='#0f172a', paper_bgcolor='#0f172a')
    return fig

# AI INSIGHTS  
def ai_insights(m):
    return f"""🎯 Revenue +{m.get('rev', 0):.1f}% | CAC -{m.get('cac', 0):.1f}% | Churn {m.get('churn', 0):.1f}% | {m.get('customers', 0):.0f} upsell ready"""
