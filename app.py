import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim


st.set_page_config(
    page_title="Fact Check Agent",
    page_icon="🔎",
    layout="wide"
)


st.title("🔎 Fact Check Agent")

st.write(
    "Upload a PDF → Extract factual claims → Verify using live web search"
)


uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)


if uploaded_file:

    st.success("PDF uploaded successfully")

    if st.button("Start Fact Check"):

        with st.spinner("Extracting text from PDF..."):

            text = extract_text_from_pdf(
                uploaded_file
            )

        if not text.strip():

            st.error(
                "Could not extract text from PDF"
            )

            st.stop()

        st.success(
            "PDF text extracted"
        )

        with st.spinner("Extracting claims..."):

            claims = extract_claims(text)

        if not claims:

            st.warning(
                "No factual claims found"
            )

            st.stop()

        st.subheader(
            f"Found {len(claims)} Claims"
        )

        verified_count = 0
        false_count = 0
        inaccurate_count = 0
        unverifiable_count = 0

        for index, claim in enumerate(claims):

            st.markdown("---")

            st.markdown(
                f"### Claim {index + 1}"
            )

            st.write(
                claim["claim"]
            )

            st.caption(
                f"Category: {claim['category']}"
            )

            with st.spinner(
                "Verifying claim..."
            ):

                result = verify_claim(
                    claim["claim"]
                )

            result_upper = result.upper()

            if "VERIFIED" in result_upper:

                verified_count += 1

                st.success(result)

            elif "FALSE" in result_upper:

                false_count += 1

                st.error(result)

            elif "INACCURATE" in result_upper:

                inaccurate_count += 1

                st.warning(result)

            else:

                unverifiable_count += 1

                st.info(result)

        st.markdown("---")

        st.subheader("Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Verified",
            verified_count
        )

        col2.metric(
            "False",
            false_count
        )

        col3.metric(
            "Inaccurate",
            inaccurate_count
        )

        col4.metric(
            "Unverifiable",
            unverifiable_count
        )

else:

    st.info(
        "Upload a PDF to begin"
    )
