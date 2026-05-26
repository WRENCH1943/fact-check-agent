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

st.caption(
    "Upload a PDF → Extract factual claims → Verify with live web search"
)


uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
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

        st.subheader(
            f"📝 Found {len(claims)} Claims"
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

                box_type = "success"

            elif "FALSE" in result_upper:

                false_count += 1

                box_type = "error"

            elif "INACCURATE" in result_upper:

                inaccurate_count += 1

                box_type = "warning"

            else:

                unverifiable_count += 1

                box_type = "info"


            with st.container(border=True):

                st.markdown(
                    f"### Claim {index + 1}"
                )

                st.write(
                    claim["claim"]
                )

                st.caption(
                    f"Category: {claim['category']}"
                )

                if box_type == "success":

                    st.success(result)

                elif box_type == "error":

                    st.error(result)

                elif box_type == "warning":

                    st.warning(result)

                else:

                    st.info(result)

        st.markdown("---")

        st.subheader("📊 Summary")

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
        "Upload a PDF to begin fact-checking."
    )
