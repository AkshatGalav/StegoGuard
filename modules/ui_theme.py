"""
UI Theme and CSS styling module for StegoGuard.
Provides CyberSentinel Glassmorphism visual theme, custom typography,
glowing cyber accents, micro-animations, and modern component card layouts.
"""
import streamlit as st


def inject_cyber_theme():
    """Injects high-end CyberSentinel glassmorphism styles and Google Fonts into Streamlit."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap');

    /* Global Body & Typography Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        color: #E2E8F0;
    }

    /* Main App Background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 85% 85%, rgba(127, 0, 255, 0.05) 0%, transparent 40%),
                    #090D16 !important;
        background-attachment: fixed !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(13, 18, 30, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.15) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
    }
    
    section[data-testid="stSidebar"] .stRadio label {
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 4px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        font-weight: 500;
        color: #94A3B8;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(0, 242, 254, 0.08);
        border-color: rgba(0, 242, 254, 0.2);
        color: #00F2FE;
        transform: translateX(4px);
    }

    section[data-testid="stSidebar"] .stRadio label[data-aria-checked="true"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(127, 0, 255, 0.15) 100%) !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.15);
        font-weight: 700;
    }

    /* Custom Glassmorphism Container Cards */
    .stCard, .cyber-card {
        background: rgba(17, 24, 39, 0.65) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .stCard:hover, .cyber-card:hover {
        border-color: rgba(0, 242, 254, 0.3) !important;
        box-shadow: 0 12px 35px rgba(0, 242, 254, 0.12);
    }

    /* Gradient Hero Headers */
    .hero-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 50%, #E100FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        color: #10B981;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        animation: pulse-dot 2s infinite;
    }

    @keyframes pulse-dot {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Buttons Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00F2FE 0%, #00C6FF 100%) !important;
        color: #090D16 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.45) !important;
        color: #000000 !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(127, 0, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(225, 0, 255, 0.5) !important;
    }

    /* Code Blocks & Inputs */
    code, stCodeBlock, [data-baseweb="input"], [data-baseweb="textarea"] {
        font-family: 'Fira Code', monospace !important;
    }

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
    }

    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #00F2FE !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
    }

    /* File Uploader Dropzone */
    [data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 2px dashed rgba(0, 242, 254, 0.3) !important;
        border-radius: 14px !important;
        padding: 16px !important;
        transition: border-color 0.3s ease !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #00F2FE !important;
        background: rgba(0, 242, 254, 0.05) !important;
    }

    /* Custom Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: rgba(15, 23, 42, 0.7) !important;
        padding: 6px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px !important;
        border-radius: 10px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0 16px !important;
        transition: all 0.25s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.2) 0%, rgba(127, 0, 255, 0.2) 100%) !important;
        color: #00F2FE !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Alerts and Notifications */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid transparent !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Dataframe Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_hero_header(title: str, subtitle: str, status_text: str = "SYSTEM ONLINE"):
    """Renders a polished CyberSentinel hero header banner."""
    html_code = f"""
    <div style="margin-bottom: 24px;">
        <div class="status-badge">
            <span class="status-dot"></span>
            <span>{status_text}</span>
        </div>
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
