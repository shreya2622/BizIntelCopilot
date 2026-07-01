"""
BizIntel Copilot — Streamlit Chat UI
"""

import os
import sys

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv()

from agent.sql_agent import run_sql_agent
from charts.chart_builder import build_chart
from rag.retriever import retrieve

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BizIntel Copilot",
    page_icon=None,
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Hero header */
.hero {
    text-align: center;
    padding: 48px 0 32px 0;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.hero p {
    color: #94a3b8;
    font-size: 1.05rem;
    margin: 0;
}

/* Stat pills */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin-bottom: 32px;
    flex-wrap: wrap;
}
.stat-pill {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 13px;
    color: #cbd5e1;
    backdrop-filter: blur(8px);
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    margin-bottom: 12px !important;
    backdrop-filter: blur(8px);
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #e2e8f0 !important;
}

/* SQL block */
.sql-box {
    background: rgba(15, 12, 41, 0.8);
    border-left: 3px solid #a78bfa;
    padding: 14px 18px;
    border-radius: 10px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #c4b5fd;
    white-space: pre-wrap;
    margin-top: 8px;
    line-height: 1.6;
}

/* Source tags */
.source-tag {
    display: inline-block;
    background: rgba(96, 165, 250, 0.15);
    color: #93c5fd;
    border: 1px solid rgba(96, 165, 250, 0.3);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    margin: 2px 4px;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: white !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton button {
    background: rgba(167, 139, 250, 0.1) !important;
    border: 1px solid rgba(167, 139, 250, 0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 13px !important;
    text-align: left !important;
    transition: all 0.2s ease;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(167, 139, 250, 0.25) !important;
    border-color: rgba(167, 139, 250, 0.5) !important;
    transform: translateX(3px);
}

/* Clear button */
.clear-btn button {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    color: #fca5a5 !important;
    border-radius: 10px !important;
}
.clear-btn button:hover {
    background: rgba(239, 68, 68, 0.2) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Section labels */
.section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #64748b;
    margin: 16px 0 8px 0;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 4px 0;">
        <div style="font-size:22px; font-weight:700; background: linear-gradient(90deg,#a78bfa,#60a5fa);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            BizIntel Copilot
        </div>
        <div style="font-size:12px; color:#64748b; margin-top:4px;">
            Natural language BI assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-label">Try asking</div>', unsafe_allow_html=True)

    suggestions = [
        "Total sales by region",
        "Most profitable product category",
        "Monthly revenue trends for 2017",
        "Top 10 customers by sales",
        "States with negative profit",
        "Average discount by segment",
    ]
    for q in suggestions:
        if st.button(q, use_container_width=True):
            st.session_state.pending_question = q

    st.divider()
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("pending_question", None)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute; bottom:20px; left:0; right:0; text-align:center;
         font-size:11px; color:#334155;">
        Powered by Groq · LangChain · DuckDB
    </div>
    """, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

db_ok = os.path.exists(os.path.join(os.path.dirname(__file__), "superstore.db"))

# ── Hero header ────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <h1>BizIntel Copilot</h1>
        <p>Ask questions about your business data in plain English.<br>
        Get instant SQL, tables, and charts — no coding needed.</p>
    </div>
    <div class="stats-row">
        <div class="stat-pill">9,994 orders</div>
        <div class="stat-pill">4 US regions</div>
        <div class="stat-pill">3 product categories</div>
        <div class="stat-pill">2014 – 2017</div>
    </div>
    """, unsafe_allow_html=True)

# ── Conversation history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sql") and msg.get("show_sql"):
            st.markdown(f'<div class="sql-box">{msg["sql"]}</div>', unsafe_allow_html=True)
        if msg.get("dataframe") is not None:
            st.dataframe(msg["dataframe"], use_container_width=True)
        if msg.get("figure"):
            st.plotly_chart(msg["figure"], use_container_width=True)
        if msg.get("sources"):
            src_html = "".join(f'<span class="source-tag">{s}</span>' for s in msg["sources"])
            st.markdown(f"**Sources:** {src_html}", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
pending = st.session_state.pop("pending_question", None)
user_input = st.chat_input("Ask a business question…") or pending

if user_input:
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found. Add it to your .env file.")
        st.stop()

    if not db_ok:
        st.error("Database not found. Run: python data/load_data.py --csv superstore.csv")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    rag_context, sources = retrieve(user_input)

    with st.spinner("Generating SQL and fetching results…"):
        sql, df, error = run_sql_agent(user_input, rag_context=rag_context)

    with st.chat_message("assistant"):
        if error:
            content = f"Sorry, I couldn't execute that query.\n\n**Error:** `{error}`"
            st.markdown(content)
            st.markdown(f'<div class="sql-box">{sql}</div>', unsafe_allow_html=True)
            st.session_state.messages.append(
                {"role": "assistant", "content": content, "sql": sql, "show_sql": True}
            )
        else:
            row_count = len(df)
            content = f"Here are the results — **{row_count} row{'s' if row_count != 1 else ''}** returned."
            st.markdown(content)

            show_sql = st.toggle("Show SQL", value=False, key=f"sql_{len(st.session_state.messages)}")
            if show_sql:
                st.markdown(f'<div class="sql-box">{sql}</div>', unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True)

            fig = build_chart(user_input, df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            if sources:
                src_html = "".join(f'<span class="source-tag">{s}</span>' for s in sources)
                st.markdown(f"**RAG Sources:** {src_html}", unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
                "sql": sql,
                "show_sql": show_sql,
                "dataframe": df,
                "figure": fig,
                "sources": sources,
            })
