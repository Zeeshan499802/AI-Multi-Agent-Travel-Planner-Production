import uuid

import streamlit as st
from importlib.metadata import version
from langchain_core.messages import HumanMessage

st.write("DEBUG - LangGraph version:", version("langgraph"))

from langgraph.types import Command

from graph import app

version("langgraph")


st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM RESPONSIVE UI
# Presentation only — no agent/business logic is changed below.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #07111f;
    --panel: #0c192b;
    --panel-2: #0f2035;
    --border: rgba(116, 164, 214, .18);
    --text: #edf6ff;
    --muted: #8fa9c2;
    --blue: #4da3ff;
    --blue-2: #2677d8;
    --cyan: #57d6ff;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(45, 125, 220, .15), transparent 30%),
        radial-gradient(circle at 92% 12%, rgba(38, 184, 232, .09), transparent 26%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1180px;
    padding: 2rem 2rem 4rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #07111e 0%, #091522 100%) !important;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.15rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: .75rem;
    margin-bottom: 1.5rem;
}

.sidebar-logo {
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: linear-gradient(135deg, #2489ee, #1551a1);
    box-shadow: 0 8px 24px rgba(36, 137, 238, .28);
    font-size: 1.25rem;
}

.sidebar-brand-title {
    color: #fff;
    font-size: 1rem;
    font-weight: 800;
}

.sidebar-brand-sub {
    color: var(--muted);
    font-size: .68rem;
    margin-top: .15rem;
}

.sidebar-section {
    color: #b9d9f5;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin: 1.5rem 0 .55rem;
}

.sidebar-chip {
    padding: .62rem .75rem;
    margin: .4rem 0;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: rgba(255,255,255,.025);
    color: #a9c7e2;
    font-size: .78rem;
}

.thread-box {
    padding: .7rem .75rem;
    border-radius: 10px;
    border: 1px dashed rgba(77,163,255,.25);
    background: rgba(77,163,255,.045);
    color: #7fa6c8;
    font-size: .68rem;
    line-height: 1.5;
    word-break: break-all;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea {
    background: #081728 !important;
    color: #edf6ff !important;
    border: 1px solid rgba(111, 163, 214, .22) !important;
    border-radius: 12px !important;
    transition: .2s ease !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(77,163,255,.75) !important;
    box-shadow: 0 0 0 3px rgba(77,163,255,.10) !important;
}

.stTextArea textarea {
    min-height: 125px !important;
}

label {
    color: #a9c9e6 !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 11px !important;
    min-height: 44px !important;
    font-weight: 700 !important;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #258ff0, #1857b0) !important;
    border: 1px solid rgba(120,195,255,.35) !important;
    color: white !important;
    box-shadow: 0 10px 28px rgba(20,100,205,.25) !important;
}

.stButton > button[kind="secondary"] {
    background: #0d1d30 !important;
    border: 1px solid var(--border) !important;
    color: #d7e9f8 !important;
}

/* Hero */
.hero {
    position: relative;
    overflow: hidden;
    min-height: 285px;
    border: 1px solid rgba(101, 165, 224, .18);
    border-radius: 24px;
    padding: 2.6rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    background:
        linear-gradient(90deg, rgba(4,13,25,.96) 0%, rgba(6,22,40,.84) 54%, rgba(6,22,40,.38) 100%),
        url("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1600&q=85") center/cover;
    box-shadow: 0 20px 60px rgba(0,0,0,.22);
}

.hero-content {
    max-width: 720px;
    position: relative;
    z-index: 2;
}

.hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .42rem .78rem;
    border-radius: 999px;
    background: rgba(77,163,255,.12);
    border: 1px solid rgba(77,163,255,.28);
    color: #77c2ff;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
}

.hero h1 {
    margin: .9rem 0 .55rem;
    color: white;
    font-size: clamp(2rem, 5vw, 3.55rem);
    line-height: 1.05;
    letter-spacing: -.04em;
}

.hero p {
    margin: 0;
    max-width: 650px;
    color: #a9bfd5;
    font-size: clamp(.88rem, 2vw, 1rem);
    line-height: 1.7;
}

/* Section heading */
.section-title {
    display: flex;
    align-items: center;
    gap: .65rem;
    margin: 1.6rem 0 .8rem;
    color: #edf6ff;
    font-size: 1.02rem;
    font-weight: 750;
}

.section-title .icon {
    width: 32px;
    height: 32px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: rgba(77,163,255,.1);
    border: 1px solid rgba(77,163,255,.2);
}

/* Cards */
.result-card {
    background: linear-gradient(180deg, rgba(14,31,51,.82), rgba(9,23,39,.82));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    min-height: 120px;
}

.info-strip {
    display: flex;
    align-items: center;
    gap: .7rem;
    padding: .85rem 1rem;
    margin: .6rem 0 1rem;
    background: rgba(77,163,255,.055);
    border: 1px solid rgba(77,163,255,.14);
    border-radius: 12px;
    color: #9fc2df;
    font-size: .8rem;
}

/* Metrics */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .8rem;
    margin: 1.25rem 0;
}

