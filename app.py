import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="AI Fact-Check Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800&display=swap');

    /* ── Base Overrides ── */
    .stApp {
        background: #07070d;
        color: #e2e8f0;
    }
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
        color: #e2e8f0;
    }
    p, span, div, li, label {
        color: #cbd5e1 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        color: #f1f5f9 !important;
    }

    /* ── Hide Default Elements ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    .stDeployButton { display: none !important; }

    /* ── Background Mesh ── */
    .main::before {
        content: '';
        position: fixed;
        top: -200px;
        right: -200px;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(79,70,229,0.10) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    .main::after {
        content: '';
        position: fixed;
        bottom: -150px;
        left: -150px;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    .main {
        background: transparent !important;
        padding-top: 1.5rem;
        position: relative;
        z-index: 1;
    }

    /* ── Grid Background ── */
    .bg-grid {
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── Title ── */
    .hero-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        background: linear-gradient(135deg, #6366f1, #06b6d4, #a78bfa);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.3rem !important;
        letter-spacing: -1px;
        line-height: 1.15;
    }
    .hero-subtitle {
        text-align: center !important;
        color: #64748b !important;
        font-size: 1rem !important;
        font-weight: 400 !important;
        margin-bottom: 2.5rem !important;
        letter-spacing: 0.2px;
    }

    /* ── Badge Pill ── */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 50px;
        background: rgba(99,102,241,0.08);
        border: 1px solid rgba(99,102,241,0.18);
        font-size: 0.78rem;
        font-weight: 500;
        color: #a5b4fc;
        margin-bottom: 1.2rem;
        letter-spacing: 0.5px;
    }

    /* ── Glass Card ── */
    .glass-card {
        padding: 1.5rem;
        border-radius: 16px;
        background: rgba(15,15,30,0.65);
        border: 1px solid rgba(99,102,241,0.12);
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), rgba(6,182,212,0.2), transparent);
    }

    /* ── Claim Box ── */
    .claim-box {
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        background: rgba(15,15,30,0.55);
        border: 1px solid rgba(99,102,241,0.10);
        margin-bottom: 0.8rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.18);
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s;
    }
    .claim-box:hover {
        border-color: rgba(99,102,241,0.25);
    }
    .claim-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, #6366f1, #06b6d4);
        border-radius: 0 2px 2px 0;
    }
    .claim-number {
        font-family: 'Poppins', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #6366f1;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .claim-number .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #6366f1;
        box-shadow: 0 0 8px rgba(99,102,241,0.5);
        display: inline-block;
    }
    .claim-text {
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
        font-weight: 400;
        padding-left: 12px;
    }

    /* ── Upload Area ── */
    .upload-zone {
        padding: 2.5rem 2rem;
        border-radius: 20px;
        border: 2px dashed rgba(99,102,241,0.2);
        background: rgba(15,15,30,0.4);
        text-align: center;
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    .upload-zone::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at center, rgba(99,102,241,0.04), transparent 70%);
        pointer-events: none;
    }
    .upload-zone:hover {
        border-color: rgba(99,102,241,0.4);
        background: rgba(99,102,241,0.03);
    }
    .upload-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        display: block;
        filter: drop-shadow(0 0 12px rgba(99,102,241,0.3));
    }
    .upload-label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    .upload-hint {
        color: #475569 !important;
        font-size: 0.75rem !important;
        margin-top: 0.4rem;
    }

    /* ── Metric Cards ── */
    .metric-card {
        padding: 1rem 1.4rem;
        border-radius: 12px;
        background: rgba(15,15,30,0.5);
        border: 1px solid rgba(99,102,241,0.10);
        backdrop-filter: blur(10px);
    }
    .metric-label {
        font-size: 0.7rem !important;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #64748b !important;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0 !important;
    }

    /* ── Verify Button ── */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px;
        box-shadow: 0 4px 20px rgba(79,70,229,0.35), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        transition: all 0.3s !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
        box-shadow: 0 6px 28px rgba(79,70,229,0.5), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        transform: translateY(-1px);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── File Uploader Override ── */
    section[data-testid="stFileUploader"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    section[data-testid="stFileUploader"] button {
        background: transparent !important;
        border: none !important;
        color: #a5b4fc !important;
    }
    section[data-testid="stFileUploader"] .st-emotion-cache-1lbeksd {
        background: transparent !important;
    }

    /* ── Success / Error / Warning / Info ── */
    .stSuccess {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.2) !important;
        border-radius: 12px !important;
        color: #6ee7b7 !important;
        backdrop-filter: blur(10px);
    }
    .stError {
        background: rgba(239,68,68,0.08) !important;
        border: 1px solid rgba(239,68,68,0.2) !important;
        border-radius: 12px !important;
        color: #fca5a5 !important;
        backdrop-filter: blur(10px);
    }
    .stWarning {
        background: rgba(245,158,11,0.08) !important;
        border: 1px solid rgba(245,158,11,0.2) !important;
        border-radius: 12px !important;
        color: #fcd34d !important;
        backdrop-filter: blur(10px);
    }
    .stInfo {
        background: rgba(99,102,241,0.08) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 12px !important;
        color: #a5b4fc !important;
        backdrop-filter: blur(10px);
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.15), transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(10,10,18,0.95) !important;
        border-right: 1px solid rgba(99,102,241,0.10) !important;
        backdrop-filter: blur(20px);
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Poppins', sans-serif !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.85rem !important;
        line-height: 1.7 !important;
    }

    /* ── Sidebar Logo ── */
    .sidebar-logo {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    .sidebar-tagline {
        text-align: center;
        font-size: 0.72rem !important;
        color: #475569 !important;
        margin-bottom: 1.8rem;
        letter-spacing: 0.5px;
    }

    /* ── Sidebar Section ── */
    .sidebar-section {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(99,102,241,0.04);
        border: 1px solid rgba(99,102,241,0.08);
        margin-bottom: 1rem;
    }
    .sidebar-section-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        color: #6366f1 !important;
        margin-bottom: 0.7rem !important;
    }
    .sidebar-feature {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.45rem;
        font-size: 0.82rem !important;
        color: #94a3b8 !important;
    }
    .sidebar-feature .icon {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.6rem;
        flex-shrink: 0;
    }
    .sidebar-tech-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.4rem;
        font-size: 0.82rem !important;
        color: #64748b !important;
    }
    .sidebar-tech-item .tech-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* ── Footer ── */
    .footer-bar {
        text-align: center;
        color: #334155 !important;
        font-size: 0.78rem !important;
        margin-top: 3rem;
        padding: 1rem 0;
        letter-spacing: 0.3px;
    }
    .footer-bar .name {
        color: #6366f1 !important;
        font-weight: 600;
    }

    /* ── Claims Count Badge ── */
    .claims-count-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 8px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.15);
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 1.5rem;
    }

    /* ── Section Header ── */
    .section-header {
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.35); }
    </style>

    <div class="bg-grid"></div>
    """,
    unsafe_allow_html=True
)


# ──────────────────────── SIDEBAR ────────────────────────

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">🔎 FactCheck AI</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sidebar-tagline">AI-Powered Claim Verification</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-section-title">Capabilities</div>
            <div class="sidebar-feature">
                <span class="icon" style="background:rgba(16,185,129,0.1);color:#10b981;">✓</span>
                Extract factual claims from PDFs
            </div>
            <div class="sidebar-feature">
                <span class="icon" style="background:rgba(99,102,241,0.1);color:#6366f1;">✓</span>
                Search live web data
            </div>
            <div class="sidebar-feature">
                <span class="icon" style="background:rgba(6,182,212,0.1);color:#06b6d4;">✓</span>
                Verify information using AI
            </div>
            <div class="sidebar-feature">
                <span class="icon" style="background:rgba(239,68,68,0.1);color:#ef4444;">✓</span>
                Detect false or outdated claims
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-section-title">Tech Stack</div>
            <div class="sidebar-tech-item">
                <span class="tech-dot" style="background:#6366f1;"></span>
                Streamlit
            </div>
            <div class="sidebar-tech-item">
                <span class="tech-dot" style="background:#f97316;"></span>
                Groq LLM
            </div>
            <div class="sidebar-tech-item">
                <span class="tech-dot" style="background:#06b6d4;"></span>
                Serper Search API
            </div>
            <div class="sidebar-tech-item">
                <span class="tech-dot" style="background:#10b981;"></span>
                PyMuPDF
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="padding:0.8rem 1rem;border-radius:10px;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.12);font-size:0.8rem;color:#64748b;line-height:1.6;">
            💡 Upload a PDF report, article, or document to begin fact-checking.
        </div>
        """,
        unsafe_allow_html=True
    )


