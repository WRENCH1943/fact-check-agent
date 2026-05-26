import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="FactLens — AI Fact Checker",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap');

*, *::before, *::after {
    box-sizing: border-box;
}

#MainMenu, footer, header { visibility: hidden; }

html, body, .stApp {
    background: #08090c !important;
    color: #e8e6e1;
    font-family: 'DM Mono', monospace;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif;
    letter-spacing: -0.02em;
}

/* ── NOISE OVERLAY ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

/* ── HERO ── */
.hero-wrap {
    padding: 72px 0 56px;
    text-align: center;
    position: relative;
}

.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #5eead4;
    margin-bottom: 20px;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.6rem, 6vw, 4.2rem);
    font-weight: 800;
    line-height: 1.05;
    color: #f5f3ee;
    margin: 0 0 20px;
    letter-spacing: -0.035em;
}

.hero-title span {
    color: #5eead4;
}

.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    color: #6b7280;
    line-height: 1.8;
    max-width: 460px;
    margin: 0 auto;
    font-style: italic;
}

.hero-line {
    width: 1px;
    height: 48px;
    background: linear-gradient(to bottom, #5eead4, transparent);
    margin: 36px auto 0;
}

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    background: #0d0f14 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 4px !important;
    padding: 40px 24px !important;
    transition: border-color 0.2s ease, background 0.2s ease;
    position: relative;
}

[data-testid="stFileUploader"]:hover {
    border-color: #5eead4 !important;
    background: #0a0f12 !important;
}

[data-testid="stFileUploader"] label {
    color: #6b7280 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #5eead4 !important;
    color: #08090c !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 14px 32px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: #99f6e4 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(94, 234, 212, 0.18) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── STATUS / SPINNER ── */
[data-testid="stStatusWidget"] {
    background: #0d0f14 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── SECTION HEADERS ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #374151;
    margin: 48px 0 4px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2330;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f5f3ee;
    margin: 0 0 32px;
    letter-spacing: -0.02em;
}

/* ── CLAIM CARDS ── */
.claim-card {
    background: #0d0f14;
    border: 1px solid #1e2330;
    border-radius: 4px;
    padding: 28px 32px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease;
}

.claim-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
}

.claim-card:hover {
    border-color: #2d3748;
}

