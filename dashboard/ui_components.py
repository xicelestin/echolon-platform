"""
Echolon AI Component Library

Reusable Streamlit UI components built on top of the design system.
Provides helper functions for consistent, polished UI across all pages.

Usage:
    from ui_components import render_page_header, metric_row, card
    render_page_header("Page Title", "Page subtitle")
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import ui_theme as theme


def render_page_header(title: str, subtitle: str, badge: Optional[str] = None, icon: Optional[str] = None):
    """
    Render a polished page header with title, subtitle, and optional badge.
    Args:
        title: Main page title (H1)
        subtitle: Subtitle or description (smaller, muted text)
        badge: Optional badge text (e.g., "Live", "Demo", "Beta")
        icon: Optional emoji/icon to display beside title
    """
    if icon:
        st.markdown(f"# {icon} {title}", unsafe_allow_html=True)
    else:
        st.markdown(f"# {title}")
    st.markdown(f"<p style='color: {theme.TEXT_MUTED}; font-size: {theme.FONT_SIZE_SM}; margin: 8px 0 0 0;'>{subtitle}</p>", unsafe_allow_html=True)
    if badge:
        st.markdown(f"<span style='background-color: rgba(59, 130, 246, 0.2); color: {theme.PRIMARY}; padding: 4px 12px; border-radius: {theme.RADIUS_PILL}; font-size: {theme.FONT_SIZE_XS}; font-weight: {theme.FONT_WEIGHT_SEMIBOLD}; margin-top: 8px;'>{badge}</span>", unsafe_allow_html=True)


def section_title(text: str, tag: Optional[str] = None):
    """
    Render a section title (H2) with optional tag badge.
    """
    st.markdown(f"## {text}")
    if tag:
        color = theme.get_tag_color(tag.lower())
        st.markdown(f"<span style='background-color: {color}20; color: {color}; padding: 4px 12px; border-radius: {theme.RADIUS_PILL}; font-size: {theme.FONT_SIZE_XS}; font-weight: {theme.FONT_WEIGHT_SEMIBOLD};'>{tag}</span>", unsafe_allow_html=True)


def pill_tag(text: str, variant: str = "default", small: bool = False):
    """
    Render a pill/badge tag.
    """
    color = theme.get_tag_color(variant)
    size = theme.FONT_SIZE_XS if small else theme.FONT_SIZE_SM
    padding = "2px 8px" if small else "4px 12px"
    st.markdown(f"<span style='display: inline-block; background-color: {color}20; color: {color}; padding: {padding}; border-radius: {theme.RADIUS_PILL}; font-size: {size}; font-weight: {theme.FONT_WEIGHT_SEMIBOLD};'>{text}</span>", unsafe_allow_html=True)


def metric_row(metrics: List[Dict[str, Any]]):
    """
    Render a row of metric cards with values, labels, and optional deltas.
    """
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            with st.container():
                st.markdown(f"<p style='color: {theme.TEXT_MUTED}; font-size: {theme.FONT_SIZE_SM}; margin: 0 0 8px 0; text-transform: uppercase; font-weight: {theme.FONT_WEIGHT_SEMIBOLD};'>{metric['label']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: {theme.TEXT_MAIN}; font-size: {theme.FONT_SIZE_2XL}; margin: 0 0 4px 0; font-weight: {theme.FONT_WEIGHT_BOLD};'>{metric['value']}</p>", unsafe_allow_html=True)
                if "delta" in metric:
                    delta_color = theme.get_metric_delta_color(metric.get("delta_type", "neutral"))
                    st.markdown(f"<p style='color: {delta_color}; font-size: {theme.FONT_SIZE_SM}; margin: 0; font-weight: {theme.FONT_WEIGHT_MEDIUM};'>{metric['delta']}</p>", unsafe_allow_html=True)
                if "help_text" in metric:
                    st.caption(metric["help_text"])


def divider():
    """Render a styled divider."""
    st.markdown(f"<hr style='border: none; border-top: 1px solid {theme.DIVIDER}; margin: 24px 0;' />", unsafe_allow_html=True)


def muted_text(text: str):
    """Render muted/secondary text."""
    st.markdown(f"<p style='color: {theme.TEXT_MUTED}; font-size: {theme.FONT_SIZE_SM}; margin: 0;'>{text}</p>", unsafe_allow_html=True)


def success_badge(text: str):
    """Render a success-colored badge."""
    st.markdown(f"<span style='background-color: {theme.ACCENT_GREEN}20; color: {theme.ACCENT_GREEN}; padding: 4px 12px; border-radius: {theme.RADIUS_PILL}; font-size: {theme.FONT_SIZE_SM}; font-weight: {theme.FONT_WEIGHT_SEMIBOLD};'>{text}</span>", unsafe_allow_html=True)


def risk_badge(text: str):
    """Render a risk-colored badge."""
    st.markdown(f"<span style='background-color: {theme.ACCENT_RED}20; color: {theme.ACCENT_RED}; padding: 4px 12px; border-radius: {theme.RADIUS_PILL}; font-size: {theme.FONT_SIZE_SM}; font-weight: {theme.FONT_WEIGHT_SEMIBOLD};'>{text}</span>", unsafe_allow_html=True)


def empty_state(icon: str, title: str, description: str):
    """
    Render an empty state placeholder.
    """
    st.markdown(f"<div style='text-align: center; padding: 40px 20px;'><p style='font-size: 48px; margin: 0;'>{icon}</p><h3 style='color: {theme.TEXT_MAIN}; margin: 16px 0 8px 0;'>{title}</h3><p style='color: {theme.TEXT_MUTED}; margin: 0;'>{description}</p></div>", unsafe_allow_html=True)
