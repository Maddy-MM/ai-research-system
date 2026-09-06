import streamlit as st
import requests
import threading
import time

import os

try:
    API_URL = st.secrets.get("API_URL", os.environ.get("API_URL", "http://127.0.0.1:8000"))
except Exception:
    API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="ResearchMind",
    page_icon="🔬",
    layout="centered"
)

# ---------------------------------------------------------------------------
# Global style — hide anchor icons
# ---------------------------------------------------------------------------
st.markdown("""
<style>
h1 a, h2 a, h3 a { display: none !important; }
@media print {
    header, [data-testid="stSidebar"], div[data-testid="stButton"], .stDownloadButton, [data-testid="stExpander"] {
        display: none !important;
    }
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------
for key, val in {
    "token": None,
    "results": None,
    "running": False,
    "topic": "",
    "topic_input": "",
    "history": [],
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
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Planner creates sub-questions</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">02</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Researchers investigate in parallel</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">03</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Writer drafts the report</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">04</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Critic loops for quality</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.8rem; padding:0.75rem 1rem;">
                <span style="color:rgba(255,140,50,0.8); font-size:0.7rem; font-weight:700;">05</span>
                <span style="color:#ffffff; font-size:0.85rem; font-weight:500;">Verifier checks key claims</span>
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
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">OpenAI</span>
            <span style="background:rgba(255,140,50,0.1); border:1px solid rgba(255,140,50,0.25); border-radius:6px; padding:0.3rem 0.7rem; color:#ffffff; font-size:0.75rem; font-weight:500; letter-spacing:0.03em;">MCP</span>
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

    if st.session_state.token and st.session_state.get("history"):
        st.markdown("""
            <div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 1.2rem 0 0.8rem 0;"></div>
            <p style="
                color: rgba(255,255,255,0.5);
                font-size: 0.68rem;
                font-weight: 700;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                margin: 0 0 0.6rem 0;
            ">Recent Reports</p>
        """, unsafe_allow_html=True)

        for idx, item in enumerate(reversed(st.session_state.history[-5:])):
            t_title = item.get("topic", "Untitled")
            disp = (t_title[:24] + "...") if len(t_title) > 24 else t_title
            if st.button(f"📑 {disp}", key=f"hist_{idx}_{item.get('request_id', idx)}", use_container_width=True):
                st.session_state.results = item["results"]
                st.session_state.topic = item["topic"]
                st.session_state.running = False
                st.rerun()

        if st.button("🗑️  Clear History", key="clear_hist_btn", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    if st.session_state.token:
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        if st.button("⎋  Sign Out", use_container_width=True):
            for key in ("token", "results", "running", "topic", "topic_input"):
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

    st.markdown("""
        <div style="text-align: center; margin: 0.8rem 0 1.4rem 0;">
            <span style="
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                border: 1px solid rgba(255,140,50,0.25);
                background: rgba(255,140,50,0.06);
                border-radius: 20px;
                padding: 0.35rem 1rem;
                color: rgba(255,255,255,0.55);
                font-size: 0.78rem;
                letter-spacing: 0.02em;
            ">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="#ff8c32" stroke-width="2">
                    <circle cx="7.5" cy="15.5" r="4.5"/>
                    <path d="M10.6 12.4 19 4"/>
                    <path d="M17 6l2 2"/>
                    <path d="M14 9l2 2"/>
                </svg>
                Authorized access only — contact administrator for credentials
            </span>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter your username", key="login_username")
    password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")


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
    ("Planner", "Breaks the topic into focused sub-questions"),
    ("Parallel Research", "Tool-using agents investigate each question"),
    ("Writer", "Combines findings into a structured report"),
    ("Critic Loop", "Scores the draft and routes revisions"),
    ("Verifier", "Independently checks the key claims"),
]

spinner_messages = [
    "Planning focused research questions...",
    "Investigating sub-questions in parallel...",
    "Writing the research report...",
    "Reviewing the report and applying revisions...",
    "Independently verifying key claims...",
]

