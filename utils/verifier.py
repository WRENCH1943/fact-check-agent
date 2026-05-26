import streamlit as st
import requests

from groq import Groq


# Load API Keys from Streamlit Secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]


# Initialize Groq Client
client = Groq(
    api_key=GROQ_API_KEY
)


# -----------------------------------
# Search Web Using Serper
# -----------------------------------
def search_web(query):

    url = "https://google.serper.dev/search"

    payload = {
        "q": query
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    return response.json()



# -----------------------------------
# Verify Claim
# -----------------------------------
def verify_claim(claim):

    search_results = search_web(claim)

    snippets = ""


    # Extract search snippets
    if "organic" in search_results:

        for item in search_results["organic"][:5]:

            snippets += item.get("snippet", "") + "\n"



    # Prompt for AI verification
    prompt = f"""
    You are a professional fact-checking AI.

    Claim:
    {claim}

    Web Search Results:
    {snippets}

    Determine whether the claim is:

    - Verified
    - Inaccurate
    - False

    Rules:
    - VERIFIED = Claim matches reliable evidence.
    - INACCURATE = Claim is partially wrong or outdated.
    - FALSE = Claim is completely unsupported or incorrect.

    Also:
    - Explain WHY.
    - Provide the correct fact if possible.
    - Keep answer concise.
    """



    # LLM Verification
    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )


    result = response.choices[0].message.content

    return result