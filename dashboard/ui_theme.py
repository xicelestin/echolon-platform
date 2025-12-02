"""
Echolon AI Design System / UI Theme

Centralized design tokens and styling utilities for consistent,
modern SaaS UI across the Streamlit dashboard.

Usage:
    from ui_theme import PRIMARY, BG_DARK, render_global_styles
    render_global_styles()  # Call once in app.py
"""

# ============================================================================
# COLOR PALETTE
# ============================================================================

# Primary brand color (Echolon Blue)
PRIMARY = "#3B82F6"
PRIMARY_DARK = "#1D4ED8"
PRIMARY_LIGHT = "#60A5FA"

# Accent colors
ACCENT_GREEN = "#22C55E"  # Positive, growth, gains
ACCENT_GREEN_DARK = "#15803D"
ACCENT_RED = "#EF4444"  # Negative, risk, loss
ACCENT_RED_DARK = "#991B1B"
ACCENT_AMBER = "#F59E0B"  # Warning, alert, caution
ACCENT_AMBER_DARK = "#B45309"

# Background colors (Dark theme)
BG_DARK = "#020617"  # Main background
BG_ELEVATED = "#0F172A"  # Slightly elevated
PANEL_BG = "#0F172A"  # Panel/card background
CARD_BG = "#1E293B"  # Card background (elevated)
CARD_BORDER = "#334155"  # Card border

# Text colors
TEXT_MAIN = "#F9FAFB"  # Primary text (near white)
TEXT_SECONDARY = "#E5E7EB"  # Secondary text
TEXT_MUTED = "#9CA3AF"  # Muted text (tertiary)
TEXT_SOFT = "#6B7280"  # Soft text (quaternary)

# Other
DIVIDER = "#1E293B"
SUCCESS = "#10B981"  # Success state
INFO = "#0EA5E9"  # Info state
ERROR = "#EF4444"  # Error state

# ============================================================================
# TYPOGRAPHY
# ============================================================================

FONT_FAMILY = "'Inter', 'Segoe UI', sans-serif"
FONT_SIZE_XS = "12px"
FONT_SIZE_SM = "14px"
FONT_SIZE_BASE = "16px"
FONT_SIZE_LG = "18px"
FONT_SIZE_XL = "24px"
FONT_SIZE_2XL = "32px"

FONT_WEIGHT_NORMAL = "400"
FONT_WEIGHT_MEDIUM = "500"
FONT_WEIGHT_SEMIBOLD = "600"
FONT_WEIGHT_BOLD = "700"

# ============================================================================
# SPACING
# ============================================================================

SPACE_XS = 4
SPACE_S = 8
SPACE_M = 12
SPACE_L = 16
SPACE_XL = 24
SPACE_2XL = 32

# ============================================================================
# BORDER & RADIUS
# ============================================================================

RADIUS_SM = "4px"
RADIUS_MD = "8px"
RADIUS_LG = "12px"
RADIUS_PILL = "999px"

BORDER_WIDTH = "1px"
BORDER_WIDTH_2 = "2px"

# ============================================================================
# SHADOWS
# ============================================================================

SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

# ============================================================================
# GLOBAL CSS / STYLE INJECTION
# ============================================================================

