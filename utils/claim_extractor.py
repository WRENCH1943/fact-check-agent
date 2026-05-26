import json
import streamlit as st

from groq import Groq


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


CLAIM_EXTRACTION_PROMPT = """You are an expert fact-checker.

Read the document below and extract every verifiable factual claim.

Focus on:
- Statistics and percentages
- Dates and years
- Financial figures
- Technical figures
- Named-entity factual statements

For each claim, return ONLY a JSON array.

Each item must have:
- "claim"
- "category"
- "search_query"

Allowed categories:
- statistic
- date
- financial
- technical
- entity

Skip opinions, predictions, and marketing fluff.

Extract at most 15 claims.

DOCUMENT:
{document}

Return ONLY valid JSON.

Example:
[
  {{
    "claim": "ChatGPT has 200 million weekly active users",
    "category": "statistic",
    "search_query": "ChatGPT weekly active users"
  }}
]
"""


def extract_claims(document_text):

    truncated = document_text[:25000]

    prompt = CLAIM_EXTRACTION_PROMPT.format(
        document=truncated
    )

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        raw = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        if raw.startswith("```"):

            raw = raw.split(
                "```",
                2
            )[1]

            if raw.startswith("json"):
                raw = raw[4:]

            raw = raw.strip()

        if raw.endswith("```"):
            raw = raw[:-3].strip()

        claims = json.loads(raw)

        if not isinstance(claims, list):
            return []

        unique_claims = []

        seen = set()

        for item in claims:

            if not isinstance(item, dict):
                continue

            claim = item.get(
                "claim",
                ""
            ).strip()

            if (
                claim and
                claim.lower() not in seen
            ):

                seen.add(
                    claim.lower()
                )

                unique_claims.append({

                    "claim": claim,

                    "category":
                    item.get(
                        "category",
                        ""
                    ),

                    "search_query":
                    item.get(
                        "search_query",
                        claim
                    )

                })

        return unique_claims[:15]

    except Exception as e:

        print(
            f"Claim extraction error: {e}"
        )

        return []
