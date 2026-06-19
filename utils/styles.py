"""
Shared design system for the Healthcare AI Assistant.

Single source of truth for every color used in the app. The app is locked to
a dark theme via .streamlit/config.toml, and every custom component below
uses explicit text + background pairs from this palette — never relying on
Streamlit's automatic light/dark switching. This is what fixes the
"text invisible in dark mode" bug: there is only ever one mode, everywhere.
"""

import streamlit as st

COLORS = {
    "bg":            "#0E1117",
    "surface":       "#161B22",
    "surface_alt":   "#1C2230",
    "border":        "#2A3340",
    "text":          "#E6EDF3",
    "text_dim":      "#9DA7B3",
    "primary":       "#22C58B",
    "primary_dk":    "#17996B",
    "accent_blue":   "#4DA3FF",
    "accent_purp":   "#A78BFA",
    "warn_bg":       "#3A2E12",
    "warn_border":   "#D9A331",
    "warn_text":     "#F4D58D",
    "danger_bg":     "#3A1414",
    "danger_border": "#E5484D",
    "danger_text":   "#FFB3B3",
}


def inject_base_css():
    """Call once per page, right after st.set_page_config()."""
    c = COLORS
    st.markdown(f"""
    <style>
        .stApp {{ background-color: {c['bg']}; }}

        .main-header {{
            background: linear-gradient(135deg, {c['primary_dk']} 0%, {c['primary']} 100%);
            padding: 2rem; border-radius: 14px; color: #FFFFFF; margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(34,197,139,0.15);
        }}
        .main-header h1 {{ color: #FFFFFF; margin-bottom: 0.3rem; }}
        .main-header p {{ color: rgba(255,255,255,0.92); }}

        .card {{
            background: {c['surface']}; border: 1px solid {c['border']};
            border-radius: 12px; padding: 1.1rem 1.3rem; margin: 0.55rem 0;
            color: {c['text']}; transition: border-color 0.15s, transform 0.15s;
        }}
        .card:hover {{ border-color: {c['primary']}; transform: translateY(-1px); }}
        .card strong {{ color: {c['text']}; }}

        .badge {{
            display: inline-block; border-radius: 20px; padding: 3px 12px;
            font-size: 0.78rem; font-weight: 600; margin: 2px;
        }}
        .badge-primary {{ background: rgba(34,197,139,0.15); color: {c['primary']}; }}
        .badge-info    {{ background: rgba(77,163,255,0.15); color: {c['accent_blue']}; }}
        .badge-purple  {{ background: rgba(167,139,250,0.15); color: {c['accent_purp']}; }}
        .badge-warn    {{ background: rgba(217,163,49,0.18); color: {c['warn_text']}; }}

        .callout-warn {{
            background: {c['warn_bg']}; border-left: 4px solid {c['warn_border']};
            color: {c['warn_text']}; padding: 0.9rem 1.1rem; border-radius: 0 10px 10px 0;
            margin: 0.9rem 0; font-size: 0.95rem;
        }}
        .callout-warn strong {{ color: {c['warn_text']}; }}

        .callout-danger {{
            background: {c['danger_bg']}; border-left: 4px solid {c['danger_border']};
            color: {c['danger_text']}; padding: 0.9rem 1.1rem; border-radius: 0 10px 10px 0;
            margin: 0.9rem 0; font-size: 0.95rem;
        }}

        .result-box {{
            background: {c['surface']}; border: 1px solid {c['border']};
            border-left: 4px solid {c['primary']}; border-radius: 0 12px 12px 0;
            padding: 1.3rem 1.5rem; margin: 1rem 0; color: {c['text']}; line-height: 1.6;
        }}
        .result-box-blue   {{ border-left-color: {c['accent_blue']}; }}
        .result-box-purple {{ border-left-color: {c['accent_purp']}; }}
        .result-box-warn   {{ border-left-color: {c['warn_border']}; }}

        .chat-user {{
            background: {c['surface_alt']}; border: 1px solid {c['border']};
            border-radius: 14px 14px 4px 14px; padding: 0.85rem 1.1rem;
            margin: 0.45rem 0 0.45rem 15%; color: {c['text']};
        }}
        .chat-bot {{
            background: {c['surface']}; border: 1px solid {c['primary_dk']};
            border-radius: 14px 14px 14px 4px; padding: 0.85rem 1.1rem;
            margin: 0.45rem 15% 0.45rem 0; color: {c['text']};
        }}
        .chat-user strong, .chat-bot strong {{ color: {c['primary']}; }}

        .extracted-text {{
            background: {c['surface_alt']}; border: 1px solid {c['border']};
            border-radius: 8px; padding: 1rem; font-family: 'SF Mono', monospace;
            font-size: 0.82rem; color: {c['text_dim']}; max-height: 220px; overflow-y: auto;
        }}

        .footer-note {{
            text-align: center; color: {c['text_dim']}; font-size: 0.82rem;
            margin-top: 1.5rem;
        }}

        .stButton > button {{
            background-color: {c['primary']}; color: #0E1117; border: none;
            border-radius: 8px; padding: 0.5rem 1.4rem; font-weight: 600;
        }}
        .stButton > button:hover {{ background-color: {c['primary_dk']}; color: #FFFFFF; }}

        .stButton > button[kind="secondary"] {{
            background-color: transparent; color: {c['text']};
            border: 1px solid {c['border']};
        }}
        .stButton > button[kind="secondary"]:hover {{ border-color: {c['primary']}; color: {c['primary']}; }}

        section[data-testid="stSidebar"] {{ background-color: {c['surface']}; }}
    </style>
    """, unsafe_allow_html=True)


def callout(text: str, kind: str = "warn"):
    cls = "callout-warn" if kind == "warn" else "callout-danger"
    icon = "⚠️" if kind == "warn" else "⛔"
    st.markdown(f"<div class='{cls}'>{icon} {text}</div>", unsafe_allow_html=True)


def footer():
    st.markdown("---")
    st.markdown(
        "<p class='footer-note'>Healthcare AI Assistant · Portfolio Project · "
        "Not a substitute for professional medical advice</p>",
        unsafe_allow_html=True,
    )
