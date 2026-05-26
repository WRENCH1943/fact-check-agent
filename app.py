import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="AI Fact-Check Agent",
    page_icon="🔎",
    layout="wide"
)

st.markdown(
    """
    <style>

    .main {
        padding-top: 2rem;
    }

    .title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: inherit;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .claim-box {
        padding: 1.2rem;
        border-radius: 16px;
        background-color: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    .footer {
        text-align: center;
        color: gray;
        margin-top: 3rem;
        padding: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:

    st.title("📘 About")

    st.write(
        """
        This AI-powered tool automatically:

        ✅ Extracts factual claims from PDFs  
        ✅ Searches live web data  
        ✅ Verifies information using AI  
        ✅ Detects false or outdated claims  
        """
    )

    st.divider()

    st.subheader("🛠 Tech Stack")

    st.write(
        """
        - Streamlit  
        - Groq LLM  
        - Serper Search API  
        - PyMuPDF  
        """
    )

    st.divider()

    st.info(
        "Upload a PDF report, article, or document to begin fact-checking."
    )

st.markdown(
    '<div class="title">🔎 AI Fact-Check Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Upload a PDF and verify claims using AI + Live Web Search</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "📄 Upload PDF File",
    type=["pdf"]
)

if uploaded_file:

    st.success("✅ PDF uploaded successfully!")

    col1, col2 = st.columns([1, 5])

    with col1:
        st.metric("File Size", f"{round(uploaded_file.size / 1024, 2)} KB")

    with col2:
        st.metric("File Name", uploaded_file.name)

    st.divider()

    if st.button("🚀 Verify Facts"):

        with st.spinner("📖 Reading PDF..."):

            text = extract_text_from_pdf(uploaded_file)

        st.success("PDF text extracted successfully!")

        with st.spinner("🧠 Extracting factual claims..."):

            claims = extract_claims(text)

        claims = list(set(claims))

        if len(claims) == 0:

            st.warning("⚠ No factual claims found in the PDF.")

        else:

            st.subheader("📌 Claims Found")

            st.write(f"Detected **{len(claims)}** factual claims.")

            for index, claim in enumerate(claims):

                with st.container():

                    st.markdown(
                        f"""
                        <div class="claim-box">

                        <h4 style="color:inherit;">
                        Claim {index + 1}
                        </h4>

                        <p style="color:inherit; font-size:16px;">
                        {claim}
                        </p>

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

    st.info("👆 Upload a PDF file to begin fact-checking.")

st.markdown(
    """
    <div class="footer">
    Built by Deepak Kumar Sahu
    </div>
    """,
    unsafe_allow_html=True
)