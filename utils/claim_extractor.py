import re


def extract_claims(text):

    claims = []

    sentences = re.split(r'[.\n]', text)

    patterns = [

        r"\d+%",
        r"\$\d+",
        r"\d{4}",
        r"million",
        r"billion",
        r"trillion",

    ]


    blacklist = [
        "report",
        "contents",
        "table of",
        "chapter"
    ]


    for sentence in sentences:

        clean_sentence = sentence.strip()


        # Skip very short sentences
        if len(clean_sentence) < 25:
            continue


        # Skip unwanted headings
        if any(word in clean_sentence.lower() for word in blacklist):
            continue


        for pattern in patterns:

            if re.search(pattern, clean_sentence, re.IGNORECASE):

                claims.append(clean_sentence)

                break


    return list(set(claims))