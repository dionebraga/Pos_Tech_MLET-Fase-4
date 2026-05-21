# -*- coding: utf-8 -*-

"""
AI Quant - Premium LSTM Trading Terminal
Tech Challenge Fase 4 - PosTech MLET FIAP
Construido por: Dione Braga Ferreira

Para rodar:
    streamlit run dashboard.py
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False



# ============================================================================
#  CONFIG
# ============================================================================
st.set_page_config(
    page_title="AI Quant • Premium Trading Terminal",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Fusos horários
BRT = timezone(timedelta(hours=-3))   # Brasília (UTC-3)
ET  = timezone(timedelta(hours=-4))   # Eastern Daylight Time (NYSE, UTC-4 de mar-nov)

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Trading"
if "active_kpi" not in st.session_state:
    st.session_state.active_kpi = None


# ============================================================================
#  CSS — Premium Terminal aesthetic
# ============================================================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,600;9..144,700;9..144,800&family=Geist:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-deep: #050507;
        --bg-base: #0A0A0E;
        --bg-elevated: #11111A;
        --bg-card: #14141F;
        --bg-overlay: rgba(255,255,255,0.02);
        --border-subtle: rgba(255,255,255,0.06);
        --border-strong: rgba(255,255,255,0.12);

        --text-primary: #FAFAFA;
        --text-secondary: #A1A1AA;
        --text-tertiary: #71717A;
        --text-muted: #52525B;

        --accent: #00FF88;
        --accent-dim: rgba(0,255,136,0.15);
        --accent-glow: rgba(0,255,136,0.4);
        --warning: #FF9500;
        --warning-dim: rgba(255,149,0,0.15);
        --danger: #FF3B3B;
        --danger-dim: rgba(255,59,59,0.15);
        --info: #5B9DFF;
        --info-dim: rgba(91,157,255,0.15);
        --purple: #B794F4;
        --purple-dim: rgba(183,148,244,0.15);

        --font-display: 'Fraunces', Georgia, serif;
        --font-body: 'Geist', -apple-system, system-ui, sans-serif;
        --font-mono: 'JetBrains Mono', 'Courier New', monospace;
    }

    /* ━━ SCROLLBAR ━━ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    html, body, [class*="css"]  {
        font-family: var(--font-body) !important;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }

    /* ━━ BACKGROUND ━━ */
    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0,255,136,0.05) 0%, transparent 50%),
            radial-gradient(ellipse 60% 50% at 100% 100%, rgba(91,157,255,0.04) 0%, transparent 50%),
            linear-gradient(180deg, var(--bg-deep) 0%, var(--bg-base) 100%);
        color: var(--text-primary);
    }

    #MainMenu, footer { display: none !important; }
    .stDeployButton { display: none !important; }
    header[data-testid="stHeader"] {
        position: absolute !important;
        top: 0; left: 0; right: 0;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        z-index: 99999;
    }
    .block-container { padding-top: 0 !important; max-width: 1600px !important; }

    /* ━━ FIX SIDEBAR ━━ */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-headerNoPadding"],
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 99999 !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        background: var(--bg-elevated) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        color: var(--accent) !important;
        box-shadow: 0 0 20px -8px var(--accent-glow) !important;
        cursor: pointer !important;
        transition: box-shadow 0.2s ease !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"]:hover {
        box-shadow: 0 0 28px -4px var(--accent-glow) !important;
    }
    button[data-testid="stSidebarCollapsedControl"] svg,
    button[data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        fill: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* ━━ SIDEBAR ━━ */
    section[data-testid="stSidebar"] {
        background: var(--bg-deep) !important;
        border-right: 1px solid var(--border-subtle);
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: var(--text-tertiary) !important;
        font-size: 0.7rem !important; font-weight: 500 !important;
        text-transform: uppercase; letter-spacing: 0.12em !important;
        font-family: var(--font-mono) !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.85rem !important;
        transition: border-color 0.2s ease !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
        border-color: var(--border-strong) !important;
    }

    .brand {
        display: flex; align-items: center; gap: 12px;
        padding: 4px 0 28px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 24px;
    }
    .brand-mark {
        width: 40px; height: 40px;
        background: var(--bg-elevated);
        border: 1px solid var(--accent);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-family: var(--font-mono); color: var(--accent);
        font-size: 1.1rem; font-weight: 700;
        box-shadow: 0 0 20px -4px var(--accent-glow);
        transition: box-shadow 0.3s ease;
    }
    .brand-mark:hover { box-shadow: 0 0 30px -2px var(--accent-glow); }
    .brand-text { display: flex; flex-direction: column; line-height: 1; }
    .brand-name {
        font-family: var(--font-display); font-weight: 700;
        font-size: 1.35rem; color: var(--text-primary);
        letter-spacing: -0.02em;
    }
    .brand-tag {
        font-family: var(--font-mono); font-size: 0.65rem;
        color: var(--text-tertiary); margin-top: 4px;
        letter-spacing: 0.15em; text-transform: uppercase;
    }

    .nav-label {
        font-family: var(--font-mono); font-size: 0.65rem;
        color: var(--text-muted); letter-spacing: 0.15em;
        text-transform: uppercase; margin: 24px 0 12px 0;
        padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);
    }

    .author {
        margin-top: 20px; padding: 14px 14px 14px 18px;
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: 10px; position: relative; overflow: hidden;
        transition: border-color 0.2s ease, background 0.2s ease;
    }
    .author:hover {
        border-color: var(--border-strong);
        background: var(--bg-card);
    }
    .author::before {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, var(--accent), rgba(0,255,136,0.3));
    }
    .author-label {
        font-family: var(--font-mono); font-size: 0.65rem;
        color: var(--text-tertiary); letter-spacing: 0.15em;
        text-transform: uppercase; margin-bottom: 6px;
    }
    .author-name {
        font-family: var(--font-display); font-size: 0.98rem;
        color: var(--text-primary); font-weight: 600;
        letter-spacing: -0.01em;
    }
    .author-subtitle {
        font-size: 0.72rem; color: var(--text-tertiary); margin-top: 3px;
    }

    /* ━━ TICKER TAPE ━━ */
    .ticker-bar {
        background: var(--bg-deep);
        border-top: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
        padding: 11px 0; margin: -1rem -3rem 24px -3rem;
        overflow: hidden; position: relative;
    }
    .ticker-bar::before, .ticker-bar::after {
        content: ""; position: absolute; top: 0; bottom: 0;
        width: 100px; z-index: 2; pointer-events: none;
    }
    .ticker-bar::before { left: 0; background: linear-gradient(90deg, var(--bg-deep) 20%, transparent); }
    .ticker-bar::after  { right: 0; background: linear-gradient(270deg, var(--bg-deep) 20%, transparent); }
    .ticker-track {
        display: flex; gap: 52px;
        animation: scroll-ticker 65s linear infinite;
        white-space: nowrap; width: max-content;
    }
    .ticker-bar:hover .ticker-track { animation-play-state: paused; }
    .ticker-item {
        display: inline-flex; align-items: center; gap: 10px;
        font-family: var(--font-mono); font-size: 0.82rem;
        cursor: default;
    }
    .ticker-sym { color: var(--text-secondary); font-weight: 600; letter-spacing: 0.04em; }
    .ticker-px { color: var(--text-primary); font-feature-settings: "tnum"; }
    .ticker-dlt-up { color: var(--accent); font-weight: 500; }
    .ticker-dlt-dn { color: var(--danger); font-weight: 500; }
    .ticker-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--border-strong); }
    @keyframes scroll-ticker {
        from { transform: translateX(0); }
        to   { transform: translateX(-50%); }
    }

    /* ━━ STATUS BAR ━━ */
    .status-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 4px 0 20px 0; gap: 20px;
        font-family: var(--font-mono); font-size: 0.78rem;
    }
    .status-group { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }
    .status-item {
        display: inline-flex; gap: 8px; align-items: center;
        color: var(--text-tertiary);
    }
    .status-item strong { color: var(--text-primary); font-weight: 500; }
    .status-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--accent); box-shadow: 0 0 8px var(--accent-glow);
        animation: pulse 2.5s ease-in-out infinite;
        flex-shrink: 0;
    }
    .status-dot.warn { background: var(--warning); box-shadow: 0 0 8px rgba(255,149,0,0.5); animation-delay: 0.4s; }
    .status-dot.off  { background: var(--text-muted); box-shadow: none; animation: none; }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.45; transform: scale(0.8); }
    }

    /* ━━ HERO ━━ */
    .hero {
        padding: 10px 0 34px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 28px;
    }
    .hero-eyebrow {
        font-family: var(--font-mono); font-size: 0.72rem;
        color: var(--text-tertiary); letter-spacing: 0.2em;
        text-transform: uppercase; margin-bottom: 14px;
        display: flex; align-items: center; gap: 10px;
    }
    .hero-eyebrow .blink {
        color: var(--accent); animation: blink 1.6s ease-in-out infinite;
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
    .hero h1 {
        font-family: var(--font-display) !important;
        font-size: clamp(2.4rem, 5vw, 3.8rem) !important;
        font-weight: 400 !important;
        color: var(--text-primary);
        margin: 0; line-height: 1.05;
        letter-spacing: -0.03em;
    }
    .hero h1 em { font-style: italic; color: var(--accent); }
    .hero-sub {
        margin-top: 16px; display: flex; align-items: center; gap: 18px;
        flex-wrap: wrap;
    }
    .hero-sub-item {
        font-family: var(--font-mono); font-size: 0.82rem;
        color: var(--text-secondary);
    }
    .hero-sub-item strong { color: var(--text-primary); font-weight: 500; }
    .hero-sub-divider {
        width: 4px; height: 4px; border-radius: 50%;
        background: var(--border-strong);
    }

    /* ━━ KPI CARDS ━━ */
    .kpi {
        position: relative;
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        transition: border-color 0.25s ease, transform 0.25s cubic-bezier(0.4,0,0.2,1),
                    box-shadow 0.25s ease;
        overflow: hidden;
        min-height: 200px;
        cursor: default;
    }
    .kpi:hover {
        border-color: var(--border-strong);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px -8px rgba(0,0,0,0.4);
    }
    .kpi::before {
        content: ""; position: absolute; top: 0; left: 0; right: 0;
        height: 2px; opacity: 0.6;
        transition: opacity 0.25s ease, height 0.25s ease;
    }
    .kpi:hover::before { opacity: 1; height: 3px; }
    .kpi.accent::before { background: linear-gradient(90deg, transparent 0%, var(--accent) 50%, transparent 100%); }
    .kpi.info::before   { background: linear-gradient(90deg, transparent 0%, var(--info) 50%, transparent 100%); }
    .kpi.purple::before { background: linear-gradient(90deg, transparent 0%, var(--purple) 50%, transparent 100%); }
    .kpi.warning::before{ background: linear-gradient(90deg, transparent 0%, var(--warning) 50%, transparent 100%); }

    .kpi.active { border-color: var(--border-strong); transform: translateY(-2px); }
    .kpi.active::before { opacity: 1; height: 3px; }
    .kpi.active.accent  { background: linear-gradient(160deg, rgba(0,255,136,0.05) 0%, var(--bg-card) 60%); box-shadow: 0 0 40px -16px var(--accent-glow); }
    .kpi.active.info    { background: linear-gradient(160deg, rgba(91,157,255,0.05) 0%, var(--bg-card) 60%); box-shadow: 0 0 40px -16px rgba(91,157,255,0.3); }
    .kpi.active.purple  { background: linear-gradient(160deg, rgba(183,148,244,0.05) 0%, var(--bg-card) 60%); box-shadow: 0 0 40px -16px rgba(183,148,244,0.3); }
    .kpi.active.warning { background: linear-gradient(160deg, rgba(255,149,0,0.05) 0%, var(--bg-card) 60%); box-shadow: 0 0 40px -16px rgba(255,149,0,0.3); }

    .kpi-head {
        display: flex; justify-content: space-between; align-items: flex-start;
        margin-bottom: 14px;
    }
    .kpi-label {
        font-family: var(--font-mono); font-size: 0.68rem;
        color: var(--text-tertiary); letter-spacing: 0.14em;
        text-transform: uppercase; font-weight: 500;
    }
    .kpi-icon {
        width: 30px; height: 30px; border-radius: 7px;
        background: var(--bg-deep); border: 1px solid var(--border-subtle);
        display: flex; align-items: center; justify-content: center;
        font-family: var(--font-mono); font-size: 0.9rem; font-weight: 700;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi.accent  .kpi-icon { color: var(--accent);  border-color: var(--accent-dim); }
    .kpi.info    .kpi-icon { color: var(--info);    border-color: var(--info-dim); }
    .kpi.purple  .kpi-icon { color: var(--purple);  border-color: var(--purple-dim); }
    .kpi.warning .kpi-icon { color: var(--warning); border-color: var(--warning-dim); }
    .kpi:hover .kpi-icon   { box-shadow: 0 0 12px -2px currentColor; }

    .kpi-value {
        font-family: var(--font-mono);
        font-size: 1.9rem; font-weight: 600;
        color: var(--text-primary); line-height: 1;
        letter-spacing: -0.02em; margin-bottom: 10px;
        font-feature-settings: "tnum";
    }
    .kpi-delta {
        font-family: var(--font-mono); font-size: 0.78rem; font-weight: 500;
        display: inline-flex; align-items: center; gap: 5px;
        margin-bottom: 14px; padding: 3px 8px;
        border-radius: 5px;
    }
    .kpi-delta.up      { color: var(--accent);        background: var(--accent-dim); }
    .kpi-delta.down    { color: var(--danger);         background: var(--danger-dim); }
    .kpi-delta.neutral { color: var(--text-tertiary);  background: var(--bg-overlay); }
    .kpi-delta::before {
        content: ""; width: 0; height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
    }
    .kpi-delta.up::before      { border-bottom: 5px solid var(--accent); }
    .kpi-delta.down::before    { border-top:    5px solid var(--danger); }
    .kpi-delta.neutral::before { display: none; }

    .kpi-bar {
        width: 100%; height: 3px; border-radius: 2px;
        background: rgba(255,255,255,0.06);
        overflow: hidden; position: relative;
        margin-top: 8px;
    }
    .kpi-bar-fill {
        position: absolute; top: 0; bottom: 0; left: 0;
        border-radius: 2px;
        animation: barGrow 1.2s cubic-bezier(0.4,0,0.2,1);
    }
    .kpi.accent  .kpi-bar-fill { background: linear-gradient(90deg, rgba(0,255,136,0.2), var(--accent)); box-shadow: 0 0 8px var(--accent-glow); }
    .kpi.info    .kpi-bar-fill { background: linear-gradient(90deg, rgba(91,157,255,0.2), var(--info)); }
    .kpi.purple  .kpi-bar-fill { background: linear-gradient(90deg, rgba(183,148,244,0.2), var(--purple)); }
    .kpi.warning .kpi-bar-fill { background: linear-gradient(90deg, rgba(255,149,0,0.2), var(--warning)); }
    @keyframes barGrow { from { width: 0%; } }

    .kpi-meta {
        font-family: var(--font-mono); font-size: 0.66rem;
        color: var(--text-muted); letter-spacing: 0.05em;
        margin-top: 10px;
        display: flex; justify-content: space-between;
    }

    /* ━━ DETAIL PANEL ━━ */
    .detail {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--accent);
        border-radius: 12px;
        padding: 20px 24px;
        margin: 0 0 24px 0;
        animation: slideIn 0.25s cubic-bezier(0.4,0,0.2,1);
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-8px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .detail.info    { border-left-color: var(--info);    background: linear-gradient(90deg, rgba(91,157,255,0.03), var(--bg-card)); }
    .detail.purple  { border-left-color: var(--purple);  background: linear-gradient(90deg, rgba(183,148,244,0.03), var(--bg-card)); }
    .detail.warning { border-left-color: var(--warning); background: linear-gradient(90deg, rgba(255,149,0,0.03), var(--bg-card)); }
    .detail.accent  { background: linear-gradient(90deg, rgba(0,255,136,0.03), var(--bg-card)); }
    .detail-eyebrow {
        font-family: var(--font-mono); font-size: 0.67rem;
        color: var(--text-tertiary); letter-spacing: 0.18em;
        text-transform: uppercase; margin-bottom: 8px;
    }
    .detail h4 {
        font-family: var(--font-display); font-size: 1.18rem;
        font-weight: 600; color: var(--text-primary);
        margin: 0 0 10px 0; letter-spacing: -0.01em;
    }
    .detail p {
        color: var(--text-secondary); font-size: 0.9rem;
        line-height: 1.7; margin: 0;
    }

    /* ━━ NAV TABS / BUTTONS ━━ */
    .stButton > button {
        width: 100% !important;
        height: 42px !important;
        border-radius: 8px !important;
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        transition: all 0.2s ease !important;
        background: var(--bg-deep) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        outline: none !important;
    }
    .stButton > button:hover {
        border-color: var(--border-strong) !important;
        color: var(--text-primary) !important;
        background: var(--bg-elevated) !important;
    }
    .stButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(0,255,136,0.25) !important;
    }
    .stButton > button:active { transform: scale(0.97) !important; }
    .stButton > button[kind="primary"] {
        background: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent), 0 0 20px -6px var(--accent-glow) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 0 1px var(--accent), 0 0 28px -2px var(--accent-glow) !important;
    }

    /* ━━ PANEL CARDS ━━ */
    .panel {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: border-color 0.2s ease;
    }
    .panel:hover { border-color: var(--border-strong); }
    .panel-head {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; padding-bottom: 16px;
        border-bottom: 1px solid var(--border-subtle);
    }
    .panel-title {
        font-family: var(--font-display); font-size: 1.18rem;
        font-weight: 600; color: var(--text-primary);
        letter-spacing: -0.01em; margin: 0;
        display: flex; align-items: center; gap: 10px;
    }
    .panel-title-tag {
        font-family: var(--font-mono); font-size: 0.66rem;
        color: var(--accent); letter-spacing: 0.14em;
        text-transform: uppercase;
        padding: 3px 9px;
        background: var(--accent-dim);
        border: 1px solid rgba(0,255,136,0.2);
        border-radius: 4px;
    }
    .panel-meta {
        font-family: var(--font-mono); font-size: 0.73rem;
        color: var(--text-tertiary); letter-spacing: 0.05em;
    }

    /* ━━ INSIGHTS ━━ */
    .insights-head {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 16px; padding-top: 4px;
    }
    .insights-title {
        font-family: var(--font-display); font-size: 1.08rem;
        font-weight: 600; color: var(--text-primary);
    }
    .insights-pulse {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 0 0 var(--accent-glow);
        animation: ping 2s ease-out infinite;
    }
    @keyframes ping {
        0%   { box-shadow: 0 0 0 0 rgba(0,255,136,0.5); }
        70%  { box-shadow: 0 0 0 6px rgba(0,255,136,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,255,136,0); }
    }

    .insight {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid transparent;
        border-radius: 10px;
        padding: 13px 14px;
        margin-bottom: 9px;
        position: relative;
        transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
    }
    .insight:hover {
        border-color: var(--border-strong);
        transform: translateX(3px);
        background: var(--bg-elevated);
    }
    .insight.up      { border-left-color: var(--accent); }
    .insight.down    { border-left-color: var(--danger); }
    .insight.info    { border-left-color: var(--info); }
    .insight.warning { border-left-color: var(--warning); }
    .insight.purple  { border-left-color: var(--purple); }

    .insight:nth-child(1) { animation: fadeUp 0.3s ease both; }
    .insight:nth-child(2) { animation: fadeUp 0.3s 0.06s ease both; }
    .insight:nth-child(3) { animation: fadeUp 0.3s 0.12s ease both; }
    .insight:nth-child(4) { animation: fadeUp 0.3s 0.18s ease both; }
    .insight:nth-child(5) { animation: fadeUp 0.3s 0.24s ease both; }
    .insight:nth-child(6) { animation: fadeUp 0.3s 0.30s ease both; }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .insight-head {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px;
    }
    .insight-label {
        font-family: var(--font-mono); font-size: 0.72rem;
        color: var(--text-secondary); letter-spacing: 0.1em;
        text-transform: uppercase; font-weight: 600;
        display: flex; align-items: center; gap: 8px;
    }
    .insight-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted); flex-shrink: 0; }
    .insight.up      .insight-dot { background: var(--accent);  box-shadow: 0 0 5px var(--accent-glow); }
    .insight.down    .insight-dot { background: var(--danger);  box-shadow: 0 0 5px rgba(255,59,59,0.5); }
    .insight.info    .insight-dot { background: var(--info);    box-shadow: 0 0 5px rgba(91,157,255,0.4); }
    .insight.warning .insight-dot { background: var(--warning); box-shadow: 0 0 5px rgba(255,149,0,0.4); }
    .insight.purple  .insight-dot { background: var(--purple);  box-shadow: 0 0 5px rgba(183,148,244,0.4); }

    .insight-meta {
        font-family: var(--font-mono); font-size: 0.67rem;
        color: var(--text-muted); letter-spacing: 0.05em;
    }
    .insight-body {
        color: var(--text-secondary); font-size: 0.86rem;
        line-height: 1.6; margin: 0;
    }
    .insight-body b { color: var(--text-primary); font-weight: 600; }

    /* ━━ PREDICTION CARD ━━ */
    .prediction {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 22px;
        margin-top: 14px;
        position: relative; overflow: hidden;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .prediction:hover {
        border-color: rgba(183,148,244,0.3);
        box-shadow: 0 0 40px -16px rgba(183,148,244,0.3);
    }
    .prediction::before {
        content: ""; position: absolute; inset: 0;
        background:
            radial-gradient(circle at 80% 10%, rgba(183,148,244,0.10), transparent 55%),
            radial-gradient(circle at 10% 90%, rgba(0,255,136,0.04), transparent 40%);
        pointer-events: none;
    }
    .prediction::after {
        content: ""; position: absolute; top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--purple) 50%, transparent);
    }
    .prediction-content { position: relative; z-index: 1; }
    .prediction-eyebrow {
        font-family: var(--font-mono); font-size: 0.67rem;
        color: var(--purple); letter-spacing: 0.18em;
        text-transform: uppercase; margin-bottom: 12px;
        display: flex; align-items: center; gap: 8px;
    }
    .prediction-row {
        display: flex; justify-content: space-between; align-items: flex-end;
    }
    .prediction-value {
        font-family: var(--font-mono); font-size: 2rem; font-weight: 700;
        color: var(--text-primary); line-height: 1;
        letter-spacing: -0.02em;
        font-feature-settings: "tnum";
    }
    .prediction-vs {
        font-family: var(--font-mono); font-size: 0.73rem;
        color: var(--text-tertiary); margin-top: 7px;
    }
    .prediction-vs strong { color: var(--accent); }
    .prediction-conf {
        font-family: var(--font-mono); font-size: 1.45rem;
        color: var(--purple); font-weight: 700;
        text-align: right; line-height: 1;
    }
    .prediction-conf-label {
        font-family: var(--font-mono); font-size: 0.64rem;
        color: var(--text-tertiary); letter-spacing: 0.12em;
        text-transform: uppercase; margin-top: 5px; text-align: right;
    }

    /* ━━ CUSTOM TABLE ━━ */
    .ctable { width: 100%; border-collapse: collapse; }
    .ctable thead th {
        font-family: var(--font-mono); font-size: 0.68rem;
        font-weight: 600; color: var(--text-muted);
        letter-spacing: 0.14em; text-transform: uppercase;
        padding: 10px 14px; text-align: left;
        border-bottom: 1px solid var(--border-subtle);
        position: sticky; top: 0;
        background: var(--bg-card);
    }
    .ctable tbody td {
        font-family: var(--font-mono); font-size: 0.82rem;
        color: var(--text-primary); padding: 12px 14px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .ctable tbody tr { transition: background 0.12s ease; }
    .ctable tbody tr:hover { background: rgba(255,255,255,0.03); }
    .ctable tbody tr:last-child td { border-bottom: none; }
    .ctable td.muted { color: var(--text-tertiary); }
    .ctable td.num { font-feature-settings: "tnum"; }
    .ctable td .pill {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 3px 10px; border-radius: 6px;
        font-size: 0.73rem; font-weight: 600; font-family: var(--font-mono);
    }
    .ctable td .pill.up   { background: var(--accent-dim);               color: var(--accent); }
    .ctable td .pill.down { background: var(--danger-dim);               color: var(--danger); }
    .ctable td .pill.flat { background: rgba(255,255,255,0.05);          color: var(--text-tertiary); }
    .ctable td .pill::before { content: ""; width: 5px; height: 5px; border-radius: 50%; }
    .ctable td .pill.up::before   { background: var(--accent); }
    .ctable td .pill.down::before { background: var(--danger); }
    .ctable td .pill.flat::before { background: var(--text-muted); }

    /* ━━ FOOTER ━━ */
    .footer {
        margin-top: 56px; padding: 28px 0 20px 0;
        border-top: 1px solid var(--border-subtle);
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 40px;
    }
    .footer-brand {
        font-family: var(--font-display); font-size: 1.08rem;
        font-weight: 600; color: var(--text-primary);
        letter-spacing: -0.01em; margin-bottom: 6px;
    }
    .footer-sub {
        font-family: var(--font-mono); font-size: 0.73rem;
        color: var(--text-tertiary); letter-spacing: 0.04em;
        line-height: 1.6;
    }
    .footer-col h5 {
        font-family: var(--font-mono); font-size: 0.68rem;
        color: var(--text-tertiary); letter-spacing: 0.14em;
        text-transform: uppercase; margin: 0 0 10px 0;
        font-weight: 500;
    }
    .footer-col p {
        font-size: 0.82rem; color: var(--text-secondary);
        margin: 0; line-height: 1.75;
    }
    .footer-col p b { color: var(--text-primary); font-weight: 500; }

    /* ━━ RESPONSIVO ━━ */
    @media (max-width: 768px) {
        .hero h1 { font-size: clamp(1.8rem, 6vw, 2.6rem) !important; }
        .footer { grid-template-columns: 1fr; gap: 20px; }
        .kpi-value { font-size: 1.5rem; }
        .status-bar { flex-direction: column; align-items: flex-start; gap: 10px; }
    }
    @media (max-width: 480px) {
        .hero h1 { font-size: 1.7rem !important; }
        .prediction-value { font-size: 1.6rem; }
        .kpi { padding: 16px; min-height: 170px; }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
#  HELPERS
# ============================================================================
def _parse_yf_v8_chart(payload: dict) -> Optional[pd.DataFrame]:
    """Parse Yahoo Finance v8 chart JSON → OHLCV DataFrame."""
    try:
        result = payload["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        n = len(timestamps)
        _f = lambda v: float(v) if v is not None else float("nan")
        df = pd.DataFrame({
            "Date": pd.to_datetime([pd.Timestamp(t, unit="s").date() for t in timestamps]),
            "Open":   [_f(v) for v in quote.get("open",   [None] * n)],
            "High":   [_f(v) for v in quote.get("high",   [None] * n)],
            "Low":    [_f(v) for v in quote.get("low",    [None] * n)],
            "Close":  [_f(v) for v in quote.get("close",  [None] * n)],
            "Volume": [float(v) if v is not None else 0.0 for v in quote.get("volume", [0] * n)],
        }).dropna(subset=["Close"])
        return df if not df.empty else None
    except Exception:
        return None


@st.cache_data(ttl=60)
def fetch_market_data(ticker: str, period: str, _ts: int = 0) -> Optional[pd.DataFrame]:
    """Fetch real OHLCV data. API proxy → yfinance+curl_cffi → yfinance direto."""
    # 1. API proxy — funciona no Render pois a API acessa o Yahoo Finance normalmente
    try:
        r = requests.get(
            f"{API_URL}/api/chart/{ticker}",
            params={"range": period, "interval": "1d"},
            timeout=15,
        )
        if r.status_code == 200:
            df = _parse_yf_v8_chart(r.json())
            if df is not None:
                return df
    except Exception:
        pass

    # 2. yfinance com curl_cffi (impersonação de browser)
    if HAS_CURL_CFFI:
        try:
            session = cffi_requests.Session(impersonate="chrome")
            df = yf.Ticker(ticker, session=session).history(period=period, auto_adjust=False)
            if not df.empty:
                return df.reset_index()
        except Exception:
            pass

    # 3. yfinance direto
    try:
        df = yf.Ticker(ticker).history(period=period, auto_adjust=False)
        if not df.empty:
            return df.reset_index()
    except Exception:
        pass

    return None


@st.cache_data(ttl=20)
def check_api_health() -> bool:
    try:
        return requests.get(f"{API_URL}/health", timeout=10).status_code == 200
    except Exception:  # noqa: BLE001
        return False


def fetch_prediction_from_api(symbol: str) -> Optional[dict]:
    try:
        r = requests.post(f"{API_URL}/predict/symbol",
                          json={"symbol": symbol, "days_ahead": 1}, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:  # noqa: BLE001
        pass
    return None


def fetch_model_info() -> Optional[dict]:
    try:
        r = requests.get(f"{API_URL}/model/info", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:  # noqa: BLE001
        pass
    return None


def market_is_open() -> tuple[bool, str]:
    now_et = datetime.now(tz=ET)
    is_weekday = now_et.weekday() < 5
    h, m = now_et.hour, now_et.minute
    after_open  = (h == 9 and m >= 30) or h >= 10
    before_close = h < 16
    if is_weekday and after_open and before_close:
        return True, "MARKET OPEN"
    return False, "MARKET CLOSED"





# ============================================================================
#  SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">◆</div>
            <div class="brand-text">
                <span class="brand-name">AI Quant</span>
                <span class="brand-tag">LSTM TERMINAL</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-label">Símbolo</div>', unsafe_allow_html=True)
    ticker = st.selectbox(
        "Ativo",
        ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-label">Janela Temporal</div>', unsafe_allow_html=True)
    period = st.selectbox(
        "Período",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        format_func=lambda x: {
            "1mo": "1 MÊS", "3mo": "3 MESES", "6mo": "6 MESES",
            "1y": "1 ANO", "2y": "2 ANOS", "5y": "5 ANOS",
        }[x],
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-label">Atualização</div>', unsafe_allow_html=True)
    refresh_rate = st.selectbox(
        "Refresh",
        ["Off", "5s", "10s", "30s"],
        index=1,
        format_func=lambda x: f"LIVE · {x}" if x != "Off" else "MANUAL",
        label_visibility="collapsed",
    )

    api_online = check_api_health()
    if api_online:
        status_class, status_text = "", "API ONLINE"
    else:
        status_class, status_text = "warn", "STANDALONE"
    st.markdown(
        f"""
        <div class="nav-label">Status do Sistema</div>
        <div style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; padding: 4px 0;">
            <span class="status-dot {status_class}"></span>
            <span>{status_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not api_online:
        st.caption("⚠️ API iniciando… aguarde.")

    st.markdown(
        """
        <div class="author">
            <div class="author-label">Construído por</div>
            <div class="author-name">Dione Braga Ferreira</div>
            <div class="author-subtitle">Tech Challenge Fase 4 · FIAP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
#  AUTO-REFRESH
# ============================================================================
if refresh_rate != "Off":
    interval_ms = int(refresh_rate.replace("s", "")) * 1000
    components.html(
        f"""
        <script>
        setTimeout(function(){{ window.location.reload(); }}, {interval_ms});
        </script>
        """,
        height=0,
    )

# ============================================================================
#  DADOS
# ============================================================================
_data_ts = int(datetime.now().timestamp() // 60)
df = fetch_market_data(ticker, period, _ts=_data_ts)
if df is None or df.empty:
    st.error(
        f"❌ Dados indisponíveis para **{ticker}**. "
        f"Verifique se a API está online em `{API_URL}` ou tente outro ativo."
    )
    st.stop()

last_close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else last_close
pct_change = (last_close - prev_close) / prev_close * 100

returns = df["Close"].pct_change().dropna()
volatility = float(returns.std() * np.sqrt(252) * 100)

recent_slope = np.polyfit(range(min(20, len(df))), df["Close"].tail(20).values, 1)[0]
if recent_slope > 0:
    trend, trend_class, trend_badge = "ALTA", "Bullish", "up"
elif recent_slope < 0:
    trend, trend_class, trend_badge = "BAIXA", "Bearish", "down"
else:
    trend, trend_class, trend_badge = "LATERAL", "Neutral", "neutral"

api_pred = fetch_prediction_from_api(ticker) if api_online else None
if api_pred and api_pred.get("predictions"):
    predicted_price = api_pred["predictions"][0]["predicted_price"]
else:
    predicted_price = None

_local_mape = None
try:
    with open("models/metadata.json", "r", encoding="utf-8") as _f:
        _local_mape = json.load(_f).get("metrics", {}).get("mape")
except Exception:
    pass

model_info = fetch_model_info() if api_online else None
if model_info and model_info.get("metrics"):
    mape = model_info["metrics"].get("mape")
    _conf_raw = round(100 - mape, 1) if mape else round(100 - _local_mape, 1) if _local_mape else None
elif _local_mape is not None:
    _conf_raw = round(100 - _local_mape, 1)
else:
    _conf_raw = None
# Confiança só é exibida quando há previsão real da API
confidence = _conf_raw if predicted_price is not None else None

pred_delta = (predicted_price - last_close) / last_close * 100 if predicted_price is not None else None

# ============================================================================
#  TECHNICAL INDICATORS
# ============================================================================
def calc_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0

def calc_macd(series: pd.Series) -> tuple[float, float, float]:
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    hist = macd - signal
    return float(macd.iloc[-1]), float(signal.iloc[-1]), float(hist.iloc[-1])

def calc_support_resistance(df: pd.DataFrame, window: int = 20) -> tuple[float, float]:
    recent = df.tail(window)
    resistance = float(recent["High"].max())
    support = float(recent["Low"].min())
    return support, resistance

rsi = calc_rsi(df["Close"])
macd_line, macd_signal, macd_hist = calc_macd(df["Close"])
support, resistance = calc_support_resistance(df)

bb_pos = ((last_close - float(df["Close"].rolling(20).mean().iloc[-1])) / (float(df["Close"].rolling(20).std().iloc[-1]) * 2))
vol_ratio = float(df["Volume"].tail(5).mean() / df["Volume"].rolling(20).mean().iloc[-1]) if len(df) > 20 else 1.0

# Generate dynamic insights for Trading tab
def trading_insights():
    insights = []

    # RSI
    if rsi > 70:
        rsi_text = f"RSI <b>{rsi:.1f}</b> — sobrecomprado. Possível reversão para baixo."
        rsi_variant = "warning"
    elif rsi < 30:
        rsi_text = f"RSI <b>{rsi:.1f}</b> — sobrevendido. Possível reversão para cima."
        rsi_variant = "up"
    else:
        rsi_text = f"RSI <b>{rsi:.1f}</b> — neutro. Sem extremos no momento."
        rsi_variant = "info"
    insights.append((rsi_variant, "RSI", "14 períodos", rsi_text))

    # MACD
    if macd_hist > 0 and macd_line > macd_signal:
        macd_text = f"MACD positivo e acima da linha de sinal — <b>momentum altista</b>."
        macd_variant = "up"
    elif macd_hist < 0 and macd_line < macd_signal:
        macd_text = f"MACD negativo e abaixo da linha de sinal — <b>momentum baixista</b>."
        macd_variant = "down"
    elif macd_hist > 0:
        macd_text = f"MACD se aproximando da linha de sinal — possível reversão."
        macd_variant = "warning"
    else:
        macd_text = f"MACD perdendo força — observar próxima vela."
        macd_variant = "info"
    insights.append((macd_variant, "MACD", "12/26/9", macd_text))

    # Bollinger / Volatilidade
    if bb_pos > 0.9:
        bb_text = f"Preço na borda superior das Bandas de Bollinger — <b>possível sobrecompra</b>."
        bb_variant = "warning"
    elif bb_pos < -0.9:
        bb_text = f"Preço na borda inferior das Bandas de Bollinger — <b>possível oversold</b>."
        bb_variant = "up"
    else:
        bb_text = f"Preço dentro das Bandas de Bollinger — volatilidade normal."
        bb_variant = "info"
    insights.append((bb_variant, "Bollinger", "2σ", bb_text))

    # Tendência + sugestão
    if trend_class == "Bullish" and rsi < 60 and macd_hist > 0:
        sig = "COMPRAR"
        sig_variant = "up"
        sig_body = f"Tendência <b>{trend_class}</b> com RSI favorável. <b>Sugestão: COMPRAR</b> nos dips próximo a <b>${support:.2f}</b>."
    elif trend_class == "Bearish" and rsi > 40:
        sig = "VENDER"
        sig_variant = "down"
        sig_body = f"Tendência <b>{trend_class}</b> com RSI cedendo. <b>Sugestão: VENDER</b> em rally até <b>${resistance:.2f}</b>."
    elif trend_class == "Bullish" and rsi > 65:
        sig = "AGUARDAR"
        sig_variant = "warning"
        sig_body = f"Tendência <b>{trend_class}</b> mas RSI sobrecomprado. <b>Sugestão: AGUARDAR</b> correção para recomprar."
    else:
        sig = "MANTER"
        sig_variant = "info"
        sig_body = f"Tendência <b>{trend_class}</b>. <b>Sugestão: MANTER</b> posição e observar suporte em <b>${support:.2f}</b>."
    insights.append((sig_variant, f"Sugestão: {sig}", "tempo real", sig_body))

    # Volume
    if vol_ratio > 1.5:
        vol_text = f"Volume <b>{vol_ratio:.1f}x</b> acima da média — forte participação."
        vol_variant = "up"
    elif vol_ratio < 0.5:
        vol_text = f"Volume <b>{vol_ratio:.1f}x</b> abaixo da média — baixa participação."
        vol_variant = "warning"
    else:
        vol_text = f"Volume dentro da média — atividade normal."
        vol_variant = "info"
    insights.append((vol_variant, "Volume", "5d vs 20d", vol_text))

    # Suporte/Resistência
    dist_support = (last_close - support) / support * 100
    dist_resistance = (resistance - last_close) / last_close * 100
    sr_text = f"Suporte <b>${support:.2f}</b> ({dist_support:+.1f}%) · Resistência <b>${resistance:.2f}</b> ({dist_resistance:+.1f}%)"
    insights.append(("info", "Suporte / Resistência", f"{ticker}", sr_text))

    return insights


# ============================================================================
#  TICKER TAPE — preços reais via yfinance
# ============================================================================
_TAPE_TICKERS = [
    ("AAPL", "AAPL"), ("MSFT", "MSFT"), ("GOOGL", "GOOGL"),
    ("AMZN", "AMZN"), ("TSLA", "TSLA"), ("META", "META"),
    ("NVDA", "NVDA"), ("BTC", "BTC-USD"), ("ETH", "ETH-USD"),
    ("S&P500", "^GSPC"), ("USD/BRL", "USDBRL=X"), ("OURO", "GC=F"),
]

@st.cache_data(ttl=120, show_spinner=False)
def _fetch_tape_prices() -> list:
    results = []
    for label, sym in _TAPE_TICKERS:
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d", auto_adjust=False)
            if len(hist) >= 2:
                c0 = float(hist["Close"].iloc[-2])
                c1 = float(hist["Close"].iloc[-1])
                pct = (c1 - c0) / c0 * 100
                results.append((label, c1, pct))
            elif len(hist) == 1:
                c1 = float(hist["Close"].iloc[-1])
                results.append((label, c1, 0.0))
        except Exception:
            pass
    return results

_tape_prices = _fetch_tape_prices()
ticker_items = []
for sym, px, dlt in (_tape_prices * 2 if _tape_prices else []):
    cls = "ticker-dlt-up" if dlt >= 0 else "ticker-dlt-dn"
    sign = "+" if dlt >= 0 else ""
    ticker_items.append(
        f'<div class="ticker-item">'
        f'<span class="ticker-sym">{sym}</span>'
        f'<span class="ticker-px">{px:,.2f}</span>'
        f'<span class="{cls}">{sign}{dlt:.2f}%</span>'
        f'<span class="ticker-dot"></span>'
        f'</div>'
    )
ticker_html = "".join(ticker_items)

st.markdown(
    f'<div class="ticker-bar"><div class="ticker-track">{ticker_html}</div></div>',
    unsafe_allow_html=True,
)


# ============================================================================
#  STATUS BAR
# ============================================================================
now = datetime.now(tz=BRT)
is_open, market_label = market_is_open()
market_dot_class = "" if is_open else "off"

st.markdown(
    f"""
    <div class="status-bar">
        <div class="status-group">
            <span class="status-item">
                <span class="status-dot {market_dot_class}"></span>
                <strong>{market_label}</strong>
            </span>
            <span class="status-item">SESSÃO · <strong>NYSE</strong></span>
            <span class="status-item">DATA · <strong>{now.strftime('%a, %d %b %Y').upper()}</strong></span>
        </div>
        <div class="status-group">
            <span class="status-item">TIME · <strong>{now.strftime('%H:%M:%S')}</strong></span>
            <span class="status-item">VOL · <strong>{int(df['Volume'].iloc[-1]/1_000_000)}M</strong></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
#  HERO
# ============================================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">
            <span class="blink">●</span> &nbsp; LIVE TERMINAL · TICKER {ticker}
        </div>
        <h1>Mercado em <em>tempo</em><br>real, decisões com IA.</h1>
        <div class="hero-sub">
            <span class="hero-sub-item">Análise técnica de <strong>{ticker}</strong></span>
            <span class="hero-sub-divider"></span>
            <span class="hero-sub-item">Modelo <strong>LSTM 64+64</strong></span>
            <span class="hero-sub-divider"></span>
            <span class="hero-sub-item">Por <strong>Dione Braga Ferreira</strong></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
#  KPI CARDS — UM POR COLUNA, RENDERIZADO INDIVIDUALMENTE
# ============================================================================
KPI_DETAILS = {
    "Preço": {
        "tag": "Asset Price",
        "title": "Análise do Preço Atual",
        "text": f"O ativo <b>{ticker}</b> opera em <b>${last_close:,.2f}</b>, com variação de <b>{pct_change:+.2f}%</b> em relação ao último fechamento. Volume atual de <b>{int(df['Volume'].iloc[-1]/1_000_000)}M</b> contratos.",
        "class": "accent",
    },
    "Volatilidade": {
        "tag": "Risk Metric",
        "title": "Volatilidade Anualizada",
        "text": f"Volatilidade de <b>{volatility:.2f}%</b> (desvio padrão dos retornos × √252). Valores acima de 30% indicam risco elevado. O ativo está {'<b>dentro</b>' if volatility < 30 else '<b>acima</b>'} dos níveis usuais.",
        "class": "info",
    },
    "Tendência": {
        "tag": "Technical",
        "title": "Análise de Tendência",
        "text": f"Tendência <b>{trend}</b> ({trend_class}) detectada pela inclinação dos últimos 20 dias. Confirmação adicional pelo cruzamento de MAs e indicador MACD.",
        "class": "purple",
    },
    "IA": {
        "tag": "Model Output",
        "title": "Confiança do Modelo LSTM",
        "text": (
            f"Modelo opera com <b>{confidence}%</b> de confiança (MAPE {100-confidence:.1f}%). "
            f"Próxima previsão: <b>${predicted_price:.2f}</b> (D+1, {pred_delta:+.2f}%). Arquitetura LSTM 64+64 com window=60."
        ) if (confidence is not None and predicted_price is not None and pred_delta is not None) else
            "Modelo LSTM disponível. Conecte à API para obter previsão e métricas em tempo real.",
        "class": "warning",
    },
}

# Calcular % de "fill" da barra de progresso baseado nos dados
def safe_fill_pct(value: float, min_v: float, max_v: float) -> int:
    if max_v <= min_v:
        return 50
    return int(max(5, min(100, (value - min_v) / (max_v - min_v) * 100)))

kpis_data = [
    ("Preço", "Preço Atual", f"${last_close:,.2f}",
     ("up" if pct_change >= 0 else "down"),
     f"{'+' if pct_change >= 0 else ''}{pct_change:.2f}%",
     "accent", "$",
     safe_fill_pct(last_close, df["Close"].min(), df["Close"].max()),
     "RANGE 52W"),
    ("Volatilidade", "Volatilidade", f"{volatility:.2f}%",
     "up" if volatility < 30 else "down",
     f"{'↓' if volatility >= 30 else '✓'}{abs(volatility - 25):.1f}pp",
     "info", "σ",
     min(100, int(volatility * 2)),
     "ANUALIZADA · σ√252"),
    ("Tendência", "Tendência (20d)", trend,
     trend_badge,
     trend_class,
     "purple", "Δ",
     75 if recent_slope > 0 else 25,
     "FORÇA · MA20/50"),
    ("IA", "Confiança IA",
     f"{confidence}%" if confidence is not None else "—",
     "up" if confidence is not None else "neutral",
     f"MAPE {100 - confidence:.1f}%" if confidence is not None else "API offline",
     "warning", "λ",
     confidence if confidence is not None else 0,
     "ACURÁCIA · LSTM"),
]

# ---------- Renderiza 4 cards em 4 colunas ----------
kpi_cols = st.columns(4, gap="small")
for col, (key, label, value, delta_class, delta_text, css_class, icon, fill_pct, meta) in zip(kpi_cols, kpis_data):
    with col:
        active = "active" if st.session_state.active_kpi == key else ""
        # Renderiza CADA card individualmente — SEM SVG inline, só barra
        card_html = (
            f'<div class="kpi {css_class} {active}">'
            f'<div class="kpi-head">'
            f'<span class="kpi-label">{label}</span>'
            f'<span class="kpi-icon">{icon}</span>'
            f'</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-delta {delta_class}">{delta_text}</div>'
            f'<div class="kpi-bar"><div class="kpi-bar-fill" style="width: {fill_pct}%"></div></div>'
            f'<div class="kpi-meta"><span>{meta}</span><span>{fill_pct}%</span></div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

# ---------- Botões de ação abaixo dos cards ----------
btn_cols = st.columns(4, gap="small")
for col, (key, *_) in zip(btn_cols, kpis_data):
    with col:
        is_active = st.session_state.active_kpi == key
        label = f"◆ FECHAR {key.upper()}" if is_active else f"◇ DETALHES {key.upper()}"
        if st.button(label, key=f"kpi_btn_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.active_kpi = None if is_active else key
            st.rerun()

# ---------- DETAIL PANEL ----------
if st.session_state.active_kpi:
    d = KPI_DETAILS[st.session_state.active_kpi]
    st.markdown(
        f"""
        <div class="detail {d['class']}">
            <div class="detail-eyebrow">{d['tag']}</div>
            <h4>{d['title']}</h4>
            <p>{d['text']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
#  TWO-COLUMN LAYOUT
# ============================================================================
main_col, insights_col = st.columns([2.8, 1], gap="large")

with main_col:
    # ---------- NAV TABS ----------
    tabs = ["Watchlist", "Trading", "Forecast", "Monte Carlo", "Heatmap", "Risk"]
    tab_cols = st.columns(len(tabs))
    for tcol, tname in zip(tab_cols, tabs):
        with tcol:
            is_active = st.session_state.active_tab == tname
            label = f"◆ {tname.upper()}" if is_active else tname.upper()
            if st.button(
                label,
                key=f"tab_{tname}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_tab = tname
                st.rerun()

    active = st.session_state.active_tab

    # ===== WATCHLIST =====
    if active == "Watchlist":
        watchlist_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        st.markdown(f"""
        <div class="panel">
            <div class="panel-head">
                <div class="panel-title">
                    Watchlist
                    <span class="panel-title-tag">TEMPO REAL</span>
                </div>
                <div class="panel-meta">{len(watchlist_tickers)} ATIVOS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        wcol1, wcol2, wcol3, wcol4 = st.columns([1, 1, 1, 1])
        with wcol1:
            filtro_rec = st.selectbox("Recomendação", ["Todas", "COMPRAR", "MANTER", "VENDER", "AGUARDAR"], label_visibility="collapsed")
        with wcol2:
            filtro_trend = st.selectbox("Tendência", ["Todas", "ALTA", "BAIXA", "LATERAL"], label_visibility="collapsed")
        with wcol3:
            filtro_rsi = st.selectbox("RSI", ["Todas", "Sobrevendido (<30)", "Neutro", "Sobrecomprado (>70)"], label_visibility="collapsed")
        with wcol4:
            st.markdown(f'<div style="font-family:var(--font-mono);font-size:0.72rem;color:var(--text-tertiary);padding:8px 0;text-align:right;">⏱ {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

        wl_data = []
        with st.spinner("Analisando ativos..."):
            for sym in watchlist_tickers:
                try:
                    wdf = fetch_market_data(sym, "3mo", _ts=_data_ts)
                    if wdf is None or wdf.empty:
                        continue
                    wclose = float(wdf["Close"].iloc[-1])
                    wprev = float(wdf["Close"].iloc[-2])
                    wpct = (wclose - wprev) / wprev * 100
                    wreturns = wdf["Close"].pct_change().dropna()
                    wslope = np.polyfit(range(min(20, len(wdf))), wdf["Close"].tail(20).values, 1)[0]
                    wtrend = "ALTA" if wslope > 0 else ("BAIXA" if wslope < 0 else "LATERAL")
                    wrsi = calc_rsi(wdf["Close"])
                    wmacd_line, wmacd_signal, wmacd_hist = calc_macd(wdf["Close"])
                    if wrsi < 35 and wmacd_hist > 0:
                        wrec, wrec_cls, wrec_icon = "COMPRAR", "up", "▲"
                    elif wrsi > 65 or (wtrend == "BAIXA" and wmacd_hist < 0):
                        wrec, wrec_cls, wrec_icon = "VENDER", "down", "▼"
                    elif 35 <= wrsi <= 65 and wtrend == "ALTA":
                        wrec, wrec_cls, wrec_icon = "MANTER", "info", "◆"
                    else:
                        wrec, wrec_cls, wrec_icon = "AGUARDAR", "warning", "◇"

                    if filtro_rec != "Todas" and wrec != filtro_rec:
                        continue
                    if filtro_trend != "Todas" and wtrend != filtro_trend:
                        continue
                    if filtro_rsi == "Sobrevendido (<30)" and not wrsi < 30:
                        continue
                    if filtro_rsi == "Sobrecomprado (>70)" and not wrsi > 70:
                        continue
                    if filtro_rsi == "Neutro" and not (30 <= wrsi <= 70):
                        continue

                    wl_data.append((sym, wclose, wpct, wtrend, wrsi, wrec, wrec_cls, wrec_icon))
                except Exception:
                    continue

        if wl_data:
            wl_rows = "".join(
                f'<tr>'
                f'<td><span class="pill" style="background:var(--bg-elevated);color:var(--text-primary);font-weight:600;">{sym}</span></td>'
                f'<td class="num">${price:.2f}</td>'
                f'<td class="num" style="color:{"var(--accent)" if pct >= 0 else "var(--danger)"}">{pct:+.2f}%</td>'
                f'<td style="color:{"var(--accent)" if trend == "ALTA" else ("var(--danger)" if trend == "BAIXA" else "var(--text-tertiary)")};">{trend}</td>'
                f'<td class="num" style="color:{"var(--accent)" if rsi > 50 else "var(--danger)"};">{rsi:.1f}</td>'
                f'<td><span class="pill {cls}" style="font-weight:600;">{icon} {rec}</span></td>'
                f'</tr>'
                for sym, price, pct, trend, rsi, rec, cls, icon in wl_data
            )
            st.markdown(f"""
            <table class="ctable">
                <thead>
                    <tr>
                        <th>Símbolo</th><th>Preço</th><th>Var</th>
                        <th>Tendência</th><th>RSI</th><th>IA Recomendação</th>
                    </tr>
                </thead>
                <tbody>{wl_rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:var(--text-tertiary);text-align:center;padding:40px;font-family:var(--font-mono);">Nenhum ativo encontrado com esses filtros.</p>', unsafe_allow_html=True)

    # ===== TRADING =====
    elif active == "Trading":
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">
                        Análise Técnica
                        <span class="panel-title-tag">CANDLES · MA · BB</span>
                    </div>
                    <div class="panel-meta">{ticker} · {period.upper()}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        df_plot = df.copy()
        df_plot["MA20"] = df_plot["Close"].rolling(20).mean()
        df_plot["MA50"] = df_plot["Close"].rolling(50).mean()
        std20 = df_plot["Close"].rolling(20).std()
        df_plot["BBUpper"] = df_plot["MA20"] + 2 * std20
        df_plot["BBLower"] = df_plot["MA20"] - 2 * std20

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_plot["Date"], open=df_plot["Open"], high=df_plot["High"],
            low=df_plot["Low"], close=df_plot["Close"], name="Candles",
            increasing_line_color="#00FF88", decreasing_line_color="#FF3B3B",
            increasing_fillcolor="rgba(0,255,136,0.6)", decreasing_fillcolor="rgba(255,59,59,0.6)",
        ))
        fig.add_trace(go.Scatter(x=df_plot["Date"], y=df_plot["MA20"],
                                 name="MA20", line=dict(color="#5B9DFF", width=1.2)))
        fig.add_trace(go.Scatter(x=df_plot["Date"], y=df_plot["MA50"],
                                 name="MA50", line=dict(color="#B794F4", width=1.2)))
        fig.add_trace(go.Scatter(x=df_plot["Date"], y=df_plot["BBUpper"],
                                 name="Upper BB", line=dict(color="rgba(255,255,255,0.2)", width=0.8, dash="dot")))
        fig.add_trace(go.Scatter(x=df_plot["Date"], y=df_plot["BBLower"],
                                 name="Lower BB", line=dict(color="rgba(255,255,255,0.2)", width=0.8, dash="dot"),
                                 fill="tonexty", fillcolor="rgba(255,255,255,0.02)"))

        # ---------- SINAIS DE COMPRA / VENDA ----------
        df_plot["Cross"] = np.where(df_plot["MA20"] > df_plot["MA50"], 1, 0)
        df_plot["CrossSig"] = df_plot["Cross"].diff()
        buy_pts = df_plot[(df_plot["CrossSig"] == 1) & df_plot["MA20"].notna()]
        sell_pts = df_plot[(df_plot["CrossSig"] == -1) & df_plot["MA20"].notna()]

        if not buy_pts.empty:
            fig.add_trace(go.Scatter(
                x=buy_pts["Date"], y=buy_pts["Low"] * 0.998,
                mode="markers",
                marker=dict(symbol="triangle-up", size=13, color="#00FF88",
                            line=dict(width=1, color="#00FF88")),
                name="COMPRAR"
            ))
        if not sell_pts.empty:
            fig.add_trace(go.Scatter(
                x=sell_pts["Date"], y=sell_pts["High"] * 1.002,
                mode="markers",
                marker=dict(symbol="triangle-down", size=13, color="#FF3B3B",
                            line=dict(width=1, color="#FF3B3B")),
                name="VENDER"
            ))

        # ---------- FIBONACCI RETRACEMENT ----------
        lookback = min(60, len(df_plot))
        fib_df = df_plot.iloc[-lookback:]
        swing_high = fib_df["High"].max()
        swing_low = fib_df["Low"].min()
        diff = swing_high - swing_low
        fib_levels = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
        fib_pct = ["0%", "23.6%", "38.2%", "50%", "61.8%", "78.6%", "100%"]

        for lvl, pct in zip(fib_levels, fib_pct):
            price = swing_high - lvl * diff
            fig.add_trace(go.Scatter(
                x=[fib_df["Date"].iloc[0], fib_df["Date"].iloc[-1]],
                y=[price, price],
                mode="lines",
                line=dict(color="rgba(183,148,244,0.25)", width=0.7, dash="dash"),
                showlegend=False,
                hoverinfo="skip",
            ))
            fig.add_annotation(
                x=fib_df["Date"].iloc[-1], y=price,
                text=f"<b>{pct}</b>",
                showarrow=False,
                font=dict(size=9, color="rgba(183,148,244,0.6)", family="JetBrains Mono"),
                xanchor="left", xshift=4,
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#A1A1AA", size=11),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", rangeslider=dict(visible=False),
                       showline=False, zeroline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
            margin=dict(t=10, b=10, l=10, r=10), height=440,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        bgcolor="rgba(0,0,0,0)", font=dict(color="#71717A", size=10)),
            hoverlabel=dict(bgcolor="#11111A", bordercolor="#27272A",
                            font=dict(family="JetBrains Mono", color="#FAFAFA")),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("</div>", unsafe_allow_html=True)

    # ===== FORECAST =====
    elif active == "Forecast":
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">
                        Previsão LSTM
                        <span class="panel-title-tag">7 DIAS · CI 95%</span>
                    </div>
                    <div class="panel-meta">{ticker} · MODELO 64+64</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        forecast_dates = pd.bdate_range(start=df["Date"].iloc[-1] + timedelta(days=1), periods=7)
        daily_closes = df["Close"].tolist()
        forecast_vals = None
        try:
            if api_online:
                r = requests.post(f"{API_URL}/predict",
                                  json={"close_prices": daily_closes, "days_ahead": 7},
                                  timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    forecast_vals = [p["predicted_price"] for p in data["predictions"]]
        except Exception:
            forecast_vals = None

        if forecast_vals is None:
            st.warning(
                "Previsão LSTM indisponível — API offline ou sem resposta. "
                "Verifique o status da API na barra lateral.",
                icon="⚠️",
            )
        else:
            spread = np.std(forecast_vals) * 0.5
            upper = [v + spread * (1 + i * 0.3) for i, v in enumerate(forecast_vals)]
            lower = [v - spread * (1 + i * 0.3) for i, v in enumerate(forecast_vals)]

            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=df["Date"].tail(60), y=df["Close"].tail(60),
                                        name="Histórico", line=dict(color="#FAFAFA", width=1.8)))
            fig_fc.add_trace(go.Scatter(x=forecast_dates, y=forecast_vals,
                                        name="Previsão LSTM",
                                        line=dict(color="#B794F4", width=2.5, dash="dash"),
                                        mode="lines+markers",
                                        marker=dict(size=6, symbol="diamond", color="#B794F4")))
            fig_fc.add_trace(go.Scatter(
                x=list(forecast_dates) + list(forecast_dates[::-1]),
                y=list(upper) + list(lower[::-1]),
                fill="toself", fillcolor="rgba(183,148,244,0.12)",
                line=dict(color="rgba(0,0,0,0)"), name="Intervalo de Confiança",
            ))
            fig_fc.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono", color="#A1A1AA", size=11),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
                margin=dict(t=10, b=10, l=10, r=10), height=440,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            bgcolor="rgba(0,0,0,0)", font=dict(color="#71717A", size=10)),
                hoverlabel=dict(bgcolor="#11111A", bordercolor="#27272A"),
            )
            st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== MONTE CARLO =====
    elif active == "Monte Carlo":
        st.markdown(
            """
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">
                        Simulação Monte Carlo
                        <span class="panel-title-tag">100 PATHS · GBM</span>
                    </div>
                    <div class="panel-meta">HORIZONTE 30 DIAS</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        n_sims, horizon = 100, 30
        mu, sigma = returns.mean(), returns.std()
        sims = np.zeros((horizon, n_sims))
        sims[0] = last_close
        rng = np.random.default_rng()
        for t in range(1, horizon):
            sims[t] = sims[t-1] * np.exp((mu - sigma**2 / 2) + sigma * rng.standard_normal(n_sims))

        future_dates = pd.bdate_range(start=df["Date"].iloc[-1], periods=horizon)
        fig_mc = go.Figure()
        for i in range(n_sims):
            fig_mc.add_trace(go.Scatter(
                x=future_dates, y=sims[:, i], mode="lines",
                line=dict(width=0.4, color="rgba(91,157,255,0.15)"),
                showlegend=False, hoverinfo="skip",
            ))
        p05 = np.percentile(sims, 5, axis=1)
        p95 = np.percentile(sims, 95, axis=1)
        fig_mc.add_trace(go.Scatter(
            x=list(future_dates) + list(future_dates[::-1]),
            y=list(p95) + list(p05[::-1]),
            fill="toself", fillcolor="rgba(0,255,136,0.06)",
            line=dict(color="rgba(0,0,0,0)"), name="P5–P95",
        ))
        fig_mc.add_trace(go.Scatter(x=future_dates, y=sims.mean(axis=1),
                                    name="Mediana", line=dict(color="#00FF88", width=2.5)))
        fig_mc.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#A1A1AA", size=11),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
            margin=dict(t=10, b=10, l=10, r=10), height=440,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        bgcolor="rgba(0,0,0,0)", font=dict(color="#71717A", size=10)),
            hoverlabel=dict(bgcolor="#11111A", bordercolor="#27272A"),
        )
        st.plotly_chart(fig_mc, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== HEATMAP =====
    elif active == "Heatmap":
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">
                        Heatmap Sazonal
                        <span class="panel-title-tag">RETORNO MÉDIO</span>
                    </div>
                    <div class="panel-meta">% AO MÊS</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        df_hm = df.copy()
        df_hm["Date"] = pd.to_datetime(df_hm["Date"])
        df_hm["Year"] = df_hm["Date"].dt.year
        df_hm["Month"] = df_hm["Date"].dt.strftime("%b")
        df_hm["Return"] = df_hm["Close"].pct_change() * 100
        pivot = df_hm.groupby(["Year", "Month"])["Return"].mean().reset_index()
        pivot_table = pivot.pivot(index="Year", columns="Month", values="Return")
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        pivot_table = pivot_table.reindex(columns=[m for m in month_order if m in pivot_table.columns])

        fig_hm = go.Figure(go.Heatmap(
            z=pivot_table.values, x=pivot_table.columns, y=pivot_table.index,
            colorscale=[[0, "#FF3B3B"], [0.5, "#11111A"], [1, "#00FF88"]],
            zmid=0,
            colorbar=dict(title="%", thickness=10, len=0.8,
                          tickfont=dict(family="JetBrains Mono", color="#71717A", size=10)),
            text=pivot_table.values,
            texttemplate="%{text:.1f}",
            textfont=dict(family="JetBrains Mono", size=10),
        ))
        fig_hm.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#A1A1AA", size=11),
            margin=dict(t=10, b=10, l=10, r=10), height=440,
        )
        st.plotly_chart(fig_hm, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== RISK =====
    elif active == "Risk":
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">
                        Métricas de Risco
                        <span class="panel-title-tag">VaR · SHARPE · DRAWDOWN</span>
                    </div>
                    <div class="panel-meta">{ticker}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        var_95 = float(np.percentile(returns, 5) * 100)
        var_99 = float(np.percentile(returns, 1) * 100)
        sharpe = float((returns.mean() / returns.std()) * np.sqrt(252)) if returns.std() > 0 else 0
        max_dd = float(((df["Close"] / df["Close"].cummax()) - 1).min() * 100)

        risk_cols = st.columns(4, gap="small")
        risk_kpis = [
            ("VaR (95%)", f"{var_95:.2f}%", "warning", "α"),
            ("VaR (99%)", f"{var_99:.2f}%", "warning", "α"),
            ("Sharpe Ratio", f"{sharpe:.2f}", "accent" if sharpe > 1 else "warning", "S"),
            ("Max Drawdown", f"{max_dd:.2f}%", "warning", "↓"),
        ]
        for rcol, (lbl, val, cls, ic) in zip(risk_cols, risk_kpis):
            with rcol:
                st.markdown(
                    f'<div class="kpi {cls}" style="min-height: 130px;">'
                    f'<div class="kpi-head">'
                    f'<span class="kpi-label">{lbl}</span>'
                    f'<span class="kpi-icon">{ic}</span>'
                    f'</div>'
                    f'<div class="kpi-value" style="font-size: 1.4rem;">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Drawdown chart
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        drawdown_series = (df["Close"] / df["Close"].cummax() - 1) * 100
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=df["Date"], y=drawdown_series,
            fill="tozeroy", fillcolor="rgba(255,59,59,0.15)",
            line=dict(color="#FF3B3B", width=1.5), name="Drawdown",
        ))
        fig_dd.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#A1A1AA", size=11),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False,
                       ticksuffix="%"),
            margin=dict(t=10, b=10, l=10, r=10), height=240,
            showlegend=False,
        )
        st.plotly_chart(fig_dd, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- HISTORY TABLE ----------
    hist = df.tail(8).copy()
    hist["Date"] = pd.to_datetime(hist["Date"])
    hist["Var"] = (hist["Close"].pct_change() * 100)

    rows = []
    for _, row in hist.iloc[::-1].iterrows():
        var = row["Var"]
        if pd.isna(var):
            pill_html = '<span class="pill flat">FLAT</span>'
            var_txt = "—"
        elif var > 0:
            pill_html = '<span class="pill up">ALTA</span>'
            var_txt = f"+{var:.2f}%"
        else:
            pill_html = '<span class="pill down">BAIXA</span>'
            var_txt = f"{var:.2f}%"

        rows.append(
            f'<tr>'
            f'<td class="muted">{row["Date"].strftime("%d %b %Y").upper()}</td>'
            f'<td class="num">${row["Open"]:.2f}</td>'
            f'<td class="num">${row["Close"]:.2f}</td>'
            f'<td class="num muted">{int(row["Volume"]):,}</td>'
            f'<td class="num">{var_txt}</td>'
            f'<td>{pill_html}</td>'
            f'</tr>'
        )
    rows_html = "".join(rows)

    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-head">
                <div class="panel-title">
                    Histórico Recente
                    <span class="panel-title-tag">ÚLTIMAS 8 SESSÕES</span>
                </div>
                <div class="panel-meta">{ticker}</div>
            </div>
            <table class="ctable">
                <thead>
                    <tr>
                        <th>Data</th><th>Abertura</th><th>Fechamento</th>
                        <th>Volume</th><th>Var %</th><th>Status</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
#  INSIGHTS PANEL
# ============================================================================
with insights_col:
    st.markdown(
        """
        <div class="insights-head">
            <span class="insights-pulse"></span>
            <span class="insights-title">AI Insights</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    active = st.session_state.active_tab

    if active == "Trading":
        insights_list = trading_insights()
    elif active == "Forecast":
        _pred_txt = (
            f"Previsão de <b>${predicted_price:.2f}</b> ({pred_delta:+.2f}%) para próximo dia."
            if predicted_price is not None and pred_delta is not None
            else "Previsão indisponível — API offline."
        )
        _conf_txt = (
            f"Intervalo de confiança de <b>{confidence}%</b> nas últimas validações."
            if confidence is not None
            else "Métricas de confiança indisponíveis — API offline."
        )
        insights_list = [
            ("purple", "LSTM D+1", "agora", _pred_txt),
            ("info", "Horizonte", "—", "Janela de 60 dias alimentada. Arquitetura LSTM 64+64 com dropout 0.2."),
            ("up", "Acurácia", "validação", _conf_txt),
        ]
    elif active == "Monte Carlo":
        insights_list = [
            ("info", "Trajetórias", "100 sims", "Simulações geradas com movimento browniano geométrico."),
            ("purple", "Distribuição", "—", "Drift μ e volatilidade σ calibrados nos retornos históricos."),
            ("up", "Horizonte", "30 dias", "Projeção de 30 dias úteis à frente do último fechamento."),
        ]
    elif active == "Heatmap":
        insights_list = [
            ("warning", "Sazonalidade", "histórico", "Retornos médios por mês revelam padrões sazonais do ativo."),
            ("up", "Melhores Meses", "—", "Verde indica desempenho positivo médio na janela selecionada."),
            ("down", "Piores Meses", "—", "Vermelho destaca períodos historicamente negativos."),
        ]
    else:
        insights_list = [
            ("down", "Value at Risk", "agora", "VaR 95% e 99% calculados pelo método histórico (percentis)."),
            ("warning", "Max Drawdown", "—", "Maior queda do pico ao vale no histórico recente."),
            ("up", "Sharpe Ratio", "anualizado", "Mede retorno ajustado ao risco. Valores > 1 são bons."),
        ]

    for variant, label, meta, body in insights_list:
        st.markdown(
            f'<div class="insight {variant}">'
            f'<div class="insight-head">'
            f'<span class="insight-label"><span class="insight-dot"></span>{label}</span>'
            f'<span class="insight-meta">{meta}</span>'
            f'</div>'
            f'<p class="insight-body">{body}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ---------- PREDICTION CARD ----------
    _pred_value_html = f"${predicted_price:.2f}" if predicted_price is not None else "—"
    _pred_delta_html = f"vs último close · <strong>{pred_delta:+.2f}%</strong>" if pred_delta is not None else "API offline"
    _conf_html = f"{confidence}%" if confidence is not None else "—"
    st.markdown(
        f"""
        <div class="prediction">
            <div class="prediction-content">
                <div class="prediction-eyebrow">✦ LSTM PREDICTION · D+1</div>
                <div class="prediction-row">
                    <div>
                        <div class="prediction-value">{_pred_value_html}</div>
                        <div class="prediction-vs">
                            {_pred_delta_html}
                        </div>
                    </div>
                    <div>
                        <div class="prediction-conf">{_conf_html}</div>
                        <div class="prediction-conf-label">Confiança</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
#  FOOTER
# ============================================================================

now = datetime.now(tz=BRT)

footer_html = (
    '<div class="footer">'
    '<div class="footer-col">'
    '<div class="footer-brand">AI Quant Trading Terminal</div>'
    '<div class="footer-sub">Tech Challenge Fase 4 | PosTech MLET FIAP</div>'
    '</div>'
    '<div class="footer-col">'
    '<h5>Autor</h5>'
    '<p><b>Dione Braga Ferreira</b><br>Engenharia de Inteligencia Artificial</p>'
    '</div>'
    '<div class="footer-col">'
    '<h5>Status</h5>'
    f'<p>Atualizado - {now.strftime("%d/%m/%Y %H:%M")}</p>'
    '</div>'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)