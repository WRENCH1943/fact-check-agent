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

    if not document:
        return []

    all_claims = []

    chunks = chunk_text(document)

    for chunk in chunks:

        prompt = CLAIM_EXTRACTION_PROMPT.format(
            document=chunk
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

            content = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            parsed = json.loads(content)

            claims = parsed.get(
                "claims",
                []
            )

            for item in claims:

                if not isinstance(item, dict):
                    continue

                claim = (
                    item.get("claim", "")
                    .strip()
                )

                category = (
                    item.get("category", "")
                    .strip()
                )

                search_query = (
                    item.get(
                        "search_query",
                        ""
                    )
                    .strip()
                )

                if (
                    claim and
                    category and
                    search_query
                ):

                    all_claims.append({

                        "claim": claim,

                        "category": category,

                        "search_query": search_query

                    })

        except Exception as e:

            print(
                f"Claim extraction failed: {e}"
            )

            continue


    unique_claims = []

    seen = set()

    for item in all_claims:

        normalized = (
            item["claim"]
            .lower()
            .strip()
        )

        if normalized not in seen:

            seen.add(normalized)

            unique_claims.append(item)

    return unique_claims[:15]
