"""Reusable UI components for Echolon Dashboard.

Provides production-grade card layouts, KPI displays, insight boxes,
and utility functions for building professional business dashboards.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ===== COLOR PALETTE ======
COLOR_PALETTE = {
    "primary": "#38bdf8",      # Sky blue
    "success": "#22c55e",      # Green
    "warning": "#f97316",      # Orange
    "danger": "#ef4444",       # Red
    "info": "#06b6d4",         # Cyan
    "dark_bg": "#0f172a",      # Slate 900
    "card_bg": "#020617",      # Slate 950
    "text_primary": "#f1f5f9",  # Slate 100
    "text_secondary": "#94a3b8", # Slate 400
    "border": "#1e293b",       # Slate 800
}

class TrendDirection(Enum):
    """Trend direction enum."""
    UP = "up"
    DOWN = "down"
    FLAT = "flat"

class Severity(Enum):
    """Severity level for insights."""
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    SUCCESS = "success"

# ===== METRIC CARD COMPONENT ======
def metric_card(
    title: str,
    value: str,
    delta: Optional[float] = None,
    delta_label: Optional[str] = None,
    helper_text: Optional[str] = None,
    icon: Optional[str] = None,
    trend: TrendDirection = TrendDirection.FLAT,
    col_span: int = 1,
) -> None:
    """Display a metric card with value, delta, and optional helper text.
    
    Args:
        title: Card title
        value: Main metric value to display
        delta: Numeric change (e.g., +12.5)
        delta_label: Label for delta (e.g., "MoM")
        helper_text: Helper text to display below
        icon: Unicode icon/emoji
        trend: Trend direction (up/down/flat)
        col_span: Column span for layout
    """
    trend_icon = {"up": "▲", "down": "▼", "flat": "→"}[trend.value]
    trend_color = {
        "up": COLOR_PALETTE["success"],
        "down": COLOR_PALETTE["danger"],
        "flat": COLOR_PALETTE["text_secondary"],
    }[trend.value]
    
    delta_html = ""
    if delta is not None:
        delta_sign = "+" if delta > 0 else ""
        delta_html = f"""<span style="color: {trend_color}; font-size: 14px; margin-left: 8px;">
            {trend_icon} {delta_sign}{delta:.1f}%
        </span>"""
        if delta_label:
            delta_html += f"<span style='color: {COLOR_PALETTE['text_secondary']}; font-size: 12px; margin-left: 4px;'>{delta_label}</span>"
    
    html_content = f"""
    <div style="
        background: {COLOR_PALETTE['card_bg']};
        border: 1px solid {COLOR_PALETTE['border']};
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="color: {COLOR_PALETTE['text_secondary']}; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                {icon if icon else ''} {title}
            </span>
        </div>
        <div style="display: flex; align-items: baseline;">
            <span style="color: {COLOR_PALETTE['text_primary']}; font-size: 32px; font-weight: 700;">
                {value}
            </span>
            {delta_html}
        </div>
        {f'<div style="color: {COLOR_PALETTE["text_secondary"]}; font-size: 12px; margin-top: 8px;">{helper_text}</div>' if helper_text else ''}
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)

# ===== INSIGHT BOX COMPONENT ======
def insight_box(
    title: str,
    body: str,
    severity: Severity = Severity.INFO,
    icon: str = "ⓘ",
) -> None:
    """Display an insight box with title, body, and severity level.
    
    Args:
        title: Insight title
        body: Insight body text (supports HTML/markdown)
        severity: Severity level (info/warning/danger/success)
        icon: Icon to display
    """
    color_map = {
        Severity.INFO: COLOR_PALETTE["info"],
        Severity.WARNING: COLOR_PALETTE["warning"],
        Severity.DANGER: COLOR_PALETTE["danger"],
        Severity.SUCCESS: COLOR_PALETTE["success"],
    }
    
    border_color = color_map[severity]
    
    html_content = f"""
    <div style="
        background: rgba(51, 65, 85, 0.3);
        border-left: 4px solid {border_color};
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    ">
        <div style="display: flex; gap: 12px; margin-bottom: 8px;">
            <span style="color: {border_color}; font-size: 18px;">{icon}</span>
            <span style="color: {COLOR_PALETTE['text_primary']}; font-weight: 600; font-size: 14px;">{title}</span>
        </div>
        <div style="color: {COLOR_PALETTE['text_secondary']}; font-size: 13px; line-height: 1.6; margin-left: 30px;">
            {body}
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)

# ===== SECTION HEADER COMPONENT ======
def section_header(title: str, subtitle: Optional[str] = None) -> None:
    """Display a section header.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
    """
    html_content = f"""
    <div style="margin: 32px 0 16px 0;">
        <h2 style="color: {COLOR_PALETTE['text_primary']}; font-size: 24px; font-weight: 700; margin: 0 0 8px 0;">
            {title}
        </h2>
        {f'<p style="color: {COLOR_PALETTE["text_secondary"]}; font-size: 13px; margin: 0;">{subtitle}</p>' if subtitle else ''}
        <hr style="border: none; border-top: 1px solid {COLOR_PALETTE['border']}; margin: 12px 0;"></hr>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# ===== TAG CHIP COMPONENT ======
