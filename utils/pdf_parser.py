import fitz


def extract_text_from_pdf(pdf_file):

    """
    Extracts all text from uploaded PDF file.
    """

    text = ""

    try:

        pdf = fitz.open(
            stream=pdf_file.read(),
            filetype="pdf"
        )

        for page in pdf:

            text += page.get_text()

    except Exception as e:

        text = f"Error reading PDF: {e}"

    return text