.metric {
    padding: 1rem;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: rgba(13,29,48,.72);
    text-align: center;
}

.metric-value {
    color: #67b8ff;
    font-size: 1.45rem;
    font-weight: 800;
}

.metric-label {
    color: #7e9bb5;
    font-size: .68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-top: .25rem;
}

/* Markdown result text */
.stMarkdown {
    color: #c9dced;
}

.stMarkdown p,
.stMarkdown li,
.stMarkdown td,
.stMarkdown th {
    color: #c9dced;
    line-height: 1.7;
}

.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {
    color: #edf6ff !important;
}

/* Approval */
.approval-card {
    padding: 1rem 1.1rem;
    border: 1px solid rgba(242,177,75,.2);
    border-radius: 14px;
    background: rgba(242,177,75,.045);
}

/* Divider */
hr {
    border-color: rgba(116,164,214,.13) !important;
}

/* Mobile */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem .8rem 3rem;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1rem .8rem;
    }

    .hero {
        min-height: 265px;
        padding: 1.5rem;
        border-radius: 18px;
        background:
            linear-gradient(180deg, rgba(4,13,25,.88), rgba(6,22,40,.96)),
            url("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1000&q=80") center/cover;
    }

    .hero h1 {
        font-size: 2rem;
    }

    .hero p {
        font-size: .86rem;
    }

    .metric-grid {
        grid-template-columns: 1fr;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100% !important;
    }
}