def tag_chip(label: str, color: str = "primary") -> str:
    """Create a styled tag chip HTML.
    
    Args:
        label: Chip label
        color: Color type (primary/success/warning/danger/info)
    
    Returns:
        HTML string for the tag chip
    """
    bg_color = COLOR_PALETTE.get(color, COLOR_PALETTE["primary"])
    return f"""
    <span style="
        background: rgba({int(bg_color[1:3], 16)}, {int(bg_color[3:5], 16)}, {int(bg_color[5:7], 16)}, 0.2);
        border: 1px solid {bg_color};
        color: {bg_color};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin: 4px 4px 4px 0;
    ">{label}</span>
    """

# ===== CONFIDENCE BADGE ======
def confidence_badge(level: float) -> str:
    """Create a confidence badge (0-1).
    
    Args:
        level: Confidence level from 0-1
    
    Returns:
        Badge HTML and label
    """
    if level >= 0.8:
        label = "High confidence"
        color = COLOR_PALETTE["success"]
    elif level >= 0.5:
        label = "Medium confidence"
        color = COLOR_PALETTE["warning"]
    else:
        label = "Low confidence"
        color = COLOR_PALETTE["danger"]
    
    return f"{label} ({level*100:.0f}%)", color

# ===== GRID LAYOUT HELPER ======
def render_metric_grid(metrics: List[Dict[str, Any]], cols: int = 3) -> None:
    """Render a grid of metric cards.
    
    Args:
        metrics: List of metric dictionaries with keys: title, value, delta, helper_text, icon, trend
        cols: Number of columns
    """
    grid = st.columns(cols)
    for idx, metric in enumerate(metrics):
        col_idx = idx % cols
        with grid[col_idx]:
            metric_card(
                title=metric.get("title", ""),
                value=metric.get("value", "-"),
                delta=metric.get("delta"),
                delta_label=metric.get("delta_label"),
                helper_text=metric.get("helper_text"),
                icon=metric.get("icon"),
                trend=TrendDirection(metric.get("trend", "flat")),
            )

# ===== PLOTLY CHART STYLING ======
def get_dark_layout(**kwargs) -> dict:
    """Get dark mode layout template for Plotly.
    
    Returns:
        Layout dictionary
    """
    layout = {
        "template": "plotly_dark",
        "paper_bgcolor": COLOR_PALETTE["card_bg"],
        "plot_bgcolor": COLOR_PALETTE["card_bg"],
        "font": {"color": COLOR_PALETTE["text_primary"], "family": "Inter, sans-serif"},
        "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
        "hovermode": "x unified",
    }
    layout.update(kwargs)
    return layout

if __name__ == "__main__":
    st.set_page_config(page_title="Components Test", layout="wide")
    st.title("UI Components Test")
    
    section_header("Metric Cards", "Sample metric cards with various states")
    render_metric_grid([
        {"title": "Revenue", "value": "$485.2K", "delta": 12.5, "delta_label": "MoM", "icon": "💰", "trend": "up"},
        {"title": "Conversion Rate", "value": "3.24%", "delta": -0.8, "delta_label": "MoM", "icon": "📊", "trend": "down"},
        {"title": "Customer LTV", "value": "$1,240", "delta": 8.2, "delta_label": "QoQ", "icon": "👥", "trend": "up"},
    ])
    
    section_header("Insights", "Sample insight boxes")
    insight_box("Revenue Opportunity", "LTV increased 12% MoM — driven by repeat purchases and higher retention.", Severity.SUCCESS)
    insight_box("Churn Alert", "Monthly churn increased to 5.2% from 4.1% last month. Investigate customer satisfaction scores.", Severity.WARNING)
