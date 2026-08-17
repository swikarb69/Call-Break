"""
styles.py
Custom CSS injection for the Cozy Call Break Scorekeeper.
Provides a warm card-table aesthetic: forest green felt, dark mahogany wood,
cream cardstock, muted gold accents, and responsive touch-friendly cards.
"""

import streamlit as st

COZY_CSS = """
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Page Styles */
.stApp {
    background: radial-gradient(circle at center, #1b3d2c 0%, #0d2117 80%, #08140e 100%) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #f4ebd0 !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background-color: transparent !important;}

/* Title & Header Typography */
h1, h2, h3, .cozy-title {
    font-family: 'Cinzel', serif !important;
    color: #e5c158 !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    letter-spacing: 0.5px;
}

.cozy-subtitle {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #bfa882;
    font-size: 1.1rem;
    font-weight: 500;
    margin-top: -10px;
    margin-bottom: 25px;
}

/* Cozy Card Container */
.cozy-card {
    background: #142e22;
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(10px);
}

.cozy-card-light {
    background: #fcf9f2;
    color: #1a2e24 !important;
    border: 1px solid #d4af37;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}

.cozy-card-light h3, .cozy-card-light h4 {
    color: #1a2e24 !important;
    text-shadow: none !important;
}

/* Leader / Crown Highlight Card */
.leader-card {
    background: linear-gradient(135deg, #2b2210 0%, #1c170a 100%);
    border: 2px solid #e5c158;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 0 20px rgba(229, 193, 88, 0.25);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.leader-card::before {
    content: "♠ ♥ ♦ ♣";
    position: absolute;
    top: -10px;
    right: -10px;
    font-size: 4rem;
    opacity: 0.05;
    color: #e5c158;
}

/* Player Score Badges & Cards */
.player-score-card {
    background: #1a382a;
    border: 1px solid rgba(229, 193, 88, 0.3);
    border-radius: 14px;
    padding: 14px 18px;
    text-align: center;
    transition: transform 0.2s ease;
}

.player-score-card:hover {
    transform: translateY(-2px);
    border-color: #e5c158;
}

.player-score-card.is-leader {
    border: 2px solid #e5c158;
    background: linear-gradient(135deg, #223f30 0%, #2b301a 100%);
    box-shadow: 0 4px 15px rgba(229, 193, 88, 0.2);
}

.player-name {
    font-size: 1rem;
    font-weight: 700;
    color: #f4ebd0;
    margin-bottom: 4px;
    letter-spacing: 0.5px;
}

.player-points {
    font-size: 1.6rem;
    font-weight: 800;
    color: #e5c158;
}

/* Button Customizations */
.stButton > button {
    background: linear-gradient(135deg, #d4af37 0%, #b88e28 100%) !important;
    color: #0d2117 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s ease !important;
    width: 100%;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #e5c158 0%, #cfa330 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(229, 193, 88, 0.35) !important;
}

.stButton > button:active {
    transform: translateY(1px) !important;
}

/* Secondary Button style */
div[data-testid="stButton"] > button[kind="secondary"], div[data-testid="stButton"] > button[data-testid="baseButton-secondary"], button[data-testid="baseButton-secondary"] {
    background: rgba(244, 235, 208, 0.1) !important;
    color: #f4ebd0 !important;
    border: 1px solid rgba(244, 235, 208, 0.3) !important;
}

div[data-testid="stButton"] > button[kind="secondary"], div[data-testid="stButton"] > button[data-testid="baseButton-secondary"], button[data-testid="baseButton-secondary"]:hover {
    background: rgba(244, 235, 208, 0.2) !important;
    border-color: #e5c158 !important;
}

/* Touch +/- Counter Buttons */
.counter-btn button {
    padding: 4px 12px !important;
    font-size: 1.4rem !important;
    border-radius: 8px !important;
    height: 42px !important;
}

/* Input Fields */
.stTextInput > div > div > input, .stNumberInput > div > div > input {
    background-color: #11261c !important;
    color: #f4ebd0 !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
}

.stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
    border-color: #e5c158 !important;
    box-shadow: 0 0 8px rgba(229, 193, 88, 0.3) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #11261c !important;
    color: #f4ebd0 !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 10px !important;
}

/* Streamlit Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #11261c;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(212, 175, 55, 0.2);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px;
    color: #bfa882;
    font-weight: 600;
    border: none !important;
    padding: 0 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #1d4030 !important;
    color: #e5c158 !important;
    border: 1px solid rgba(229, 193, 88, 0.4) !important;
}

/* Table Styling */
.cozy-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 16px 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(212, 175, 55, 0.3);
}

.cozy-table th {
    background: #0d2117;
    color: #e5c158;
    font-family: 'Cinzel', serif;
    font-weight: 700;
    padding: 12px 16px;
    text-align: center;
    border-bottom: 2px solid rgba(212, 175, 55, 0.4);
}

.cozy-table td {
    background: #142e22;
    color: #f4ebd0;
    padding: 10px 16px;
    text-align: center;
    border-bottom: 1px solid rgba(244, 235, 208, 0.08);
}

.cozy-table tr:last-child td {
    background: #1d4030;
    font-weight: 800;
    color: #e5c158;
    border-top: 2px solid #e5c158;
    border-bottom: none;
    font-size: 1.05rem;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #142e22 !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 10px !important;
    color: #f4ebd0 !important;
    font-weight: 600;
}

/* Score Pill Badge */
.score-positive {
    color: #5cdb95;
    font-weight: 700;
}

.score-negative {
    color: #ff6b6b;
    font-weight: 700;
}

/* 5 Player Mode Banner */
.five-player-banner {
    background: linear-gradient(135deg, #3d2a10 0%, #261a0a 100%);
    border: 1px solid #e5c158;
    border-radius: 12px;
    padding: 12px 16px;
    color: #f4ebd0;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.five-player-banner strong {
    color: #e5c158;
}

/* Hero Section */
.hero-box {
    text-align: center;
    padding: 30px 15px;
    margin-bottom: 20px;
    background: radial-gradient(circle at center, rgba(229, 193, 88, 0.08) 0%, transparent 70%);
    border-radius: 20px;
}

.suit-symbols {
    font-size: 1.8rem;
    letter-spacing: 12px;
    color: #e5c158;
    margin-bottom: 10px;
}
</style>
"""


def inject_cozy_css():
    """
    Injects the custom CSS styles into the active Streamlit app.
    """
    st.markdown(COZY_CSS, unsafe_allow_html=True)
