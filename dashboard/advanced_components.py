"""Advanced Streamlit Components for Business Intelligence Dashboard."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class PredictionMetrics:
    """Generate advanced forecasting with confidence intervals."""
    
    @staticmethod
    def generate_forecast_with_ci(
        historical_data: pd.Series,
        periods: int = 12,
        confidence_level: float = 0.95
    ) -> Dict:
        """Generate forecast with confidence intervals."""
        # Simulated forecast logic
        values = historical_data.values
        trend = (values[-1] - values[0]) / len(values)
        std_dev = np.std(values)
        
        forecast = []
        ci_upper = []
        ci_lower = []
        
        for i in range(periods):
            pred = values[-1] + (trend * (i + 1))
            forecast.append(pred)
            # 95% CI approximation
            margin = 1.96 * std_dev
            ci_upper.append(pred + margin)
            ci_lower.append(pred - margin)
        
        return {
            'forecast': forecast,
            'ci_upper': ci_upper,
            'ci_lower': ci_lower,
            'trend_direction': 'Strong upward' if trend > 0 else 'Downward'
        }
    
    @staticmethod
    def plot_forecast_with_ci(
        historical_data: pd.Series,
        forecast_data: Dict,
        title: str = "Forecast"
    ):
        """Plot forecast with confidence intervals."""
        dates_hist = pd.date_range(end=datetime.now(), periods=len(historical_data), freq='D')
        dates_future = pd.date_range(start=dates_hist[-1], periods=len(forecast_data['forecast']), freq='D')
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=dates_hist, y=historical_data.values,
            mode='lines', name='Historical',
            line=dict(color='#3B82F6', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=dates_future, y=forecast_data['forecast'],
            mode='lines', name='Forecast',
            line=dict(color='#F59E0B', width=2)
        ))
        
        # 95% CI
        fig.add_trace(go.Scatter(
            x=dates_future, y=forecast_data['ci_upper'],
            fill=None, mode='lines', name='95% CI Upper',
            line=dict(width=0), showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=dates_future, y=forecast_data['ci_lower'],
            fill='tonexty', mode='lines', name='95% Confidence Interval',
            line=dict(width=0), fillcolor='rgba(245, 158, 11, 0.2)'
        ))
        
        fig.update_layout(
            title=title,
            hovermode='x unified',
            height=400,
            template='plotly_dark'
        )
        
        return fig


class SalesInsights:
    """Generate business-grade sales analytics."""
    
    @staticmethod
    def calculate_kpis(data: pd.DataFrame) -> Dict:
        """Calculate key performance indicators."""
        total_revenue = data['revenue'].sum()
        total_customers = data['customer_id'].nunique()
        avg_order_value = data['amount'].mean()
        
        # Calculate LTV (simplified)
        ltv = (total_revenue / total_customers) if total_customers > 0 else 0
        
        # Calculate MRR growth
        mrr_growth = 0.08  # Mock data
        cac = 45  # Customer Acquisition Cost
        churn_rate = 0.05
        
        return {
            'revenue': total_revenue,
            'customers': total_customers,
            'aov': avg_order_value,
            'ltv': ltv,
            'mrr_growth': mrr_growth,
            'cac': cac,
            'churn': churn_rate,
            'ltv_cac_ratio': ltv / cac if cac > 0 else 0
        }
    
    @staticmethod
    def plot_sales_breakdown(data: pd.DataFrame, dimension: str = 'product'):
        """Plot sales distribution by dimension."""
        breakdown = data.groupby(dimension)['amount'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=breakdown.values, y=breakdown.index,
            orientation='h',
            title=f'Sales Distribution by {dimension.title()}',
            labels={'x': 'Revenue ($)', 'y': dimension.title()},
            color=breakdown.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(height=400, template='plotly_dark')
        return fig


class InventoryOptimization:
    """Generate inventory operations intelligence."""
    
    @staticmethod
    def calculate_stockout_probability(
        current_stock: int,
        daily_demand: float,
        lead_time_days: int
    ) -> float:
        """Calculate probability of stockout."""
        expected_usage = daily_demand * lead_time_days
        if current_stock < expected_usage:
            return min((expected_usage - current_stock) / expected_usage, 1.0)
        return 0.0
    
    @staticmethod
    def calculate_optimal_reorder_point(
        daily_demand: float,
        lead_time_days: int,
        service_level: float = 0.95
    ) -> int:
        """Calculate optimal reorder point."""
        z_score = 1.645 if service_level == 0.95 else 2.33
        std_dev = daily_demand * 0.2  # Assume 20% variability
        reorder_point = (daily_demand * lead_time_days) + (z_score * std_dev * (lead_time_days ** 0.5))
        return int(reorder_point)
    
    @staticmethod
    def calculate_safety_stock(
        daily_demand: float,
        lead_time_days: int,
        service_level: float = 0.95
    ) -> int:
        """Calculate optimal safety stock."""
        z_score = 1.645 if service_level == 0.95 else 2.33
        std_dev = daily_demand * 0.2
        safety_stock = z_score * std_dev * (lead_time_days ** 0.5)
        return int(safety_stock)
    
    @staticmethod
    def abc_classification(items: List[Dict]) -> Dict:
        """Classify inventory using ABC analysis."""
        sorted_items = sorted(items, key=lambda x: x['annual_value'], reverse=True)
        total_value = sum(item['annual_value'] for item in sorted_items)
        
        classifications = {'A': [], 'B': [], 'C': []}
        cumulative = 0
        
        for item in sorted_items:
            cumulative += item['annual_value']
            percentage = cumulative / total_value
            
            if percentage <= 0.8:
                classifications['A'].append(item)
            elif percentage <= 0.95:
                classifications['B'].append(item)
            else:
                classifications['C'].append(item)
        
        return classifications


class Recommendations:
    """Generate tactical business recommendations."""
    
    @staticmethod
    def generate_revenue_recommendations(data: pd.DataFrame) -> List[Dict]:
        """Generate revenue optimization recommendations."""
        recommendations = []
        
        high_ltv_users = len(data[data['ltv'] > data['ltv'].quantile(0.75)])
        ltv_pct = (high_ltv_users / len(data)) * 100
        
        recommendations.append({
            'title': 'Revenue Optimization',
            'recommendation': 'Add tiered pricing for high-LTV customers',
            'impact': '+8-12% MRR',
            'why': f'{ltv_pct:.0f}% of users fall into upsell-ready segment',
            'steps': [
                'Create pricing tiers based on usage',
                'Run email campaign to high-LTV segment',
                'Monitor conversion rates'
            ],
            'timeline': '30 days'
        })
        
        return recommendations
    
    @staticmethod
    def generate_retention_recommendations(churn_rate: float) -> List[Dict]:
        """Generate customer retention recommendations."""
        recommendations = []
        
        if churn_rate > 0.05:
            recommendations.append({
                'title': 'Retention Optimization',
                'recommendation': 'Launch win-back campaign',
                'impact': f'-{min(churn_rate * 30, 50)}% churn',
                'why': f'Current churn of {churn_rate*100:.1f}% is above threshold',
                'steps': [
                    'Segment at-risk customers',
                    'Create personalized outreach',
                    'Offer incentives'
                ],
                'timeline': '14 days'
            })
        
        return recommendations


class WhatIfAnalysis:
    """Scenario planning and what-if analysis."""
    
    @staticmethod
    def project_scenario(
        baseline: Dict,
        scenario: Dict,
        months: int = 3
    ) -> Dict:
        """Project business metrics for a scenario."""
        current_revenue = baseline['revenue']
        current_cac = baseline['cac']
        current_churn = baseline['churn']
        
        # Simulate scenario impact
        marketing_multiplier = scenario.get('marketing_spend', 1.0) / baseline.get('marketing_spend', 1.0)
        projected_revenue = current_revenue * (1 + (marketing_multiplier - 1) * 0.3)  # 30% elasticity
        projected_cac = current_cac / marketing_multiplier
        projected_churn = current_churn * (1 - scenario.get('retention_invest', 0) * 0.1)
        
        return {
            'projected_revenue': projected_revenue,
            'projected_cac': projected_cac,
            'projected_churn': projected_churn,
            'revenue_delta': projected_revenue - current_revenue,
            'cac_efficiency_improvement': ((current_cac - projected_cac) / current_cac) * 100
        }
    
    @staticmethod
    def plot_scenario_comparison(
        baseline: Dict,
        scenarios: Dict[str, Dict]
    ):
        """Plot scenario comparison."""
        scenarios_with_baseline = {'Baseline': baseline, **scenarios}
        
        revenue_data = [s['projected_revenue'] for s in scenarios_with_baseline.values()]
        names = list(scenarios_with_baseline.keys())
        
        fig = go.Figure(data=[
            go.Bar(x=names, y=revenue_data, marker_color=['#3B82F6'] + ['#F59E0B'] * len(scenarios))
        ])
        
        fig.update_layout(
            title='Revenue Projection by Scenario',
            yaxis_title='Projected Revenue ($)',
            height=400,
            template='plotly_dark'
        )
        
        return fig