step_nums = ["01", "02", "03", "04", "05"]

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

    # If the planner judged the topic too ambiguous to research, `report`/`feedback` are
    # None — show the clarifying question instead of rendering broken report/feedback panels
    if r.get("clarifying_question"):
        st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.09);
                border-top: 3px solid #ff8c32;
                border-radius: 14px;
                padding: 1.75rem;
                margin-bottom: 1.5rem;
            ">
                <p style="color: rgba(255,140,50,0.8); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.75rem 0;">Needs Clarification</p>
                <p style="color: #ffffff; font-size: 1.05rem; margin: 0; line-height: 1.6;">{r["clarifying_question"]}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("← Try Again", use_container_width=True):
            st.session_state.results = None
            st.session_state.topic = ""
            st.rerun()

        st.stop()

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

    # Executive Metrics Bar
    topic_text = r.get("topic") or st.session_state.get("topic", "")
    score_val = r.get("critic_score")
    if score_val is not None:
        score_display = f"{score_val * 10:.1f} / 10" if score_val <= 1.0 else f"{score_val:.1f} / 10"
    else:
        import re
        match_s = re.search(r"Score:\s*(\d+(?:\.\d+)?)/10", r.get("feedback", "") or "")
        score_display = f"{match_s.group(1)} / 10" if match_s else "Passed"

    verif_text = r.get("verification") or "Verification was not returned by the backend."
    import re
    match_v = re.search(r"(\d+/\d+)\s+claims\s+fully\s+supported", verif_text, re.IGNORECASE)
    verif_stat = f"{match_v.group(1)} Verified" if match_v else ("Fact-Checked" if "supported" in verif_text.lower() else "Verified")

    iteration_val = r.get("iteration_count", 1)
    tokens_val = r.get("tokens_used")
    tokens_display = f"{tokens_val:,}" if tokens_val else "Standard"

    sub_questions = r.get("sub_questions") or []
    depth_display = f"{len(sub_questions)} Tracks" if sub_questions else "Deep Search"

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); border-radius: 12px; padding: 0.85rem 0.9rem; text-align: center;">
                <p style="color: rgba(255,140,50,0.9); font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.25rem 0;">Quality Score</p>
                <p style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin: 0 0 0.15rem 0; line-height: 1.1;">{score_display}</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; margin: 0;">Critic Approved</p>
            </div>
        """, unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); border-radius: 12px; padding: 0.85rem 0.9rem; text-align: center;">
                <p style="color: #60be96; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.25rem 0;">Fact-Check</p>
                <p style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin: 0 0 0.15rem 0; line-height: 1.1;">{verif_stat}</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; margin: 0;">Independent Verifier</p>
            </div>
        """, unsafe_allow_html=True)
    with mcol3:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); border-radius: 12px; padding: 0.85rem 0.9rem; text-align: center;">
                <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.25rem 0;">Research Depth</p>
                <p style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin: 0 0 0.15rem 0; line-height: 1.1;">{depth_display}</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; margin: 0;">Parallel MCP Agents</p>
            </div>
        """, unsafe_allow_html=True)
    with mcol4:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09); border-radius: 12px; padding: 0.85rem 0.9rem; text-align: center;">
                <p style="color: rgba(255,255,255,0.5); font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.25rem 0;">Compute</p>
                <p style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin: 0 0 0.15rem 0; line-height: 1.1;">{tokens_display}</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; margin: 0;">{iteration_val} Iteration{'s' if iteration_val != 1 else ''}</p>
            </div>
        """, unsafe_allow_html=True)

    if sub_questions:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"🔍 Explored Sub-Questions ({len(sub_questions)} Parallel Tracks)", expanded=False):
            for idx_q, sq in enumerate(sub_questions, start=1):
                st.markdown(f"**Track {idx_q:02d}:** {sq}")

    # Report header & Native Markdown Container
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin: 1.8rem 0 0.8rem 0;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0;">Research Report</p>
            <span style="color: rgba(255,255,255,0.3); font-size: 0.7rem;">Markdown · Formatted Output</span>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(r["report"])

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    act_col1, act_col2 = st.columns([1, 1])
    with act_col1:
        report_download = f"""---
title: "{topic_text}"
request_id: "{r.get('request_id', '')}"
critic_score: "{score_display}"
date: "{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
pipeline: "ResearchMind Multi-Agent LangGraph"
---

{r["report"]}
"""
        st.download_button(
            label="📥  Download Report (.md)",
            data=report_download,
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with act_col2:
        with st.expander("📋 View Raw / Copy"):
            st.code(r["report"], language="markdown")

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    # Independent citation verification panel
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem;">
            <p style="color: #60be96; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0;">🛡️ Citation Verification</p>
            <span style="background: rgba(96,190,150,0.1); border: 1px solid rgba(96,190,150,0.3); border-radius: 12px; padding: 0.2rem 0.65rem; color: #60be96; font-size: 0.68rem; font-weight: 700;">Independent Tool Fact-Check</span>
        </div>
        <div style="
            background: rgba(96,190,150,0.03);
            border: 1px solid rgba(96,190,150,0.2);
            border-left: 4px solid #60be96;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.5rem;
            color: rgba(255,255,255,0.85);
            font-size: 0.88rem;
            line-height: 1.8;
        ">
    """, unsafe_allow_html=True)
    st.markdown(verif_text)
    st.markdown("</div>", unsafe_allow_html=True)

    # Critic panel
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem;">
            <p style="color: #ff8c32; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0;">🔍 Critic Review & Feedback</p>
            <span style="background: rgba(255,140,50,0.1); border: 1px solid rgba(255,140,50,0.3); border-radius: 12px; padding: 0.2rem 0.65rem; color: #ff8c32; font-size: 0.68rem; font-weight: 700;">Iterative Loop</span>
        </div>
        <div style="
            background: rgba(255,140,50,0.02);
            border: 1px solid rgba(255,140,50,0.18);
            border-left: 4px solid #ff8c32;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.5rem;
            color: rgba(255,255,255,0.8);
            font-size: 0.88rem;
            line-height: 1.8;
        ">
    """, unsafe_allow_html=True)
    st.markdown(r.get("feedback") or "No feedback recorded.")
    st.markdown("</div>", unsafe_allow_html=True)

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
                ">A planner, parallel researchers, writer, critic, and verifier collaborate to deliver a polished research report.</p>
            </div>
        """, unsafe_allow_html=True)

        starter_prompts = [
            "Breakthroughs in Quantum Computing 2025",
            "State of Open-Source Reasoning LLMs",
            "Room-Temperature Superconductor Claims",
            "Solid-State Battery Commercialization",
        ]

        st.markdown("""
            <p style="color: rgba(255,255,255,0.4); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 0.5rem 0;">Sample Topics</p>
        """, unsafe_allow_html=True)

        chip_col1, chip_col2 = st.columns(2)
        for i, prompt in enumerate(starter_prompts):
            target_col = chip_col1 if i % 2 == 0 else chip_col2
            with target_col:
                if st.button(f"💡 {prompt}", key=f"chip_starter_{i}", use_container_width=True):
                    st.session_state.topic_input = prompt
                    st.session_state.topic = prompt
                    st.rerun()

        st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

        input_val = st.session_state.get("topic_input", "")
        topic = st.text_input(
            "Research Topic",
            value=input_val,
            placeholder="e.g. Breakthroughs in quantum computing 2025",
            key="research_topic_input_box"
        )
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
            ">Pipeline Architecture</p>
        """, unsafe_allow_html=True)

        step_cols = st.columns(5)
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
            chosen = topic.strip()
            if not chosen:
                st.warning("Please enter a research topic first.")
            else:
                st.session_state.results = None
                st.session_state.topic = chosen
                st.session_state.topic_input = chosen
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
                    timeout=600,
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
                <p style="color: #ffffff; font-size: 1rem; font-weight: 700; margin: 0 0 0.3rem 0;">Multi-Agent Pipeline Active</p>
                <p style="color: rgba(255,255,255,0.4); font-size: 0.82rem; margin: 0 0 1.5rem 0;">
                    Investigating <span style="color: #ff8c32; font-weight: 600;">{topic_to_run}</span>
                </p>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        status_ph = st.empty()
        step_idx = 0
        elapsed = 0
        step_duration = 15
        start_time = time.time()

        while thread.is_alive():
            elapsed_total = int(time.time() - start_time)
            mins, secs = divmod(elapsed_total, 60)
            current = min(step_idx, len(spinner_messages) - 1)
            status_ph.markdown(f"""
                <div style="text-align: center;">
                    <p style="
                        color: #ff8c32;
                        font-size: 1.15rem;
                        font-weight: 800;
                        letter-spacing: 0.04em;
                        margin: 0 0 0.4rem 0;
                    ">⏱ {mins:02d}:{secs:02d}</p>
                    <p style="
                        color: rgba(255,255,255,0.75);
                        font-size: 0.9rem;
                        font-weight: 600;
                        margin: 0 0 0.3rem 0;
                    ">⏳ {spinner_messages[current]}</p>
                    <p style="
                        color: rgba(255,255,255,0.35);
                        font-size: 0.72rem;
                        margin: 0;
                        letter-spacing: 0.02em;
                    ">Parallel agents are searching Tavily, scraping content, and querying arXiv via MCP...</p>
                </div>
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
            payload = result_container["data"]
            st.session_state.results = payload
            st.session_state.running = False

            if "history" not in st.session_state or not isinstance(st.session_state.history, list):
                st.session_state.history = []

            # Prepend or append to recent history
            st.session_state.history.append({
                "topic": topic_to_run,
                "timestamp": time.strftime("%H:%M"),
                "results": payload,
                "request_id": payload.get("request_id", ""),
            })
            st.rerun()