# ──────────────────────── MAIN AREA ────────────────────────

st.markdown(
    '<div class="badge-pill">⚡ AI-NATIVE FACT VERIFICATION</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-title">AI Fact-Check Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">Upload a PDF and verify claims using AI + Live Web Search</div>',
    unsafe_allow_html=True
)


# ── Upload Zone ──
st.markdown(
    """
    <div class="upload-zone">
        <span class="upload-icon">📄</span>
        <div class="upload-label">Drag & drop or click to upload</div>
        <div class="upload-hint">Supports PDF files only</div>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    " ",
    type=["pdf"],
    label_visibility="collapsed"
)

if uploaded_file:

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:8px;padding:0.7rem 1rem;border-radius:10px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);margin-bottom:1rem;font-size:0.85rem;color:#6ee7b7;">
            <span style="font-size:1rem;">✅</span> PDF uploaded successfully!
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 5])

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">File Size</div>
                <div class="metric-value">{round(uploaded_file.size / 1024, 2)} KB</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">File Name</div>
                <div class="metric-value">{uploaded_file.name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    if st.button("🚀  Verify Facts"):

        with st.spinner("📖 Reading PDF..."):

            text = extract_text_from_pdf(uploaded_file)

        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:8px;padding:0.7rem 1rem;border-radius:10px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);margin-bottom:0.5rem;font-size:0.85rem;color:#6ee7b7;">
                <span style="font-size:1rem;">✅</span> PDF text extracted successfully!
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("🧠 Extracting factual claims..."):

            claims = extract_claims(text)

        claims = list(set(claims))

        if len(claims) == 0:

            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:8px;padding:0.7rem 1rem;border-radius:10px;background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);font-size:0.85rem;color:#fcd34d;">
                    <span style="font-size:1rem;">⚠</span> No factual claims found in the PDF.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="section-header">📌 Claims Found</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="claims-count-badge">🔍 {len(claims)} factual claims detected</div>',
                unsafe_allow_html=True
            )

            for index, claim in enumerate(claims):

                with st.container():

                    st.markdown(
                        f"""
                        <div class="claim-box">
                            <div class="claim-number">
                                <span class="dot"></span>
                                Claim {index + 1}
                            </div>
                            <p class="claim-text">{claim}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.spinner("🌐 Searching web and verifying claim..."):

                        result = verify_claim(claim)

                    result_upper = result.upper()

                    if "VERIFIED" in result_upper:

                        st.success(result)

                    elif "FALSE" in result_upper:

                        st.error(result)

                    elif "INACCURATE" in result_upper:

                        st.warning(result)

                    else:

                        st.info(result)

                    st.divider()

else:

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:8px;padding:0.7rem 1rem;border-radius:10px;background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.12);font-size:0.85rem;color:#64748b;">
            <span style="font-size:1rem;">👆</span> Upload a PDF file to begin fact-checking.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class="footer-bar">
        Built by <span class="name">Deepak Kumar Sahu</span>
    </div>
    """,
    unsafe_allow_html=True
)
