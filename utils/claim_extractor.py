import streamlit as st
import json
from groq import Groq

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

Return ONLY valid JSON array.

Each item MUST contain:
{{
  "claim": "...",
  "category": "...",
  "search_query": "..."
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

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


def chunk_text(
    text,
    chunk_size=4000
):

    chunks = []

    for i in range(0, len(text), chunk_size):

        chunks.append(
            text[i:i + chunk_size]
        )

    return chunks


def extract_claims(document):

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

                temperature=0,

                response_format={
                    "type": "json_object"
                }

            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            parsed = json.loads(content)

            if isinstance(parsed, dict):

                claims = parsed.get(
                    "claims",
                    []
                )

            else:

                claims = parsed


            for item in claims:

                if not isinstance(item, dict):
                    continue

                if (
                    "claim" in item and
                    "category" in item and
                    "search_query" in item
                ):

                    all_claims.append({

                        "claim":
                        item["claim"].strip(),

                        "category":
                        item["category"].strip(),

                        "search_query":
                        item["search_query"].strip()

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
