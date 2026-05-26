import json
import streamlit as st

from groq import Groq


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


CLAIM_EXTRACTION_PROMPT = """
You are an expert fact-checker.

Read the document below and extract ONLY strong,
verifiable factual claims.

Focus on:
- statistics
- percentages
- dates
- years
- funding
- revenue
- valuations
- acquisitions
- market share
- user counts
- technical metrics
- named entity relationships

IGNORE:
- opinions
- predictions
- hype
- marketing language
- vague statements

Return ONLY valid JSON.

Format:
{{
  "claims": [
    {{
      "claim": "...",
      "category": "...",
      "search_query": "..."
    }}
  ]
}}

Allowed categories:
- statistic
- date
- financial
- technical
- entity

Rules:
- claim must be self-contained
- maximum 25 words
- search query must be concise
- maximum 15 claims

DOCUMENT:
{document}
"""


def chunk_text(
    text,
    chunk_size=4000
):

    return [

        text[i:i + chunk_size]

        for i in range(
            0,
            len(text),
            chunk_size
        )

    ]


def extract_claims(document):

    if not document or len(document.strip()) < 20:
        return []

    prompt = CLAIM_EXTRACTION_PROMPT.format(
        document=document[:12000]
    )

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": "Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print(content)

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(content)

        claims = parsed.get(
            "claims",
            []
        )

        cleaned_claims = []

        seen = set()

        for item in claims:

            if not isinstance(item, dict):
                continue

            claim = item.get(
                "claim",
                ""
            ).strip()

            category = item.get(
                "category",
                ""
            ).strip()

            search_query = item.get(
                "search_query",
                ""
            ).strip()

            if (
                claim and
                claim.lower() not in seen
            ):

                seen.add(
                    claim.lower()
                )

                cleaned_claims.append({

                    "claim": claim,

                    "category": category,

                    "search_query": search_query

                })

        return cleaned_claims

    except Exception as e:

        print(
            f"Extractor Error: {e}"
        )

        return []
