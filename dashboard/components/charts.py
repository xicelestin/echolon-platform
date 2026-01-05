"""
Standardized Chart Components for Echolon Dashboard

This module provides reusable chart functions with consistent styling,
color schemes, and layouts across the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional, List, Dict, Any

# Echolon Brand Colors
COLORS = {
    'primary': '#3B82F6',      # Blue
    'secondary': '#8B5CF6',    # Purple
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Orange
    'danger': '#EF4444',       # Red
    'info': '#06B6D4',         # Cyan
    'neutral': '#6B7280',      # Gray
    'background': '#F9FAFB',   # Light gray
    'text': '#111827',         # Dark gray
}

# Color palettes for multi-series charts
COLOR_PALETTE = [COLORS['primary'], COLORS['secondary'], COLORS['success'], 
                COLORS['warning'], COLORS['info'], COLORS['danger']]

# Default layout configuration
DEFAULT_LAYOUT = {
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white',
    'font': {'family': 'Inter, system-ui, sans-serif', 'color': COLORS['text']},
    'margin': {'t': 40, 'r': 20, 'b': 40, 'l': 60},
    'hovermode': 'closest',
    'hoverlabel': {'bgcolor': 'white', 'font_size': 12},
}


def apply_default_layout(fig: go.Figure, title: Optional[str] = None, 
                        height: int = 400) -> go.Figure:
    """Apply consistent layout styling to a Plotly figure."""
    layout_updates = DEFAULT_LAYOUT.copy()
    if title:
        layout_updates['title'] = {
            'text': title,
            'font': {'size': 16, 'weight': 600},
            'x': 0.05,
            'xanchor': 'left'
        }
    layout_updates['height'] = height
    fig.update_layout(**layout_updates)
    return fig


def create_metric_card_chart(value: float, previous_value: float, 
                             title: str, format_str: str = '${:,.0f}') -> go.Figure:
    """Create a compact trend indicator chart for metric cards."""
    change = ((value - previous_value) / previous_value * 100) if previous_value else 0
    color = COLORS['success'] if change >= 0 else COLORS['danger']
    
    fig = go.Figure(go.Indicator(
        mode='number+delta',
        value=value,
        delta={'reference': previous_value, 'relative': True, 'valueformat': '.1f'},
        number={'valueformat': format_str.replace('{:,', '').replace('}', '').replace('$', '$')},
        title={'text': title}
    ))
    
    fig.update_layout(height=120, margin={'t': 20, 'r': 20, 'b': 20, 'l': 20})
    return fig


def create_line_chart(df: pd.DataFrame, x_col: str, y_cols: List[str],
                     title: Optional[str] = None, height: int = 400,
                     y_title: Optional[str] = None) -> go.Figure:
    """Create a standardized line chart with multiple series."""
    fig = go.Figure()
    
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers',
            name=y_col,
            line={'color': COLOR_PALETTE[i % len(COLOR_PALETTE)], 'width': 2},
            marker={'size': 6},
            hovertemplate='<b>%{y:,.0f}</b><br>%{x}<extra></extra>'
        ))
    
    fig = apply_default_layout(fig, title, height)
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB', title=x_col)
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB', title=y_title)
    return fig


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str,
                    title: Optional[str] = None, height: int = 400,
                    orientation: str = 'v', color_col: Optional[str] = None) -> go.Figure:
    """Create a standardized bar chart."""
    fig = go.Figure()
    
    if color_col:
        colors = df[color_col].map(lambda x: COLORS.get(x, COLORS['primary']))
    else:
        colors = COLORS['primary']
    
    if orientation == 'v':
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color=colors,
            hovertemplate='<b>%{x}</b><br>%{y:,.0f}<extra></extra>'
        ))
    else:
        fig.add_trace(go.Bar(
            x=df[y_col],
            y=df[x_col],
            orientation='h',
            marker_color=colors,
            hovertemplate='<b>%{y}</b><br>%{x:,.0f}<extra></extra>'
        ))
    
    fig = apply_default_layout(fig, title, height)
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB')
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
    return fig


def create_pie_chart(df: pd.DataFrame, labels_col: str, values_col: str,
                    title: Optional[str] = None, height: int = 400) -> go.Figure:
    """Create a standardized pie chart."""
    fig = go.Figure(go.Pie(
        labels=df[labels_col],
        values=df[values_col],
        hole=0.3,  # Donut chart
        marker={'colors': COLOR_PALETTE},
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>'
    ))
    
    fig = apply_default_layout(fig, title, height)
    return fig


def create_stacked_area_chart(df: pd.DataFrame, x_col: str, y_cols: List[str],
                              title: Optional[str] = None, height: int = 400) -> go.Figure:
    """Create a standardized stacked area chart."""
    fig = go.Figure()
    
    for i, y_col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines',
            name=y_col,
            stackgroup='one',
            fillcolor=COLOR_PALETTE[i % len(COLOR_PALETTE)],
            line={'width': 0.5},
            hovertemplate='<b>%{fullData.name}</b><br>%{y:,.0f}<extra></extra>'
        ))
    
    fig = apply_default_layout(fig, title, height)
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB')
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
    return fig


def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str,
                       title: Optional[str] = None, height: int = 400,
                       size_col: Optional[str] = None, color_col: Optional[str] = None) -> go.Figure:
    """Create a standardized scatter plot."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        color_discrete_sequence=COLOR_PALETTE,
        hover_data=df.columns
    )
    
    fig = apply_default_layout(fig, title, height)
    fig.update_xaxes(showgrid=True, gridcolor='#E5E7EB', title=x_col)
    fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB', title=y_col)
    return fig


def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str,
                  title: Optional[str] = None, height: int = 400) -> go.Figure:
    """Create a standardized heatmap."""
    pivot_df = df.pivot(index=y_col, columns=x_col, values=value_col)
    
    fig = go.Figure(go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='Blues',
        hovertemplate='<b>%{x}</b><br>%{y}<br>Value: %{z:,.0f}<extra></extra>'
    ))
    
    fig = apply_default_layout(fig, title, height)
    return fig


def create_gauge_chart(value: float, max_value: float, title: str,
                      thresholds: Optional[Dict[str, float]] = None) -> go.Figure:
    """Create a gauge chart for KPIs."""
    if thresholds is None:
        thresholds = {'low': 0.3, 'medium': 0.7, 'high': 1.0}
    
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': COLORS['primary']},
            'steps': [
                {'range': [0, max_value * thresholds['low']], 'color': '#FEE2E2'},
                {'range': [max_value * thresholds['low'], max_value * thresholds['medium']], 'color': '#FEF3C7'},
                {'range': [max_value * thresholds['medium'], max_value], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300, margin={'t': 40, 'r': 40, 'b': 40, 'l': 40})
    return fig


# Example usage
if __name__ == '__main__':
    # Test data
    test_df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30),
        'Revenue': [1000 + i * 50 for i in range(30)],
        'Costs': [700 + i * 30 for i in range(30)]
    })
    
    # Create sample charts
    line_fig = create_line_chart(test_df, 'Date', ['Revenue', 'Costs'], 'Revenue vs Costs')
    print('Charts module loaded successfully!')
