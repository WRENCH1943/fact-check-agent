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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        padding: 40px 20px;
        background-color: #f8fafc;
        text-align: center;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
        background-color: #eff6ff;
    }
    [data-testid="stFileUploader"] section {
        padding: 0;
        background-color: transparent;
    }
    
    [data-testid="stFileUploader"] p {
        margin-bottom: 0;
    }

    .claim-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 5px solid #cbd5e1;
        transition: transform 0.2s ease;
        animation: fadeIn 0.5s ease-in-out;
    }
    .claim-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    .status-verified { border-left-color: #10b981; background-color: #f0fdf4; }
    .status-false { border-left-color: #ef4444; background-color: #fef2f2; }
    .status-inaccurate { border-left-color: #f59e0b; background-color: #fffbeb; }
    .status-unverifiable { border-left-color: #6b7280; background-color: #f9fafb; }

    .claim-text {
        font-size: 16px;
        font-weight: 500;
        color: #1e293b;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .claim-meta {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 8px;
    }
    .verdict-text {
        font-size: 14px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #e2e8f0;
        line-height: 1.6;
    }

    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-green .metric-value { color: #10b981; }
    .metric-red .metric-value { color: #ef4444; }
    .metric-yellow .metric-value { color: #f59e0b; }
    .metric-gray .metric-value { color: #6b7280; }

    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)


def render_claim_card(claim_text, category, result_text, status_class):
    return f"""
    <div class="claim-card {status_class}">
        <div class="claim-text">"{claim_text}"</div>
        <div class="claim-meta">📂 Category: {category}</div>
        <div class="verdict-text">{result_text}</div>
    </div>
    """

def render_summary(verified, false, inaccurate, unverifiable):
    return f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 10px;">
        <div class="metric-card metric-green">
            <div class="metric-value">{verified}</div>
            <div class="metric-label">Verified</div>
        </div>
        <div class="metric-card metric-red">
            <div class="metric-value">{false}</div>
            <div class="metric-label">False</div>
        </div>
        <div class="metric-card metric-yellow">
            <div class="metric-value">{inaccurate}</div>
            <div class="metric-label">Inaccurate</div>
        </div>
        <div class="metric-card metric-gray">
            <div class="metric-value">{unverifiable}</div>
            <div class="metric-label">Unverifiable</div>
        </div>
    </div>
    """


if uploaded_file:
    st.markdown("""
    <div class="empty-state">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #0f172a; margin-bottom: 10px;">🔎 Fact Check Agent</h1>
        <p style="font-size: 1.1rem; color: #64748b; max-width: 400px; margin-bottom: 40px;">
            Upload a document to extract factual claims and verify them using live web search.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Drag and drop your PDF here, or click to browse", type=["pdf"], label_visibility="collapsed")

else:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-bottom: 5px;">🔎 Fact Check Agent</h1>
        <p style="color: #64748b;">Analyzing: <strong>{}</strong></p>
    </div>
    """.format(uploaded_file.name), unsafe_allow_html=True)

    if st.button("🚀 Start Fact Check", use_container_width=True, type="primary"):

        with st.status("Analyzing Document...", expanded=True) as status:
            st.write("🔍 **Step 1:** Extracting text from PDF...")
            text = extract_text_from_pdf(uploaded_file)
            
            if not text.strip():
                status.update(label="Extraction Failed", state="error", expanded=False)
                st.error("Could not extract text from the PDF. Please ensure it contains selectable text.")
                st.stop()
                
            st.write("🧠 **Step 2:** Identifying factual claims...")
            claims = extract_claims(text)
            
            if not claims:
                status.update(label="No Claims Found", state="error", expanded=False)
                st.warning("No factual claims could be identified in this document.")
                st.stop()

            status.update(label="Analysis Complete! Verifying claims...", state="complete", expanded=False)

        st.markdown(f"### 📝 Found {len(claims)} Claims")
        st.markdown("---")

        verified_count = 0
        false_count = 0
        inaccurate_count = 0
        unverifiable_count = 0

        for index, claim in enumerate(claims):
            with st.spinner(f"Verifying claim {index + 1}..."):
                result = verify_claim(claim["claim"])

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
        st.markdown("### 📊 Summary")
        st.markdown(
            render_summary(verified_count, false_count, inaccurate_count, unverifiable_count), 
            unsafe_allow_html=True
        )
