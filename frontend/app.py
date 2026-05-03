import streamlit as st
import requests
import threading
import time

# API_URL = "https://your-backend.onrender.com"  # replace with your Render URL
API_URL = "http://127.0.0.1:8000"             # uncomment for local dev

st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Global style — hide anchor icons
# ---------------------------------------------------------------------------
st.markdown("""
<style>
h1 a, h2 a, h3 a { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------
for key, val in {
    "token": None,
    "results": None,
    "running": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.4rem 0 1.2rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            margin-bottom: 1.4rem;
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                border-radius: 8px;
                width: 32px;
                height: 32px;
                flex-shrink: 0;
                box-shadow: 0 2px 10px rgba(255,140,50,0.4);
            ">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="white">
                    <path d="M11 2a9 9 0 1 0 9 9A9 9 0 0 0 11 2zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm1-11h-2v5l4.25 2.52.75-1.23-3-1.79z"/>
                </svg>
            </div>
            <div>
                <p style="
                    color: #ffffff;
                    font-size: 0.9rem;
                    font-weight: 800;
                    letter-spacing: 0.02em;
                    margin: 0;
                    line-height: 1;
                ">Research<span style="color: #ff8c32; font-weight: 400;">Mind</span></p>
                <p style="
                    color: rgba(255,255,255,0.4);
                    font-size: 0.65rem;
                    letter-spacing: 0.06em;
                    margin: 0.2rem 0 0 0;
                    line-height: 1;
                    text-transform: uppercase;
                ">Multi-Agent Pipeline</p>
            </div>
        </div>

        <p style="
            color: rgba(255,255,255,0.5);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin: 0 0 0.7rem 0;
        ">How it works</p>

        <div style="
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 1.4rem;
            background: rgba(255,255,255,0.02);
        ">
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">01</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Search Agent finds sources</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">02</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Reader Agent scrapes pages</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">03</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Writer Chain drafts report</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem;">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">04</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Critic Chain scores &amp; reviews</span>
            </div>
        </div>

        <p style="
            color: rgba(255,255,255,0.4);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin: 0 0 0.7rem 0;
        ">Tech Stack</p>

        <div style="display: flex; flex-wrap: wrap; gap: 0.45rem; margin-bottom: 1.8rem;">
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">FastAPI</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">LangChain</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">LangGraph</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">Groq</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">Tavily</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">JWT</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">Prometheus</span>
        </div>

        <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem;">
            <p style="
                color: rgba(255,255,255,0.3);
                font-size: 0.65rem;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                margin: 0;
                text-align: center;
            ">AI-powered research intelligence</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.token:
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("⎋  Sign Out", use_container_width=True):
            for key in ("token", "results", "running"):
                st.session_state[key] = None if key != "running" else False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SCREEN 0: LOGIN
# ---------------------------------------------------------------------------
if not st.session_state.token:

    st.markdown("""
        <style>
            .block-container {
                padding-top: 5vh !important;
                max-width: 400px !important;
            }
            div[data-testid="stTextInput"] div[data-testid="InputInstructions"] {
                display: none !important;
            }
            div[data-testid="stTextInput"] label {
                color: rgba(255,255,255,0.38);
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            }
            div[data-testid="stTextInput"] input {
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
                background-color: rgba(255,255,255,0.04);
                color: #ffffff;
                padding: 0.65rem 1rem;
                font-size: 0.93rem;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: rgba(255,140,50,0.5);
                box-shadow: 0 0 0 3px rgba(255,140,50,0.08);
            }
            div[data-testid="stButton"] button {
                background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.92rem;
                letter-spacing: 0.05em;
                transition: all 0.2s ease;
                box-shadow: 0 4px 18px rgba(255,140,50,0.35);
            }
            div[data-testid="stButton"] button:hover {
                background: linear-gradient(135deg, #ffaa55 0%, #ff8c32 100%);
                box-shadow: 0 6px 24px rgba(255,140,50,0.5);
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            div[data-testid="stMarkdown"] > div { width: 100% !important; }
        </style>
        <div style="width: 100%; text-align: center; margin-bottom: 1.2rem;">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                border-radius: 20px;
                width: 68px;
                height: 68px;
                box-shadow: 0 8px 32px rgba(255,140,50,0.45);
                margin-bottom: 0.5rem;
            ">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="white">
                    <path d="M11 2a9 9 0 1 0 9 9A9 9 0 0 0 11 2zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm1-11h-2v5l4.25 2.52.75-1.23-3-1.79z"/>
                </svg>
            </div>
            <h1 style="
                color: #ffffff;
                font-size: 1.9rem;
                font-weight: 900;
                margin: 0;
                letter-spacing: -0.03em;
                line-height: 1;
            ">Research<span style="color: #ff8c32; font-weight: 300;">Mind</span></h1>
            <div style="
                display: inline-block;
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 20px;
                padding: 0.3rem 0.9rem;
                margin-top: 0.6rem;
            ">
                <p style="
                    color: rgba(255,255,255,0.38);
                    font-size: 0.68rem;
                    letter-spacing: 0.14em;
                    text-transform: uppercase;
                    font-weight: 600;
                    margin: 0;
                ">Multi-Agent Research Pipeline</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    st.markdown("<div style='height: 0.2rem'></div>", unsafe_allow_html=True)

    if st.button("Sign In", use_container_width=True):
        if not username or not password:
            st.warning("Please enter both username and password.")
        else:
            with st.spinner("Signing in..."):
                try:
                    res = requests.post(
                        f"{API_URL}/auth/token",
                        data={"username": username, "password": password},
                        timeout=90,
                    )
                    body = res.json()
                except Exception:
                    st.error("Could not reach the backend. Please try again.")
                    st.stop()

            if "access_token" in body:
                st.session_state.token = body["access_token"]
                st.rerun()
            else:
                st.error(body.get("detail", "Login failed."))

    st.markdown("""
        <p style="text-align: center; margin-top: 1rem; color: rgba(255,255,255,0.5); font-size: 0.82rem; letter-spacing: 0.03em;">
            ⏱ First sign-in may take 30–60s while the backend wakes up
        </p>
    """, unsafe_allow_html=True)

    st.stop()


# ---------------------------------------------------------------------------
# Shared data — defined outside both screens so both can access
# ---------------------------------------------------------------------------
steps = [
    ("Search Agent", "Gathers recent web information"),
    ("Reader Agent", "Scrapes and extracts content"),
    ("Writer Chain", "Drafts the research report"),
    ("Critic Chain", "Reviews and scores the report"),
]

spinner_messages = [
    "Searching the web for recent sources...",
    "Scraping and reading top results...",
    "Writing the research report...",
    "Reviewing and scoring the report...",
]

step_nums = ["01", "02", "03", "04"]

r = st.session_state.results


# ---------------------------------------------------------------------------
# SCREEN 2: RESULTS
# ---------------------------------------------------------------------------
if r:

    st.markdown("""
        <style>
            .main .block-container {
                max-width: 760px !important;
                padding-top: 2.5rem !important;
            }
            div[data-testid="stButton"] button {
                background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                border: none;
                border-radius: 12px;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.92rem;
                letter-spacing: 0.05em;
                padding: 0.65rem 1rem;
                transition: all 0.2s ease;
                box-shadow: 0 4px 18px rgba(255,140,50,0.3);
            }
            div[data-testid="stButton"] button:hover {
                background: linear-gradient(135deg, #ffaa55 0%, #ff8c32 100%);
                box-shadow: 0 6px 24px rgba(255,140,50,0.5);
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    # Top bar
    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 2rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="
                    width: 28px; height: 28px;
                    background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                    border-radius: 8px;
                    display: inline-flex; align-items: center; justify-content: center;
                    box-shadow: 0 2px 10px rgba(255,140,50,0.35);
                ">
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="white">
                        <path d="M11 2a9 9 0 1 0 9 9A9 9 0 0 0 11 2zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm1-11h-2v5l4.25 2.52.75-1.23-3-1.79z"/>
                    </svg>
                </div>
                <span style="color: #ffffff; font-size: 0.95rem; font-weight: 800;">Research<span style="color: #ff8c32; font-weight: 300;">Mind</span></span>
            </div>
            <div style="
                background: rgba(255,140,50,0.08);
                border: 1px solid rgba(255,140,50,0.2);
                border-radius: 20px;
                padding: 0.25rem 0.85rem;
                display: inline-flex; align-items: center; gap: 0.5rem;
            ">
                <div style="width: 5px; height: 5px; border-radius: 50%; background: #ff8c32;"></div>
                <span style="color: rgba(255,255,255,0.6); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">Report Ready</span>
            </div>
        </div>

        <div style="margin-bottom: 1.5rem;">
            <p style="color: rgba(255,255,255,0.35); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin: 0 0 0.3rem 0;">Research Topic</p>
            <h2 style="color: #ffffff; font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">{r.get('topic', '')}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Report panel
    st.markdown("""
        <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.75rem 0;">Research Report</p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.09);
            border-top: 3px solid #ff8c32;
            border-radius: 14px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            color: rgba(255,255,255,0.85);
            font-size: 0.9rem;
            line-height: 1.8;
        ">{r["report"]}</div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="Download Report",
        data=r["report"],
        file_name=f"research_report_{int(time.time())}.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # Critic panel
    st.markdown("""
        <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.75rem 0;">Critic Feedback</p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.07);
            border-top: 3px solid rgba(255,140,50,0.4);
            border-radius: 14px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            color: rgba(255,255,255,0.75);
            font-size: 0.88rem;
            line-height: 1.8;
        ">{r["feedback"]}</div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0;
            border-top: 1px solid rgba(255,255,255,0.07);
            margin-top: 0.5rem;
        ">
            <p style="color: rgba(255,255,255,0.2); font-size: 0.72rem; margin: 0; letter-spacing: 0.04em;">
                Request ID: {r.get('request_id', '—')}
            </p>
            <p style="color: rgba(255,255,255,0.2); font-size: 0.72rem; margin: 0;">
                ResearchMind · Multi-Agent Pipeline
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    if st.button("← New Research", use_container_width=True):
        st.session_state.results = None
        st.session_state.topic = ""
        st.rerun()


# ---------------------------------------------------------------------------
# SCREEN 1: MAIN APP
# ---------------------------------------------------------------------------
else:

    st.markdown("""
        <style>
            .main .block-container {
                max-width: 760px !important;
                padding-top: 2.5rem !important;
            }
            div[data-testid="stTextInput"] label {
                color: rgba(255,255,255,0.38);
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
            }
            div[data-testid="stTextInput"] input {
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                background-color: rgba(255,255,255,0.04);
                color: #ffffff;
                padding: 0.75rem 1rem;
                font-size: 0.95rem;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: rgba(255,140,50,0.5);
                box-shadow: 0 0 0 3px rgba(255,140,50,0.08);
            }
            div[data-testid="stTextInput"] input::placeholder {
                color: rgba(255,255,255,0.2);
            }
            div[data-testid="stButton"] button {
                background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                border: none;
                border-radius: 12px;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.92rem;
                letter-spacing: 0.05em;
                padding: 0.65rem 1rem;
                transition: all 0.2s ease;
                box-shadow: 0 4px 18px rgba(255,140,50,0.3);
            }
            div[data-testid="stButton"] button:hover {
                background: linear-gradient(135deg, #ffaa55 0%, #ff8c32 100%);
                box-shadow: 0 6px 24px rgba(255,140,50,0.5);
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state.running:
        # Header
        st.markdown("""
            <div style="margin-bottom: 0.5rem;">
                <div style="display: inline-block; margin-bottom: 1.2rem;">
                    <div style="
                        display: inline-flex;
                        align-items: center;
                        gap: 0.7rem;
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.15);
                        border-radius: 14px;
                        padding: 0.65rem 1.2rem;
                    ">
                        <div style="
                            width: 30px;
                            height: 30px;
                            background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            flex-shrink: 0;
                            box-shadow: 0 2px 10px rgba(255,140,50,0.4);
                        ">
                            <svg viewBox="0 0 24 24" width="15" height="15" fill="white">
                                <path d="M11 2a9 9 0 1 0 9 9A9 9 0 0 0 11 2zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm1-11h-2v5l4.25 2.52.75-1.23-3-1.79z"/>
                            </svg>
                        </div>
                        <span style="
                            color: #ffffff;
                            font-size: 1.25rem;
                            font-weight: 800;
                            letter-spacing: -0.02em;
                        ">Research<span style="color: #ff8c32; font-weight: 300;">Mind</span></span>
                    </div>
                </div>
                <div style="
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    background: rgba(255,140,50,0.08);
                    border: 1px solid rgba(255,140,50,0.2);
                    border-radius: 20px;
                    padding: 0.25rem 0.85rem;
                    margin-bottom: 0.9rem;
                ">
                    <div style="width: 5px; height: 5px; border-radius: 50%; background: #ff8c32;"></div>
                    <p style="
                        color: rgba(255,255,255,0.6);
                        font-size: 0.68rem;
                        font-weight: 700;
                        letter-spacing: 0.12em;
                        text-transform: uppercase;
                        margin: 0;
                    ">Multi-Agent Research Pipeline</p>
                </div>
                <p style="
                    color: rgba(255,255,255,0.5);
                    font-size: 0.88rem;
                    margin: 0 0 1.8rem 0;
                    line-height: 1.7;
                    border-left: 2px solid rgba(255,140,50,0.3);
                    padding-left: 0.75rem;
                ">Four specialized AI agents collaborate to deliver a polished research report on any topic.</p>
            </div>
        """, unsafe_allow_html=True)

        topic = st.text_input("Research Topic", placeholder="e.g. Breakthroughs in quantum computing 2025")
        run_btn = st.button("Run Research Pipeline", use_container_width=True)

        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

        # Pipeline cards
        st.markdown("""
            <p style="
                color: rgba(255,255,255,0.4);
                font-size: 0.68rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                margin: 0 0 0.75rem 0;
            ">Pipeline</p>
        """, unsafe_allow_html=True)

        step_cols = st.columns(4)
        for i, (name, desc) in enumerate(steps):
            with step_cols[i]:
                st.markdown(f"""
                    <div style="
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.12);
                        border-top: 3px solid rgba(255,140,50,0.4);
                        border-radius: 12px;
                        padding: 1.2rem 1rem;
                        min-height: 130px;
                    ">
                        <p style="color: rgba(255,140,50,0.8); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; margin: 0 0 0.5rem 0;">{step_nums[i]}</p>
                        <p style="color: #ffffff; font-size: 0.9rem; font-weight: 700; margin: 0 0 0.3rem 0;">{name}</p>
                        <p style="color: rgba(255,255,255,0.5); font-size: 0.78rem; margin: 0; line-height: 1.4;">{desc}</p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        # Run pipeline
        if run_btn:
            if not topic.strip():
                st.warning("Please enter a research topic first.")
            else:
                st.session_state.results = None
                st.session_state.topic = topic
                st.session_state.running = True
                st.rerun()

    if st.session_state.running:
        result_container = {"data": None, "error": None}

        token = st.session_state.token
        topic_to_run = st.session_state.get("topic", "")

        def call_api():
            try:
                res = requests.post(
                    f"{API_URL}/research/run",
                    json={"topic": topic_to_run},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=180,
                )
                result_container["data"] = res.json()
            except Exception as e:
                result_container["error"] = str(e)

        thread = threading.Thread(target=call_api)
        thread.start()

        st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                margin-top: 1rem;
            ">
                <div style="
                    width: 44px;
                    height: 44px;
                    background: linear-gradient(135deg, #ff8c32 0%, #e06b10 100%);
                    border-radius: 12px;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 1rem;
                    box-shadow: 0 4px 20px rgba(255,140,50,0.35);
                ">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="white">
                        <path d="M11 2a9 9 0 1 0 9 9A9 9 0 0 0 11 2zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm1-11h-2v5l4.25 2.52.75-1.23-3-1.79z"/>
                    </svg>
                </div>
                <p style="color: #ffffff; font-size: 1rem; font-weight: 700; margin: 0 0 0.3rem 0;">Pipeline Running</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.82rem; margin: 0 0 1.5rem 0;">
                    Researching <span style="color: #ff8c32; font-weight: 600;">{topic_to_run}</span>
                </p>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
        status_ph = st.empty()
        step_idx = 0
        elapsed = 0
        step_duration = 15

        while thread.is_alive():
            current = min(step_idx, len(spinner_messages) - 1)
            status_ph.markdown(f"""
                <p style="
                    color: rgba(255,255,255,0.55);
                    font-size: 0.82rem;
                    text-align: center;
                    margin: 0;
                    letter-spacing: 0.02em;
                ">⏳ {spinner_messages[current]}</p>
            """, unsafe_allow_html=True)
            time.sleep(1)
            elapsed += 1
            if elapsed >= step_duration and step_idx < len(spinner_messages) - 1:
                step_idx += 1
                elapsed = 0

        thread.join()
        status_ph.empty()

        st.markdown("</div>", unsafe_allow_html=True)

        if result_container["error"]:
            st.error(f"Could not reach the backend: {result_container['error']}")
            st.session_state.running = False
        elif "detail" in result_container["data"]:
            st.error(f"Pipeline failed: {result_container['data']['detail']}")
            st.session_state.running = False
        else:
            st.session_state.results = result_container["data"]
            st.session_state.running = False
            st.rerun()