import streamlit as st
import html

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="Fact Check Agent",
    page_icon="🔍",
    layout="wide"
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
    background: #0b1120;
    color: #f8fafc;
}

.main-title {
    text-align: center;
    margin-top: 30px;
    margin-bottom: 40px;
}

.main-title h1 {
    font-size: 3.2rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 8px;
}

.main-title p {
    color: #94a3b8;
    font-size: 1.05rem;
}

.upload-wrapper {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 30px;
}

[data-testid="stFileUploader"] {
    border: 2px dashed #334155;
    border-radius: 16px;
    background: #0f172a;
    padding: 30px;
}

[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6;
}

.claim-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 22px;
}

.claim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.claim-number {
    background: #1e293b;
    color: #cbd5e1;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.claim-category {
    background: #0f172a;
    border: 1px solid #334155;
    color: #cbd5e1;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
}

.claim-text {
    color: #ffffff;
    font-size: 19px;
    line-height: 1.7;
    margin-bottom: 20px;
    font-weight: 600;
}

.result-box {
    padding: 18px;
    border-radius: 14px;
    line-height: 1.8;
    font-size: 15px;
}

.verified {
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
}

.false {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.35);
}

.inaccurate {
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.35);
}

.unverifiable {
    background: rgba(148,163,184,0.12);
    border: 1px solid rgba(148,163,184,0.35);
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 18px;
    margin-top: 25px;
}

.summary-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 24px;
    text-align: center;
}

.summary-number {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 8px;
}

.summary-label {
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
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

.stButton button {
    height: 52px;
    border-radius: 14px;
    border: none;
    background: linear-gradient(
        135deg,
        #2563eb,
        #38bdf8
    );
    color: white;
    font-size: 16px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


def render_claim_card(
    number,
    claim,
    category,
    result,
    status_class
):

    safe_claim = html.escape(
        str(claim)
    )

    safe_result = html.escape(
        str(result)
    )

    safe_result = safe_result.replace(
        "\n",
        "<br>"
    )

    return f"""
    <div class="claim-card">

        <div class="claim-header">

            <div class="claim-number">
                Claim {number}
            </div>

            <div class="claim-category">
                {category}
            </div>

        </div>

        <div class="claim-text">
            {safe_claim}
        </div>

        <div class="result-box {status_class}">
            {safe_result}
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

        <div class="summary-card">
            <div class="summary-number green">
                {verified}
            </div>

            <div class="summary-label">
                Verified
            </div>
        </div>

        <div class="summary-card">
            <div class="summary-number red">
                {false}
            </div>

            <div class="summary-label">
                False
            </div>
        </div>

        <div class="summary-card">
            <div class="summary-number yellow">
                {inaccurate}
            </div>

            <div class="summary-label">
                Inaccurate
            </div>
        </div>

        <div class="summary-card">
            <div class="summary-number gray">
                {unverifiable}
            </div>

            <div class="summary-label">
                Unverifiable
            </div>
        </div>

    </div>
    """


st.markdown("""
<div class="main-title">

<h1>🔍 Fact Check Agent</h1>

<p>
Upload a PDF document and verify factual claims using AI + live web search
</p>

</div>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="upload-wrapper">',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    label_visibility="collapsed"
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "🚀 Start Fact Check",
        use_container_width=True
    ):

        with st.spinner(
            "Extracting text from PDF..."
        ):

            text = extract_text_from_pdf(
                uploaded_file
            )

        if not text.strip():

            st.error(
                "Could not extract text from PDF."
            )

            st.stop()

        with st.spinner(
            "Extracting factual claims..."
        ):

            claims = extract_claims(text)

        if not claims:

            st.warning(
                "No factual claims found."
            )

            st.stop()

        st.markdown(
            f"## 📝 Found {len(claims)} Claims"
        )

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
                status_class = "verified"

            elif "FALSE" in result_upper:

                false_count += 1
                status_class = "false"

            elif "INACCURATE" in result_upper:

                inaccurate_count += 1
                status_class = "inaccurate"

            else:

                unverifiable_count += 1
                status_class = "unverifiable"

            st.markdown(
                render_claim_card(
                    number=index + 1,
                    claim=claim["claim"],
                    category=claim["category"],
                    result=result,
                    status_class=status_class
                ),
                unsafe_allow_html=True
            )

        st.markdown("---")

        st.markdown(
            "## 📊 Summary"
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
        "Upload a PDF to begin fact-checking."
    )