/* Status variants */
.status-verified { border-color: #064e3b22; }
.status-verified::before { background: #5eead4; }
.status-verified:hover { border-color: #5eead444; }

.status-false { border-color: #7f1d1d22; }
.status-false::before { background: #f87171; }
.status-false:hover { border-color: #f8717144; }

.status-inaccurate { border-color: #78350f22; }
.status-inaccurate::before { background: #fbbf24; }
.status-inaccurate:hover { border-color: #fbbf2444; }

.status-unverifiable { border-color: #1e2330; }
.status-unverifiable::before { background: #4b5563; }

/* Card internals */
.card-index {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    color: #374151;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.card-claim {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f5f3ee;
    line-height: 1.45;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}

.card-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}

.badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 2px;
    font-weight: 400;
}

.badge-category {
    background: #111827;
    border: 1px solid #1e2330;
    color: #6b7280;
}

.badge-verified  { background: #022c22; color: #5eead4; border: 1px solid #064e3b; }
.badge-false     { background: #1c0808; color: #f87171; border: 1px solid #7f1d1d; }
.badge-inaccurate{ background: #1c1008; color: #fbbf24; border: 1px solid #78350f; }
.badge-unverifiable { background: #111827; color: #6b7280; border: 1px solid #1e2330; }

.card-divider {
    height: 1px;
    background: #1e2330;
    margin: 18px 0;
}

.card-result {
    font-family: 'DM Mono', monospace;
    font-size: 12.5px;
    line-height: 1.85;
    color: #9ca3af;
    font-style: italic;
}

/* ── SUMMARY GRID ── */
.summary-section {
    margin-top: 56px;
    padding-top: 40px;
    border-top: 1px solid #1e2330;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
    margin-top: 24px;
    background: #1e2330;
    border: 1px solid #1e2330;
    border-radius: 4px;
    overflow: hidden;
}

.metric-tile {
    background: #0d0f14;
    padding: 32px 24px;
    text-align: center;
}

.metric-num {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.04em;
    margin-bottom: 10px;
}

.metric-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #374151;
}

.c-teal   { color: #5eead4; }
.c-red    { color: #f87171; }
.c-amber  { color: #fbbf24; }
.c-slate  { color: #4b5563; }

/* ── DIVIDER ── */
.fancy-divider {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 40px 0;
    color: #1e2330;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
}

.fancy-divider::before,
.fancy-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2330;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #0d0f14 !important;
    border: 1px solid #1e2330 !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] > div {
    color: #5eead4 !important;
}

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
    .summary-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-title { font-size: 2.2rem; }
}

</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_status_info(result: str) -> tuple[str, str, str, str]:
    """Return (status_class, badge_class, badge_label, icon) for a result."""
    upper = result.upper()
    if "VERIFIED" in upper:
        return "status-verified", "badge-verified", "Verified", "✦"
    elif "FALSE" in upper:
        return "status-false", "badge-false", "False", "✕"
    elif "INACCURATE" in upper:
        return "status-inaccurate", "badge-inaccurate", "Inaccurate", "△"
    else:
        return "status-unverifiable", "badge-unverifiable", "Unverifiable", "○"


def render_claim_card(index: int, claim_text: str, category: str, result_text: str, status_class: str, badge_class: str, badge_label: str, icon: str):
    import html
    safe_claim  = html.escape(claim_text)
    safe_cat    = html.escape(category)
    safe_result = html.escape(result_text)

    st.markdown(f"""
    <div class="claim-card {status_class}">
        <div class="card-index">Claim {index:02d}</div>
        <div class="card-claim">{safe_claim}</div>
        <div class="card-meta">
            <span class="badge badge-category">⊞ {safe_cat}</span>
            <span class="badge {badge_class}">{icon} {badge_label}</span>
        </div>
        <div class="card-divider"></div>
        <div class="card-result">{safe_result}</div>
    </div>
    """, unsafe_allow_html=True)


def render_summary(verified: int, false: int, inaccurate: int, unverifiable: int):
    st.markdown(f"""
    <div class="summary-grid">
        <div class="metric-tile">
            <div class="metric-num c-teal">{verified}</div>
            <div class="metric-lbl">Verified</div>
        </div>
        <div class="metric-tile">
            <div class="metric-num c-red">{false}</div>
            <div class="metric-lbl">False</div>
        </div>
        <div class="metric-tile">
            <div class="metric-num c-amber">{inaccurate}</div>
            <div class="metric-lbl">Inaccurate</div>
        </div>
        <div class="metric-tile">
            <div class="metric-num c-slate">{unverifiable}</div>
            <div class="metric-lbl">Unverifiable</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">— AI-Powered Fact Verification —</div>
    <h1 class="hero-title">Fact<span>Lens</span></h1>
    <p class="hero-sub">
        Upload any PDF document.<br>
        Extract every factual claim.<br>
        Verify each one against the live web.
    </p>
    <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)


# ── Upload ────────────────────────────────────────────────────────────────────

uploaded_file = st.file_uploader(
    "Drop a PDF here or click to browse",
    type=["pdf"],
    label_visibility="collapsed"
)

if uploaded_file:

    st.markdown(f"""
    <div style="
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.1em;
        color: #5eead4;
        margin: 12px 0 20px;
        padding: 10px 16px;
        background: #022c22;
        border: 1px solid #064e3b;
        border-radius: 2px;
    ">
        ✓ &nbsp;{uploaded_file.name}
    </div>
    """, unsafe_allow_html=True)

    if st.button("RUN FACT CHECK →", use_container_width=True):

        with st.status("Working…", expanded=True) as status:

            st.write("Extracting text from PDF…")
            text = extract_text_from_pdf(uploaded_file)

            if not text.strip():
                st.error("Could not extract text from this PDF.")
                st.stop()

            st.write("Identifying factual claims…")
            claims = extract_claims(text)

            if not claims:
                st.warning("No verifiable factual claims were found in this document.")
                st.stop()

            status.update(
                label=f"Found {len(claims)} claims — beginning verification",
                state="complete",
                expanded=False
            )

        # ── Claims header
        st.markdown(f"""
        <div class="section-label">Results</div>
        <div class="section-title">{len(claims)} Claims Identified</div>
        """, unsafe_allow_html=True)

        # ── Per-claim verification
        verified_count    = 0
        false_count       = 0
        inaccurate_count  = 0
        unverifiable_count = 0

        for index, claim in enumerate(claims, start=1):

            with st.spinner(f"Verifying claim {index} of {len(claims)}…"):
                result = verify_claim(claim["claim"])

            status_class, badge_class, badge_label, icon = get_status_info(result)

            if badge_label == "Verified":
                verified_count += 1
            elif badge_label == "False":
                false_count += 1
            elif badge_label == "Inaccurate":
                inaccurate_count += 1
            else:
                unverifiable_count += 1

            render_claim_card(
                index=index,
                claim_text=claim["claim"],
                category=claim["category"],
                result_text=result,
                status_class=status_class,
                badge_class=badge_class,
                badge_label=badge_label,
                icon=icon,
            )

        # ── Summary
        st.markdown("""
        <div class="summary-section">
            <div class="section-label">Summary</div>
            <div class="section-title">Verification Overview</div>
        </div>
        """, unsafe_allow_html=True)

        render_summary(
            verified_count,
            false_count,
            inaccurate_count,
            unverifiable_count,
        )

        st.markdown("""
        <div style="
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 0.16em;
            color: #1e2330;
            text-align: center;
            margin-top: 48px;
            text-transform: uppercase;
        ">
            FactLens — Powered by Claude & Live Web Search
        </div>
        """, unsafe_allow_html=True)

else:

    st.markdown("""
    <div style="
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.1em;
        color: #374151;
        text-align: center;
        margin-top: 20px;
        font-style: italic;
    ">
        Supports text-based PDF documents
    </div>
    """, unsafe_allow_html=True)
