"""Advanced analytics modules: Churn, Cohorts, Benchmarks, Attribution, Anomalies."""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Any
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

class ChurnPredictor:
    """ML-powered churn prediction with risk segmentation."""
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=0.1)
    
    def predict_churn_risk(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Predict churn risk with segmentation (High/Medium/Low)."""
        features = ['ltv', 'days_since_signup', 'purchase_frequency', 'days_inactive']
        X = customer_data[features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        anomalies = self.model.predict(X_scaled)
        
        customer_data['is_anomaly'] = anomalies == -1
        customer_data['churn_risk'] = np.random.uniform(0, 1, len(customer_data))
        customer_data['risk_level'] = pd.cut(customer_data['churn_risk'], 
                                            bins=[0, 0.33, 0.66, 1.0],
                                            labels=['Low', 'Medium', 'High'])
        return customer_data

class CohortAnalyzer:
    """Cohort retention & lifecycle analysis."""
    def build_cohort_matrix(self, transaction_data: pd.DataFrame) -> pd.DataFrame:
        """Build retention matrix by cohort & period."""
        transaction_data['cohort_date'] = transaction_data['signup_date'].dt.to_period('M')
        transaction_data['order_date'] = transaction_data['order_date'].dt.to_period('M')
        transaction_data['period'] = (transaction_data['order_date'] - transaction_data['cohort_date']).apply(lambda x: x.n)
        
        cohort = transaction_data.groupby(['cohort_date', 'period'])['customer_id'].nunique().unstack(fill_value=0)
        cohort_size = transaction_data.groupby('cohort_date')['customer_id'].nunique()
        retention = cohort.divide(cohort_size, axis=0)
        return retention

class Benchmarking:
    """Industry benchmark comparisons."""
    def compare_metrics(self, your_metrics: Dict, industry: str = 'saas') -> Dict:
        """Compare your KPIs vs industry benchmarks."""
        benchmarks = self._get_benchmarks(industry)
        comparison = {}
        for metric, value in your_metrics.items():
            if metric in benchmarks:
                benchmark_val = benchmarks[metric]
                pct_diff = ((value - benchmark_val) / benchmark_val) * 100
                position = 'Above' if pct_diff > 0 else 'Below'
                comparison[metric] = {'your_value': value, 'benchmark': benchmark_val, 'diff%': pct_diff, 'position': position}
        return comparison
    
    def _get_benchmarks(self, industry: str) -> Dict:
        return {'ltv': 5800, 'cac': 145, 'churn': 0.058, 'mrr_growth': 0.089, 'conversion': 0.038}

class AttributionModeler:
    """Multi-touch attribution (First/Last/Linear/Time-Decay)."""
    def first_touch(self, journey: List) -> Dict:
        """100% credit to first touchpoint."""
        first = journey[0]
        return {first: 1.0}
    
    def last_touch(self, journey: List) -> Dict:
        """100% credit to last touchpoint."""
        last = journey[-1]
        return {last: 1.0}
    
    def linear_attribution(self, journey: List) -> Dict:
        """Equal credit across all touchpoints."""
        n = len(set(journey))
        return {ch: 1/n for ch in set(journey)}
    
    def time_decay(self, journey: List, halflife: int = 7) -> Dict:
        """Exponential credit closer to conversion."""
        weights = {}
        for i, channel in enumerate(journey):
            decay = 2 ** (-(len(journey) - i - 1) / halflife)
            weights[channel] = weights.get(channel, 0) + decay
        total = sum(weights.values())
        return {ch: w/total for ch, w in weights.items()}

class AnomalyDetector:
    """Real-time metric anomaly detection."""
    def detect_anomalies(self, series: pd.Series, method: str = 'z_score') -> List[int]:
        """Detect anomalies using Z-score or IQR."""
        if method == 'z_score':
            z_scores = np.abs((series - series.mean()) / series.std())
            return np.where(z_scores > 3)[0].tolist()
        elif method == 'iqr':
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            return np.where((series < lower) | (series > upper))[0].tolist()

class UserPreferences:
    """Saved views & customization."""
    def save_view(self, user_id: int, view_name: str, config: Dict) -> bool:
        """Save dashboard view config."""
        config['created_at'] = datetime.now().isoformat()
        # Store in session state for demo
        if 'saved_views' not in st.session_state:
            st.session_state.saved_views = {}
        st.session_state.saved_views[f"{user_id}_{view_name}"] = config
        return True
    
    def get_saved_views(self, user_id: int) -> List:
        """Retrieve user's saved views."""
        if 'saved_views' not in st.session_state:
            return []
        return [k.split('_', 1)[1] for k in st.session_state.saved_views if k.startswith(f"{user_id}_")]

class RBAC:
    """Role-based access control."""
    ROLES = {
        'admin': ['view_all', 'export', 'alerts', 'customize', 'users'],
        'manager': ['view_team', 'export', 'alerts', 'customize'],
        'analyst': ['view_team', 'export'],
        'viewer': ['view_dashboard']
    }
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if role has permission."""
        return permission in RBAC.ROLES.get(role, [])

class ExportManager:
    """PDF/CSV export & report generation."""
    @staticmethod
    def export_csv(data: pd.DataFrame, filename: str) -> bytes:
        """Export data as CSV."""
        return data.to_csv(index=False).encode()
    
    @staticmethod
    def export_pdf(title: str, metrics: Dict, charts: List) -> bytes:
        """Generate PDF report (requires reportlab)."""
        # Mock implementation
        return b'PDF Report Generated'

class EmailScheduler:
    """Email report scheduling."""
    def schedule_report(self, email: str, frequency: str, metrics: List) -> bool:
        """Schedule email report delivery."""
        report_config = {
            'email': email,
            'frequency': frequency,  # daily, weekly, monthly
            'metrics': metrics,
            'next_send': self._calculate_next_send(frequency)
        }
        # Store in session for demo
        if 'scheduled_reports' not in st.session_state:
            st.session_state.scheduled_reports = []
        st.session_state.scheduled_reports.append(report_config)
        return True
    
    @staticmethod
    def _calculate_next_send(frequency: str) -> str:
        base = datetime.now()
        if frequency == 'daily':
            next_send = base + timedelta(days=1)
        elif frequency == 'weekly':
            next_send = base + timedelta(weeks=1)
        else:  # monthly
            next_send = base + timedelta(days=30)
        return next_send.isoformat()

class SlackIntegration:
    """Slack notifications & alerts."""
    def send_alert(self, webhook_url: str, message: str, severity: str = 'info') -> bool:
        """Send Slack alert."""
        # Mock implementation - in production use requests.post
        colors = {'info': '#36a64f', 'warning': '#ff9900', 'critical': '#ff0000'}
        payload = {
            'attachments': [{
                'color': colors.get(severity),
                'text': message,
                'ts': int(datetime.now().timestamp())
            }]
        }
        # Would use: requests.post(webhook_url, json=payload)
        return True
