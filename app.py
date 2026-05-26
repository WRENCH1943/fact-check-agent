import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="Fact Check Agent",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background: #0f172a;
    color: #f8fafc;
}

h1, h2, h3 {
    color: #f8fafc;
}

[data-testid="stFileUploader"] {
    border: 2px dashed #334155;
    border-radius: 16px;
    padding: 40px 20px;
    background: #111827;
}

[data-testid="stFileUploader"]:hover {
    border-color: #38bdf8;
    background: #1e293b;
}

.claim-card {
    padding: 22px;
    border-radius: 14px;
    margin-bottom: 20px;
    background: #111827;
    border-left: 6px solid #334155;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}

.status-verified {
    border-left-color: #22c55e;
    background: #052e16;
}

.status-false {
    border-left-color: #ef4444;
    background: #450a0a;
}

.status-inaccurate {
    border-left-color: #f59e0b;
    background: #451a03;
}

.status-unverifiable {
    border-left-color: #94a3b8;
    background: #1e293b;
}

.claim-title {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 14px;
}

.claim-category {
    font-size: 14px;
    color: #cbd5e1;
    margin-bottom: 14px;
}

.claim-result {
    font-size: 15px;
    line-height: 1.7;
    color: #e2e8f0;
    border-top: 1px solid #334155;
    padding-top: 14px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 16px;
    margin-top: 20px;
}

.metric-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}

.metric-number {
    font-size: 34px;
    font-weight: 700;
}

.metric-label {
    margin-top: 8px;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 13px;
}

.green {
    color: #22c55e;
}

.red {
    color: #ef4444;
}

.yellow {
    color: #f59e0b;
}

.gray {
    color: #cbd5e1;
}

.hero {
    text-align: center;
    margin-top: 50px;
    margin-bottom: 40px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #f8fafc;
}

.hero-subtitle {
    color: #94a3b8;
    margin-top: 10px;
    font-size: 1.05rem;
}

</style>
""", unsafe_allow_html=True)


def render_claim_card(
    claim_text,
    category,
    result_text,
    status_class
):

    return f"""
    <div class="claim-card {status_class}">

        <div class="claim-title">
            {claim_text}
        </div>

        <div class="claim-category">
            📂 Category: {category}
        </div>

        <div class="claim-result">
            {result_text}
        </div>

    </div>
    """


def render_summary(
    verified,
    false,
    inaccurate,
    unverifiable
):

    return f"""
    <div class="summary-grid">

        <div class="metric-card">
            <div class="metric-number green">
                {verified}
            </div>

            <div class="metric-label">
                Verified
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-number red">
                {false}
            </div>

            <div class="metric-label">
                False
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-number yellow">
                {inaccurate}
            </div>

            <div class="metric-label">
                Inaccurate
            </div>
        </div>

        <div class="metric-card">
            <div class="metric-number gray">
                {unverifiable}
            </div>

            <div class="metric-label">
                Unverifiable
            </div>
        </div>

    </div>
    """


st.markdown(f"""
<div class="hero">

    <div class="hero-title">
        🔎 Fact Check Agent
    </div>

    <div class="hero-subtitle">
        Upload a PDF → Extract factual claims → Verify with live web search
    </div>

</div>
""", unsafe_allow_html=True)


uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    label_visibility="collapsed"
)


if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "🚀 Start Fact Check",
        use_container_width=True
    ):

        with st.status(
            "Analyzing document...",
            expanded=True
        ) as status:

            st.write(
                "📖 Extracting text from PDF..."
            )

            text = extract_text_from_pdf(
                uploaded_file
            )

            if not text.strip():

                st.error(
                    "Could not extract text from PDF"
                )

                st.stop()

            st.write(
                "🧠 Extracting factual claims..."
            )

            claims = extract_claims(text)

            if not claims:

                st.warning(
                    "No factual claims found"
                )

                st.stop()

            status.update(
                label="Claims extracted successfully",
                state="complete",
                expanded=False
            )

        st.markdown(
            f"## 📝 Found {len(claims)} Claims"
        )

        st.markdown("---")

        verified_count = 0
        false_count = 0
        inaccurate_count = 0
        unverifiable_count = 0

        for index, claim in enumerate(claims):

            with st.spinner(
                f"Verifying claim {index + 1}..."
            ):

                result = verify_claim(
                    claim["claim"]
                )

            result_upper = result.upper()

            if "VERIFIED" in result_upper:

                verified_count += 1

                status_class = "status-verified"

            elif "FALSE" in result_upper:

                false_count += 1

                status_class = "status-false"

            elif "INACCURATE" in result_upper:

                inaccurate_count += 1

                status_class = "status-inaccurate"

            else:

                unverifiable_count += 1

                status_class = "status-unverifiable"

            st.markdown(
                render_claim_card(
                    claim_text=claim["claim"],
                    category=claim["category"],
                    result_text=result,
                    status_class=status_class
                ),
                unsafe_allow_html=True
            )

        st.markdown("---")

        st.markdown(
            f"## 📊 Summary"
        )

        st.markdown(
            render_summary(
                verified_count,
                false_count,
                inaccurate_count,
                unverifiable_count
            ),
            unsafe_allow_html=True
        )

else:

    st.info(
        "Upload a PDF to begin fact-checking"
    )
