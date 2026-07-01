---
title: BizIntel Copilot
emoji: 📊
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# BizIntel Copilot

Ask questions about your business data in plain English — get back SQL, tables, and charts instantly. No coding required.

Built with LangChain, Groq, DuckDB, ChromaDB, and Streamlit.

---

## How it works

You type a question like *"Which states had negative profit last year?"* and the app:

1. Searches indexed documents for relevant context (RAG)
2. Generates a SQL query using an LLM with full schema awareness
3. Runs it against a DuckDB database
4. Automatically picks the right chart type and renders it

---

## Tech stack

| Layer | Tool |
|---|---|
| LLM | Groq (llama-3.3-70b) — free tier |
| SQL engine | DuckDB |
| Vector store | ChromaDB + sentence-transformers |
| Orchestration | LangChain |
| Frontend | Streamlit + Plotly |

---

## Running locally

```bash
git clone https://github.com/shreya2622/BizIntelCopilot
cd BizIntelCopilot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Groq API key
python data/load_data.py --csv your_superstore.csv
streamlit run app.py
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## Dataset

Uses the [Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) — US retail orders across 4 regions, 3 product categories, 2014–2017.