def render_global_styles():
    """
    Inject global CSS styles into the Streamlit app.
    Call this once in app.py after st.set_page_config().
    """
    import streamlit as st
    
    global_css = f"""
    <style>
    /* Root & Body */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BG_DARK} !important;
        color: {TEXT_MAIN};
        font-family: {FONT_FAMILY};
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {BG_ELEVATED} !important;
        border-right: {BORDER_WIDTH} solid {DIVIDER};
    }}
    
    [data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
        background-color: transparent;
    }}
    
    /* Sidebar labels */
    [data-testid="stSidebar"] .stRadio > label {{
        color: {TEXT_MAIN} !important;
        font-weight: {FONT_WEIGHT_MEDIUM};
        padding: 8px 12px;
        border-radius: {RADIUS_MD};
        transition: all 0.2s ease;
    }}
    
    [data-testid="stSidebar"] .stRadio > label:hover {{
        background-color: rgba(59, 130, 246, 0.1);
    }}
    
    /* Selected radio button */
    [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] + label {{
        background-color: {PRIMARY};
        color: white !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: {RADIUS_PILL};
        font-weight: {FONT_WEIGHT_SEMIBOLD};
        padding: 8px 24px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
    }}
    
    .stButton > button:hover {{
        background-color: {PRIMARY_DARK};
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }}
    
    .stButton > button:active {{
        transform: translateY(0px);
    }}
    
    /* Cards & Containers */
    [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {{
        background-color: {CARD_BG};
        border: {BORDER_WIDTH} solid {CARD_BORDER};
        border-radius: {RADIUS_LG};
        padding: 20px;
        margin-bottom: 16px;
    }}
    
    /* Headings */
    h1 {{
        color: {TEXT_MAIN};
        font-size: {FONT_SIZE_2XL};
        font-weight: {FONT_WEIGHT_BOLD};
        margin-top: 24px;
        margin-bottom: 8px;
    }}
    
    h2 {{
        color: {TEXT_MAIN};
        font-size: {FONT_SIZE_XL};
        font-weight: {FONT_WEIGHT_SEMIBOLD};
        margin-top: 20px;
        margin-bottom: 12px;
        border-bottom: {BORDER_WIDTH} solid {DIVIDER};
        padding-bottom: 12px;
    }}
    
    h3 {{
        color: {TEXT_SECONDARY};
        font-size: {FONT_SIZE_LG};
        font-weight: {FONT_WEIGHT_SEMIBOLD};
        margin-top: 16px;
        margin-bottom: 8px;
    }}
    
    /* Text */
    p, span, label {{
        color: {TEXT_MAIN};
    }}
    
    .stMarkdown {{
        color: {TEXT_MAIN};
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {{
        background-color: {BG_ELEVATED} !important;
        color: {TEXT_MAIN} !important;
        border: {BORDER_WIDTH} solid {CARD_BORDER} !important;
        border-radius: {RADIUS_MD};
    }}
    
    /* Sliders */
    .stSlider > div > div > div {{
        background-color: {BG_ELEVATED};
        border: {BORDER_WIDTH} solid {CARD_BORDER};
        border-radius: {RADIUS_LG};
        padding: 12px;
    }}
    
    /* Tabs */
    [data-testid="stTabs"] {{
        background-color: transparent;
    }}
    
    [role="tab"] {{
        color: {TEXT_MUTED};
        border-bottom: {BORDER_WIDTH_2} solid transparent;
        padding: 12px 16px;
        font-weight: {FONT_WEIGHT_MEDIUM};
        transition: all 0.2s ease;
    }}
    
    [role="tab"]:hover {{
        color: {TEXT_MAIN};
        border-bottom-color: {PRIMARY};
    }}
    
    [aria-selected="true"][role="tab"] {{
        color: {PRIMARY};
        border-bottom-color: {PRIMARY};
    }}
    
    /* Info/Warning/Error boxes */
    [data-testid="stAlert"] {{
        background-color: rgba(59, 130, 246, 0.1);
        border-left: 4px solid {PRIMARY};
        border-radius: {RADIUS_MD};
        padding: 12px 16px;
    }}
    
    /* Horizontal rule */
    hr {{
        border: none;
        border-top: {BORDER_WIDTH} solid {DIVIDER};
        margin: 24px 0;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {BG_DARK};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {CARD_BORDER};
        border-radius: {RADIUS_SM};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {PRIMARY};
    }}
    </style>
    """
    
    st.markdown(global_css, unsafe_allow_html=True)


# ============================================================================
# STYLE DICTIONARIES / HELPERS
# ============================================================================

def get_metric_delta_color(delta_type: str) -> str:
    """
    Return color for delta indicator based on type.
    Args:
        delta_type: 'up', 'down', or 'neutral'
    Returns:
        Color hex string
    """
    if delta_type == "up":
        return ACCENT_GREEN
    elif delta_type == "down":
        return ACCENT_RED
    else:
        return TEXT_MUTED


def get_tag_color(variant: str) -> str:
    """
    Get color for a tag/badge variant.
    Args:
        variant: 'growth', 'risk', 'efficiency', 'innovation', 'default'
    Returns:
        Color hex string
    """
    colors = {
        "growth": ACCENT_GREEN,
        "risk": ACCENT_RED,
        "efficiency": ACCENT_AMBER,
        "innovation": PRIMARY,
        "default": TEXT_MUTED,
    }
    return colors.get(variant, colors["default"])


CARD_STYLE = {
    "background-color": CARD_BG,
    "border": f"1px solid {CARD_BORDER}",
    "border-radius": RADIUS_LG,
    "padding": "20px",
    "box-shadow": SHADOW_MD,
}

METRIC_CARD_STYLE = {
    "background": f"linear-gradient(135deg, {PRIMARY}, {PRIMARY_DARK})",
    "border-radius": RADIUS_LG,
    "padding": "24px",
    "border-left": f"4px solid {ACCENT_GREEN}",
    "box-shadow": SHADOW_MD,
}

SECTION_TITLE_STYLE = {
    "font-size": FONT_SIZE_XL,
    "font-weight": FONT_WEIGHT_SEMIBOLD,
    "color": TEXT_MAIN,
    "margin-top": "24px",
    "margin-bottom": "12px",
}

MUTED_TEXT_STYLE = {
    "font-size": FONT_SIZE_SM,
    "color": TEXT_MUTED,
    "font-weight": FONT_WEIGHT_NORMAL,
}