@media (max-width: 480px) {
    .hero {
        min-height: 300px;
        padding: 1.15rem;
    }

    .hero h1 {
        font-size: 1.75rem;
    }

    .hero-kicker {
        font-size: .62rem;
    }

    .section-title {
        font-size: .94rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# Same controls / same state logic.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">✈️</div>
        <div>
            <div class="sidebar-brand-title">AI Travel Planner</div>
            <div class="sidebar-brand-sub">Multi-Agent Travel Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Session</div>', unsafe_allow_html=True)

    user_id = st.text_input("User ID", value="demo_user")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"

    if st.button("New Thread"):
        st.session_state.thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        st.session_state.pop("waiting_for_approval", None)
        st.session_state.pop("latest_result", None)

    st.markdown(
        f'<div class="thread-box">Thread ID<br><strong>{st.session_state.thread_id}</strong></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Powered by</div>', unsafe_allow_html=True)

    for tech in [
        "🔗 LangGraph",
        "🧠 Groq · LLaMA 3.3 70B",
        "🐘 PostgreSQL",
        "🔍 Tavily Search",
        "✈️ AviationStack",
    ]:
        st.markdown(f'<div class="sidebar-chip">{tech}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Agent Pipeline</div>', unsafe_allow_html=True)

    for step in [
        "① Flight Agent",
        "② Hotel Agent",
        "③ Weather / Budget",
        "④ Itinerary Agent",
        "⑤ Final Response",
    ]:
        st.markdown(f'<div class="sidebar-chip">{step}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-content">
        <div class="hero-kicker">✦ Multi-Agent AI System</div>
        <h1>Plan your next journey with AI.</h1>
        <p>
            Your travel request is handled by specialized agents for flights,
            hotels, weather, budget and itinerary planning — then combined into
            one final travel plan.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TRAVEL REQUEST
# Same query widget and same behavior.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-title">
    <span class="icon">🗺️</span>
    <span>Tell us about your trip</span>
</div>
""", unsafe_allow_html=True)

query = st.text_area(
    "Travel request",
    placeholder="Plan a 7-day Japan trip under Rs. 2 lakh. I prefer budget hotels and no overnight flights.",
    height=110,
)

config = {"configurable": {"thread_id": st.session_state.thread_id}}

if st.button("✈️  Create Draft Plan", type="primary"):
    if not query.strip():
        st.warning("Enter a travel request first.")
    else:
        with st.spinner("Agents are planning..."):
            result = app.invoke(
                {
                    "messages": [HumanMessage(content=query)],
                    "user_id": user_id,
                    "user_query": query,
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "budget_results": "",
                    "itinerary": "",
                    "final_response": "",
                    "llm_calls": 0,
                },
                config=config,
            )

        st.session_state.latest_result = result
        st.session_state.waiting_for_approval = "__interrupt__" in result


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# Same result/state logic.
# ─────────────────────────────────────────────────────────────────────────────
result = st.session_state.get("latest_result")

if result:
    st.markdown("""
    <div class="section-title">
        <span class="icon">🧭</span>
        <span>Travel Intelligence</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="info-strip">🧠 <strong>Supervisor:</strong>&nbsp; '
        f'{result.get("supervisor_reasoning", "")}</div>',
        unsafe_allow_html=True,
    )

    selected = result.get("selected_agents", [])
    if selected:
        st.markdown(
            f'<div class="info-strip">⚙️ <strong>Selected agents:</strong>&nbsp; '
            f'{", ".join(map(str, selected))}</div>',
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title"><span class="icon">✈️</span><span>Flights</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result.get("flight_results", ""))

        st.markdown(
            '<div class="section-title"><span class="icon">🌤️</span><span>Weather</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result.get("weather_results", ""))

    with col2:
        st.markdown(
            '<div class="section-title"><span class="icon">🏨</span><span>Hotels</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result.get("hotel_results", ""))

        st.markdown(
            '<div class="section-title"><span class="icon">💰</span><span>Budget</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(result.get("budget_results", ""))

    st.markdown(
        '<div class="section-title"><span class="icon">🗓️</span><span>Draft Itinerary</span></div>',
        unsafe_allow_html=True,
    )

    if "__interrupt__" in result:
        draft = result["__interrupt__"][0].value.get("draft_itinerary", "")
    else:
        draft = result.get("itinerary", "")

    st.markdown(draft)


# ─────────────────────────────────────────────────────────────────────────────
# HUMAN APPROVAL
# Same approval logic.
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.get("waiting_for_approval"):
    st.divider()

    st.markdown("""
    <div class="section-title">
        <span class="icon">🤝</span>
        <span>Human Approval</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="approval-card">Review the draft itinerary above and '
        'approve it or request a revision.</div>',
        unsafe_allow_html=True,
    )

    approved = st.radio(
        "Approve this draft?",
        ["Yes", "No, revise it"],
        horizontal=True,
    )

    feedback = st.text_area("Feedback", disabled=approved == "Yes")

    if st.button("Submit Approval"):
        with st.spinner("Creating final response..."):
            final_result = app.invoke(
                Command(
                    resume={
                        "approved": approved == "Yes",
                        "feedback": feedback,
                    }
                ),
                config=config,
            )

        st.session_state.latest_result = final_result
        st.session_state.waiting_for_approval = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# FINAL RESPONSE
# Same final-response logic.
# ─────────────────────────────────────────────────────────────────────────────
final_result = st.session_state.get("latest_result")

if final_result and final_result.get("final_response"):
    st.divider()

    st.markdown("""
    <div class="section-title">
        <span class="icon">✨</span>
        <span>Final Travel Plan</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True,
    )
    st.markdown(final_result["final_response"])
    st.markdown('</div>', unsafe_allow_html=True)
