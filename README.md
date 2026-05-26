# 🔎 AI Fact-Check Agent

An AI-powered fact-checking web application that verifies factual claims from uploaded PDF documents using live web search and LLM-based reasoning.

---

## 🚀 Features

- 📄 Upload PDF documents
- 🧠 Extract factual/statistical claims automatically
- 🌐 Search live web data using Serper API
- 🤖 Verify claims using Groq LLM
- ✅ Detect:
  - Verified claims
  - False claims
  - Inaccurate/outdated claims
- 🎨 Modern Streamlit UI

---

## 🛠 Tech Stack

- Streamlit
- Groq API
- Serper API
- PyMuPDF
- Python

---

## 📂 Project Structure

```bash
fact-check-agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│
└── utils/
    ├── pdf_parser.py
    ├── claim_extractor.py
    └── verifier.py
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/fact-check-agent.git
```

Go into project directory:

```bash
cd fact-check-agent
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create:

```bash
.streamlit/secrets.toml
```

Add:

```toml
GROQ_API_KEY="your_groq_api_key"
SERPER_API_KEY="your_serper_api_key"
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 🌍 Deployment

This project is deployed using Streamlit Community Cloud.

---

## 📌 Example Claims Tested

- “The AI market reached $5 trillion in 2023.”
- “ChatGPT launched in November 2022.”
- “Tesla was founded in 2003.”

---

## 🎯 Objective

The goal of this project is to combat misinformation and hallucinated statistics in reports, articles, and marketing documents through automated AI-powered fact verification.

---

## 👨‍💻 Author

Deepak Kumar Sahu
