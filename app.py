import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from retrieval import Stratum

# ─── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Stratum — Enterprise Intelligence",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    background-color: #0a0a0f !important;
    color: #ccccee !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background-color: #0d0d1a !important;
    border-right: 1px solid #1e1e2e !important;
}
[data-testid="stSidebar"] * {
    font-family: 'JetBrains Mono', monospace !important;
    color: #8888aa !important;
}

.sidebar-brand {
    font-size: 18px;
    font-weight: 700;
    color: #7c6af7 !important;
    letter-spacing: 0.15em;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 1rem;
}

.section-label {
    font-size: 10px;
    color: #4a4a6a !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 1rem 0 0.4rem 0;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    padding: 3px 0;
    border-bottom: 1px solid #16162a;
    color: #6666aa;
}
.stat-val { color: #7c6af7; }

.topbar {
    background: #0d0d1a;
    border-bottom: 1px solid #1e1e2e;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
}
.topbar-brand {
    font-size: 16px;
    font-weight: 700;
    color: #7c6af7;
    letter-spacing: 0.15em;
}
.online-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #3ecf8e;
    margin-right: 5px;
}

.answer-card {
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 12px 0;
    font-size: 13px;
    line-height: 1.8;
    color: #aaaacc;
}
.answer-header {
    font-size: 10px;
    color: #3ecf8e;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 10px;
    color: #6666aa;
    margin: 3px;
    font-family: monospace;
}
.source-co { color: #7c6af7; font-weight: 700; }
.source-pg { color: #3ecf8e; }

.conf-wrap {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid #1e1e2e;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 10px;
    color: #4a4a6a;
}
.conf-track {
    flex: 1;
    height: 3px;
    background: #1e1e2e;
    border-radius: 2px;
    overflow: hidden;
}

.stTextInput input {
    background: #0d0d1a !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 6px !important;
    color: #ccccee !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 1px #7c6af7 !important;
}

.stButton button {
    background: #7c6af7 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 10px 24px !important;
    width: 100% !important;
}
.stButton button:hover { background: #6a58e0 !important; }

[data-testid="stMultiSelect"] > div {
    background: #0d0d1a !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 6px !important;
}
[data-testid="stMultiSelect"] span {
    background: #1a1a3a !important;
    color: #7c6af7 !important;
    font-size: 11px !important;
}

.history-item {
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 11px;
    color: #6666aa;
    line-height: 1.5;
}

.warn-box {
    background: #1a1200;
    border: 1px solid #3a2800;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 11px;
    color: #aa8800;
    margin: 8px 0;
}

.mono-divider {
    border: none;
    border-top: 1px solid #1e1e2e;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Session state ─────────────────────────────────────────────────────────────

if "stratum" not in st.session_state:
    with st.spinner("// loading stratum engine..."):
        st.session_state.stratum = Stratum(chroma_path="./stratum_db")

if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "query" not in st.session_state:
    st.session_state.query = ""

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-brand">STR<span style="color:#3ecf8e">A</span>TUM</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Companies</div>', unsafe_allow_html=True)
    companies = st.multiselect(
        label="companies",
        options=["NVIDIA", "Google", "IBM", "Oracle", "Microsoft", "Meta"],
        default=["NVIDIA", "Google"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label">Domain</div>', unsafe_allow_html=True)
    domains = st.multiselect(
        label="domains",
        options=["financial", "technical", "hr", "strategy", "news"],
        default=["financial"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label">Year range</div>', unsafe_allow_html=True)
    year_range = st.slider(
        label="year range",
        min_value=2022,
        max_value=2025,
        value=(2022, 2025),
        label_visibility="collapsed",
    )

    st.markdown('<div class="section-label">Index stats</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="stat-row"><span>total chunks</span><span class="stat-val">4,907</span></div>
    <div class="stat-row"><span>companies</span><span class="stat-val">NVIDIA · Google</span></div>
    <div class="stat-row"><span>years</span><span class="stat-val">2022 – 2025</span></div>
    <div class="stat-row"><span>model</span><span class="stat-val" style="color:#3ecf8e">gemma3:4b</span></div>    <div class="stat-row"><span>retrieval</span><span class="stat-val">hybrid BM25+vec</span></div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown('<div class="section-label" style="margin-top:1.5rem">Recent queries</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f'<div class="history-item">{h}</div>', unsafe_allow_html=True)

# ─── Top bar ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="topbar">
    <div class="topbar-brand">STRATUM
        <span style="color:#4a4a6a;font-size:12px;font-weight:400"> / enterprise intelligence</span>
    </div>
    <div style="display:flex;align-items:center;gap:20px;font-size:11px;color:#4a4a6a">
        <span>NVIDIA · Google · 2022–2025</span>
        <span><span class="online-dot"></span><span style="color:#3ecf8e">gemma3:4b online</span></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Query area ───────────────────────────────────────────────────────────────

st.markdown("<div style='padding: 20px 24px 0 24px;'>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    query_input = st.text_input(
        label="query",
        value=st.session_state.query,
        placeholder="query:// e.g. Compare NVIDIA and Google R&D spending 2023-2025",
        label_visibility="collapsed",
    )
with col2:
    run = st.button("RUN ▶")

suggested = [
    "Total revenue and R&D expenses for NVIDIA and Alphabet 2023 and 2024 with R&D as percentage of revenue",
    "What is NVIDIA total revenue and R&D expenses for 2023 2024 and 2025?",
    "What is Alphabet total revenue and R&D expenses for 2022 2023 and 2024?",
    "What risks does NVIDIA highlight in their 2025 annual report?",
    "What is Alphabet cloud strategy in 2024?",
]

st.markdown("<div style='font-size:10px;color:#4a4a6a;font-family:monospace;margin:8px 0 4px 0'>suggested://</div>", unsafe_allow_html=True)
sug_cols = st.columns(len(suggested))
for i, sug in enumerate(suggested):
    with sug_cols[i]:
        if st.button(sug[:28] + "…", key=f"sug_{i}"):
            st.session_state.query = sug
            st.rerun()

st.markdown("<hr class='mono-divider'>", unsafe_allow_html=True)

# ─── Run query ────────────────────────────────────────────────────────────────

active_query = query_input.strip() or st.session_state.query.strip()

if run and active_query:
    if not companies:
        st.markdown('<div class="warn-box">// error: select at least one company from the sidebar.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("// querying stratum_db · hybrid BM25+semantic · generating answer..."):
            result = st.session_state.stratum.query(
                question=active_query,
                companies=companies,
                domains=domains if domains else None,
                year_range=tuple(year_range),
            )
            st.session_state.result = result
            if active_query not in st.session_state.history:
                st.session_state.history.append(active_query)

# ─── Render result ────────────────────────────────────────────────────────────

if st.session_state.result:
    result     = st.session_state.result
    confidence = result.get("confidence", 0)
    conf_pct   = int(confidence * 100)
    conf_color = (
        "#3ecf8e" if confidence > 0.6 else
        "#f7a26a" if confidence > 0.4 else
        "#f76a6a"
    )

    # Answer header
    st.markdown(
        '<div class="answer-header">// STRATUM RESPONSE</div>',
        unsafe_allow_html=True,
    )

    # Open answer card
    st.markdown('<div class="answer-card">', unsafe_allow_html=True)

    # Answer body — rendered as markdown so tables format correctly
    st.markdown(result["answer"])

    # Confidence bar — closes the answer card
    st.markdown(f"""
        <div class="conf-wrap">
            <span>confidence</span>
            <div class="conf-track">
                <div style="height:100%;width:{conf_pct}%;background:{conf_color};border-radius:2px;"></div>
            </div>
            <span style="color:{conf_color}">{confidence:.3f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Low confidence warning
    if result.get("confidence_flag"):
        st.markdown(
            '<div class="warn-box">// low confidence — try broadening year range or domain filter.</div>',
            unsafe_allow_html=True,
        )

    # Sources
    if result.get("citations"):
        st.markdown(
            '<div class="answer-header" style="margin-top:18px">// SOURCES</div>',
            unsafe_allow_html=True,
        )
        chips = ""
        for c in result["citations"]:
            chips += f"""<span class="source-chip">
                <span class="source-co">{c['company'].upper()}</span>
                {c['source']}
                <span class="source-pg">p.{c['page']}</span>
                <span style="color:#3a3a5a">· {c['score']}</span>
            </span>"""
        st.markdown(
            f"<div style='margin-bottom:14px'>{chips}</div>",
            unsafe_allow_html=True,
        )

    # Query metadata
    q_short       = result["question"][:80] + ("…" if len(result["question"]) > 80 else "")
    companies_str = ", ".join(result["companies"])
    domains_str   = ", ".join(result["domains"])
    st.markdown(f"""
    <div style="font-size:10px;color:#3a3a5a;font-family:monospace;padding:4px 0 16px 0;">
        query: "{q_short}" &nbsp;|&nbsp;
        companies: {companies_str} &nbsp;|&nbsp;
        domains: {domains_str} &nbsp;|&nbsp;
        sources: {len(result.get("citations", []))}
    </div>
    """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center;padding:80px 20px;">
        <div style="font-size:52px;color:#1e1e2e;font-family:monospace">▲</div>
        <div style="font-size:13px;color:#3a3a5a;font-family:monospace;margin-top:16px">
            stratum is ready // enter a query above or pick a suggested one
        </div>
        <div style="font-size:11px;color:#2a2a4a;font-family:monospace;margin-top:8px">
            4,842 chunks · NVIDIA &amp; Google · 2022–2025 · hybrid BM25 + semantic retrieval
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)