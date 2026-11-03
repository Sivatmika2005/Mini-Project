"""Custom CSS injected across the app for a pastel mental-wellness aesthetic."""

BASE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --lavender: #a5a6f6;
        --lavender-light: #ecebff;
        --mint: #b7f0d4;
        --mint-light: #e9f9f0;
        --sky: #bcd9fb;
        --sky-light: #eef6ff;
        --ink: #1a1a2e;
        --muted: #5c5b78;
        --card-bg: #ffffff;
        --accent: #7c7ceb;
        --accent-deep: #6669e5;
        --line: rgba(124, 124, 235, 0.16);
        color-scheme: light !important;
    }

    /* Hide Streamlit default headers & toolbars completely */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header,
    header[data-testid="stHeader"],
    div[data-testid="stHeader"],
    .stAppHeader,
    [data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden !important;
    }
    .stDeployButton {display: none !important;}

    /* Force Light Theme Colors and Typography */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Inter', sans-serif !important;
        color: #1a1a2e !important;
        background: linear-gradient(135deg, #f1efff 0%, #edf6ff 48%, #edfaf3 100%) !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif !important;
        color: #1a1a2e !important;
    }

    /* Force text colors inside Streamlit markdown containers */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] div {
        color: #1a1a2e;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1240px !important;
    }

    /* Top Navigation Bar Floating Glass Container */
    div[data-testid="stHorizontalBlock"]:has(.logo) {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 18px !important;
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 20px !important;
        padding: 10px 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 24px rgba(124, 124, 235, 0.08) !important;
        border: 1px solid rgba(124, 124, 235, 0.12) !important;
    }

    /* Logo Text Styling */
    .logo {
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #1a1a2e !important;
        letter-spacing: -0.02em !important;
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    .logo span {
        color: #7c7ceb !important;
        font-weight: 800 !important;
    }

    /* Navigation Columns Row Alignment */
    div[data-testid="stHorizontalBlock"]:has(.logo) div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
        margin: 0 !important;
        gap: 12px !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.logo) div[data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.logo) .stButton {
        width: 100% !important;
        margin: 0 !important;
    }

    /* Navigation Buttons Base Styling */
    div[data-testid="stHorizontalBlock"]:has(.logo) .stButton > button {
        height: 42px !important;
        border-radius: 999px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0 1.25rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
    }

    /* Home & Resources Buttons (Nav link pill style) */
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_landing"],
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_resources"],
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_dashboard"] {
        background: rgba(124, 124, 235, 0.08) !important;
        color: #1a1a2e !important;
        border: 1px solid rgba(124, 124, 235, 0.18) !important;
        box-shadow: none !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_landing"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_resources"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_dashboard"]:hover {
        background: #ecebff !important;
        color: #6669e5 !important;
        border-color: rgba(124, 124, 235, 0.35) !important;
    }

    /* Log In / Action Buttons */
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_login"],
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_profile"],
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_logout"] {
        background: linear-gradient(135deg, #7c7ceb 0%, #6669e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(124, 124, 235, 0.25) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_login"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_profile"]:hover,
    div[data-testid="stHorizontalBlock"]:has(.logo) button[key="nav_logout"]:hover {
        background: linear-gradient(135deg, #6e71e5 0%, #585bd8 100%) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(124, 124, 235, 0.35) !important;
    }

    /* Hero Section Card Container */
    .aw-hero,
    div[data-testid="stHorizontalBlock"]:has(.hero-tagline) {
        background: linear-gradient(135deg, #f8f7ff 0%, #eef6ff 50%, #f0fdf4 100%) !important;
        border-radius: 24px !important;
        padding: 48px 44px !important;
        margin-bottom: 28px !important;
        border: 1px solid rgba(124, 124, 235, 0.16) !important;
        box-shadow: 0 8px 32px rgba(124, 124, 235, 0.1), 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        position: relative !important;
        overflow: hidden !important;
        align-items: center !important;
    }

    .aw-hero::before,
    div[data-testid="stHorizontalBlock"]:has(.hero-tagline)::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        right: -20% !important;
        width: 60% !important;
        height: 200% !important;
        background: radial-gradient(circle, rgba(124, 124, 235, 0.08) 0%, transparent 70%) !important;
        pointer-events: none !important;
    }

    /* Hero Title - Explicit Black */
    .stApp h1,
    div[data-testid="stMarkdownContainer"] h1,
    .aw-hero h1,
    div[data-testid="stHorizontalBlock"]:has(.hero-tagline) h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
        margin-bottom: 16px !important;
        color: #000000 !important;
        letter-spacing: -0.02em !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Hero Subtitle - Explicit Black */
    .stApp p.subtitle,
    div[data-testid="stMarkdownContainer"] p.subtitle,
    .aw-hero p.subtitle,
    div[data-testid="stHorizontalBlock"]:has(.hero-tagline) p.subtitle {
        font-size: 1.05rem !important;
        color: #000000 !important;
        font-weight: 500 !important;
        margin-bottom: 24px !important;
        max-width: 520px !important;
        line-height: 1.65 !important;
        opacity: 1 !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Hero Tagline Badge */
    .hero-tagline {
        display: inline-block !important;
        background: linear-gradient(135deg, #7c7ceb, #6669e5) !important;
        color: #ffffff !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        border-radius: 24px !important;
        margin-bottom: 18px !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        box-shadow: 0 4px 12px rgba(124, 124, 235, 0.3) !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Hero Action Buttons Styling */
    button[key="hero_checkin"] {
        background: linear-gradient(135deg, #7c7ceb 0%, #6669e5 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
        height: 46px !important;
        border-radius: 999px !important;
        box-shadow: 0 6px 16px rgba(124, 124, 235, 0.25) !important;
    }

    button[key="hero_learn"] {
        background: #ffffff !important;
        color: #1a1a2e !important;
        font-weight: 700 !important;
        border: 1.5px solid rgba(124, 124, 235, 0.3) !important;
        height: 46px !important;
        border-radius: 999px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }

    button[key="hero_learn"]:hover {
        background: #ecebff !important;
        color: #6669e5 !important;
        border-color: rgba(124, 124, 235, 0.5) !important;
    }

    /* Hero Badge */
    .aw-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 7px 16px !important;
        border-radius: 999px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: #1a1a2e !important;
        margin-top: 14px !important;
        border: 1px solid rgba(124, 124, 235, 0.25) !important;
    }

    /* Stats Section Container */
    .aw-stats-section,
    div[data-testid="stHorizontalBlock"]:has(.aw-stat-item) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 48px !important;
        padding: 32px 24px !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(248, 247, 255, 0.92)) !important;
        border-radius: 20px !important;
        margin: 28px 0 !important;
        border: 1px solid rgba(124, 124, 235, 0.12) !important;
        box-shadow: 0 4px 20px rgba(124, 124, 235, 0.08) !important;
    }

    .aw-stat-item {
        text-align: center !important;
        padding: 0 24px !important;
        position: relative !important;
    }

    .aw-stat-item:not(:last-child)::after {
        content: '' !important;
        position: absolute !important;
        right: -24px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        width: 1px !important;
        height: 40px !important;
        background: linear-gradient(to bottom, transparent, rgba(124, 124, 235, 0.2), transparent) !important;
    }

    .aw-stat-number {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #7c7ceb, #6669e5) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        line-height: 1 !important;
        margin-bottom: 6px !important;
    }

    .aw-stat-label {
        font-size: 0.9rem !important;
        color: #1a1a2e !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }

    /* Section titles */
    .aw-section-title {
        font-weight: 800 !important;
        font-size: 1.6rem !important;
        margin: 4px 0 16px 0 !important;
        color: #1a1a2e !important;
        letter-spacing: -0.02em !important;
        position: relative !important;
        display: inline-block !important;
    }

    .aw-section-title::after {
        content: '' !important;
        position: absolute !important;
        bottom: -6px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 50px !important;
        height: 3px !important;
        background: linear-gradient(90deg, #7c7ceb, #6669e5) !important;
        border-radius: 2px !important;
    }

    .aw-muted {
        color: #5c5b78 !important;
        font-size: 0.92rem !important;
    }

    .aw-card {
        background: #ffffff !important;
        border-radius: 18px !important;
        padding: 18px !important;
        box-shadow: 0 6px 20px rgba(124,124,235,0.07) !important;
        border: 1px solid rgba(165,166,246,0.14) !important;
    }

    .aw-feature-card {
        background: white !important;
        border-radius: 18px !important;
        padding: 20px 18px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(124,124,235,0.08) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        height: 100% !important;
        border: 1px solid rgba(124,124,235,0.12) !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }

    .aw-feature-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 28px rgba(124,124,235,0.15) !important;
        border-color: rgba(124,124,235,0.25) !important;
    }

    .aw-feature-icon {
        width: 48px !important;
        height: 48px !important;
        border-radius: 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #ecebff, #eef6ff) !important;
        font-size: 1.55rem !important;
        box-shadow: inset 0 0 0 1px rgba(124,124,235,0.08) !important;
    }

    .aw-step-card {
        background: white !important;
        border-radius: 20px !important;
        padding: 28px 24px !important;
        text-align: center !important;
        border: 1px solid rgba(124, 124, 235, 0.12) !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 12px rgba(124, 124, 235, 0.06) !important;
    }

    .aw-step-card:hover {
        transform: translateY(-6px) !important;
        box-shadow: 0 12px 32px rgba(124, 124, 235, 0.15) !important;
        border-color: rgba(124, 124, 235, 0.25) !important;
    }

    .aw-step-number {
        width: 48px !important;
        height: 48px !important;
        background: linear-gradient(135deg, #7c7ceb, #6669e5) !important;
        color: white !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin: 0 auto 16px !important;
        box-shadow: 0 4px 12px rgba(124, 124, 235, 0.3) !important;
    }

    .aw-step-title {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #1a1a2e !important;
        margin-bottom: 8px !important;
    }

    .aw-step-desc {
        font-size: 0.88rem !important;
        color: #3b3a58 !important;
        line-height: 1.55 !important;
    }

    .stButton > button {
        border-radius: 999px !important;
        font-weight: 700 !important;
        font-size: 0.93rem !important;
        border: none !important;
        padding: 0.72rem 1.25rem !important;
        background: linear-gradient(135deg, #7c7ceb 0%, #756ff0 100%) !important;
        color: white !important;
        transition: all 0.2s ease !important;
        height: 44px !important;
        box-shadow: 0 6px 16px rgba(124,124,235,0.18) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #6e71e5 0%, #6668dc 100%) !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 10px 18px rgba(124,124,235,0.24) !important;
    }

    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .aw-secondary-btn button {
        background: white !important;
        color: var(--ink) !important;
        border: 1.5px solid rgba(124,124,235,0.24) !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .aw-secondary-btn button:hover {
        background: var(--lavender-light) !important;
        color: var(--accent-deep) !important;
        border-color: rgba(124,124,235,0.4) !important;
    }

    div[data-testid="column"] .stButton > button {
        width: 100%;
    }

    .aw-chat-sidebar {
        padding-right: 8px;
    }

    .aw-chat-sidebar .aw-card {
        padding: 14px;
    }

    .aw-chat-list-item {
        width: 100%;
        text-align: left;
        background: transparent;
        border: 1px solid rgba(124,124,235,0.14);
        border-radius: 14px;
        padding: 10px 12px;
        margin: 6px 0;
        color: var(--ink);
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
    }

    .aw-chat-list-item:hover {
        background: rgba(124,124,235,0.05);
    }

    .aw-chat-list-active {
        background: var(--lavender-light);
        border-color: rgba(124,124,235,0.26);
    }

    .aw-chat-user {
        background: linear-gradient(135deg, var(--accent) 0%, #7a77ea 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 6px 18px;
        margin: 8px 0;
        max-width: 76%;
        margin-left: auto;
        text-align: left;
        box-shadow: 0 6px 14px rgba(124,124,235,0.18);
    }

    .aw-chat-bot {
        background: white;
        color: var(--ink);
        padding: 12px 16px;
        border-radius: 18px 18px 18px 6px;
        margin: 8px 0;
        max-width: 78%;
        box-shadow: 0 4px 14px rgba(124,124,235,0.09);
        border: 1px solid rgba(124,124,235,0.12);
    }

    .aw-pill,
    .aw-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.82);
        border: 1px solid rgba(124,124,235,0.2);
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--accent-deep);
    }

    .aw-quote {
        font-style: italic;
        color: var(--muted);
        border-left: 3px solid var(--accent);
        padding-left: 14px;
    }

    .aw-section-title {
        font-weight: 800;
        font-size: 1.5rem;
        margin: 4px 0 16px 0;
        color: #1a1a2e;
        letter-spacing: -0.02em;
        position: relative;
        display: inline-block;
    }

    .aw-section-title::after {
        content: '';
        position: absolute;
        bottom: -6px;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent-deep));
        border-radius: 2px;
    }

    .aw-muted {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .aw-back-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(124,124,235,0.22);
        border-radius: 999px;
        padding: 8px 14px;
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--ink);
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 16px;
    }

    .aw-back-btn:hover {
        background: var(--lavender-light);
        transform: translateY(-1px);
    }

    .aw-empty-state {
        background: linear-gradient(135deg, rgba(236,235,255,0.55), rgba(238,246,255,0.9));
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        border: 1px dashed rgba(124,124,235,0.24);
        color: var(--muted);
    }

    .aw-section-spacing {
        margin-top: 20px;
        margin-bottom: 20px;
    }

    @media (max-width: 1024px) {
        .aw-hero h1 {font-size: 2.3rem;}
        .aw-hero {padding: 36px 32px;}
    }

    @media (max-width: 768px) {
        .aw-hero {
            padding: 28px 24px;
        }
        .aw-hero h1 {
            font-size: 2rem;
        }
        .aw-hero p.subtitle {
            font-size: 0.95rem;
        }
        .aw-feature-card {
            padding: 16px 12px;
        }
        .aw-feature-icon {
            width: 42px;
            height: 42px;
            font-size: 1.4rem;
        }
        .aw-stats-section {
            flex-direction: column;
            gap: 20px;
            padding: 24px 16px;
        }
        .aw-stat-item {
            padding: 0;
        }
        .aw-stat-item:not(:last-child)::after {
            display: none;
        }
        .aw-step-card {
            padding: 20px 16px;
        }
        .aw-section-title {
            font-size: 1.3rem;
        }
    }

    /* Reset BaseWeb input wrapper borders to prevent double borders */
    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* Target direct input/textarea elements cleanly */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    input[type="text"],
    input[type="password"],
    textarea {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
        border: 1.5px solid rgba(124, 124, 235, 0.22) !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        caret-color: #1a1a2e !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-baseweb="input"] input:focus,
    div[data-baseweb="textarea"] textarea:focus,
    input[type="text"]:focus,
    input[type="password"]:focus,
    textarea:focus {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
        border-color: #7c7ceb !important;
        box-shadow: 0 0 0 3.5px rgba(124, 124, 235, 0.18) !important;
        outline: none !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder,
    textarea::placeholder,
    input::placeholder {
        color: #6b6a8a !important;
        -webkit-text-fill-color: #6b6a8a !important;
        opacity: 1 !important;
    }

    /* Tabs Styling */
    div[data-testid="stTabs"] button[role="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #5c5b78 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #7c7ceb !important;
        border-bottom-color: #7c7ceb !important;
        background: rgba(124, 124, 235, 0.06) !important;
    }

    /* Primary Button Theme Styling (Overriding Streamlit Red Theme everywhere including sidebar) */
    button[kind="primary"],
    button[data-testid="baseButton-primary"],
    button[kind="primaryFormSubmit"],
    button[data-testid="baseButton-primaryFormSubmit"],
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] button,
    button[kind="secondaryFormSubmit"],
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button[data-testid="baseButton-primary"],
    [data-testid="stSidebar"] .stButton button[kind="primary"],
    [data-testid="stSidebar"] .stButton button[data-testid="baseButton-primary"],
    [data-testid="stSidebar"] div[data-testid="column"] button[kind="primary"],
    [data-testid="stSidebar"] div[data-testid="column"] button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #7c7ceb 0%, #6669e5 100%) !important;
        background-color: #7c7ceb !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        border: none !important;
        border-radius: 999px !important;
        box-shadow: 0 4px 14px rgba(124, 124, 235, 0.25) !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid="baseButton-primaryFormSubmit"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover,
    [data-testid="stSidebar"] .stButton button[kind="primary"]:hover,
    [data-testid="stSidebar"] .stButton button[data-testid="baseButton-primary"]:hover,
    [data-testid="stSidebar"] div[data-testid="column"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] div[data-testid="column"] button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #6e71e5 0%, #585bd8 100%) !important;
        background-color: #6669e5 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(124, 124, 235, 0.35) !important;
    }
    
    /* Slider styling */
    div[data-testid="stSlider"] > div > div > div > div {
        background: var(--lavender-light);
    }
    
    /* Select slider styling */
    div[data-testid="stSelectSlider"] > div > div > div > div {
        background: var(--lavender-light);
    }
    
    /* Checkbox styling */
    div[data-testid="stCheckbox"] > div > div > label > div {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(124, 124, 235, 0.25);
        border-radius: 6px;
    }
    div[data-testid="stCheckbox"] > div > div > label > div:hover {
        border-color: var(--accent);
    }

    /* Popover Dropdown Styling */
    div[data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(124, 124, 235, 0.25) !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        color: #1a1a2e !important;
        height: 42px !important;
        padding: 0 16px !important;
        box-shadow: 0 4px 14px rgba(124, 124, 235, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stPopover"] > button:hover {
        border-color: #7c7ceb !important;
        box-shadow: 0 6px 18px rgba(124, 124, 235, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stPopoverBody"] {
        border-radius: 16px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(124, 124, 235, 0.2) !important;
        padding: 12px !important;
    }
</style>
"""

DARK_CSS = """
<style>
    /* Premium Midnight Dark Theme Overrides */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
        background: #0b0f19 !important;
        background-color: #0b0f19 !important;
        color: #f1f5f9 !important;
    }

    section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background: #111827 !important;
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .aw-card,
    div[data-testid="column"]:has(button[key="dash_checkin"]),
    div[data-testid="column"]:has(button[key="dash_chat"]) {
        background: #1e293b !important;
        background-color: #1e293b !important;
        border: 1px solid rgba(124, 124, 235, 0.25) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
        color: #f8fafc !important;
    }

    h1, h2, h3, h4, h5, h6,
    .aw-section-title, .aw-stat-label,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] label,
    p, span, label {
        color: #cbd5e1 !important;
    }

    .aw-muted {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }

    /* Inputs, Textareas, Selectboxes */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    textarea, input[type="text"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder,
    textarea::placeholder, input::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
    }

    /* Buttons */
    .stButton > button {
        background: #1e293b !important;
        background-color: #1e293b !important;
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }

    .stButton > button:hover {
        background: #6366f1 !important;
        background-color: #6366f1 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #818cf8 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: none !important;
    }

    div[data-testid="stPopover"] > button,
    div[data-testid="stPopoverBody"] {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: rgba(124, 124, 235, 0.25) !important;
    }
</style>
"""

SOFT_PASTEL_CSS = """
<style>
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: linear-gradient(135deg, #fff0f3 0%, #ffe5ec 50%, #fff5f7 100%) !important;
        color: #4a2e35 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #fff0f3 !important;
        border-right: 1px solid rgba(244, 63, 94, 0.15) !important;
    }
    .aw-card {
        background-color: #ffffff !important;
        border: 1px solid rgba(244, 63, 94, 0.15) !important;
        box-shadow: 0 6px 20px rgba(244, 63, 94, 0.08) !important;
    }
    h1, h2, h3, h4, h5, h6, b, strong, .aw-section-title {
        color: #881337 !important;
    }
    .aw-muted {
        color: #9f1239 !important;
    }
</style>
"""

OCEAN_CSS = """
<style>
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #f0f9ff 100%) !important;
        color: #0f172a !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #e0f2fe !important;
        border-right: 1px solid rgba(14, 165, 233, 0.15) !important;
    }
    .aw-card {
        background-color: #ffffff !important;
        border: 1px solid rgba(14, 165, 233, 0.15) !important;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.08) !important;
    }
    h1, h2, h3, h4, h5, h6, b, strong, .aw-section-title {
        color: #0369a1 !important;
    }
    .aw-muted {
        color: #0369a1 !important;
    }
</style>
"""


CLEANUP_SCRIPT = """
<script>
(function() {
    try {
        const targetDoc = (window.parent && window.parent.document) ? window.parent.document : document;
        targetDoc.querySelectorAll('.aw-celebration-root').forEach(el => el.remove());
    } catch(e) {}
})();
</script>
"""


def inject_base_css(st):
    st.markdown(BASE_CSS, unsafe_allow_html=True)
    st.markdown(CLEANUP_SCRIPT, unsafe_allow_html=True)
    theme = st.session_state.get("theme", "Light")
    if theme == "Soft Pastel":
        st.markdown(SOFT_PASTEL_CSS, unsafe_allow_html=True)
    elif theme == "Ocean Breeze":
        st.markdown(OCEAN_CSS, unsafe_allow_html=True)


