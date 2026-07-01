# BizIntel Copilot

RAG-Powered Natural Language Business Intelligence Assistant

**Stack:** LangChain · Groq (free LLM) · DuckDB · ChromaDB · Plotly · Streamlit

---

## Architecture

```
User question
    │
    ├─► RAG Retriever (ChromaDB + sentence-transformers)
    │       └─ domain context from indexed PDFs
    │
    ├─► SQL Agent (LangChain + Groq llama-3.3-70b)
    │       └─ schema_metadata.yaml as context
    │       └─ executes SQL against DuckDB
    │
    └─► Chart Builder (Plotly)
            └─ LLM classifies → bar / line / pie / table
```

---

## Quick start

### 1. Get a free Groq API key
Sign up at [console.groq.com](https://console.groq.com) — no credit card required.

```bash
cp .env.example .env
# Paste your key into .env
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Load the dataset
Download the **Superstore Sales Dataset** from Kaggle:
https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

```bash
python data/load_data.py --csv path/to/Sample_-_Superstore.csv
```

### 4. (Optional) Index PDF documents for RAG
```bash
python rag/ingest.py --pdf path/to/annual_report.pdf
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## Project structure

```
BizIntelCopilot/
├── app.py                  # Streamlit UI (Phase 5)
├── schema_metadata.yaml    # Table/column docs fed to LLM (Phase 1)
├── requirements.txt
├── .env.example
├── data/
│   └── load_data.py        # CSV → DuckDB loader (Phase 1)
├── agent/
│   └── sql_agent.py        # Text-to-SQL via Groq (Phase 2)
├── rag/
│   ├── ingest.py           # PDF → ChromaDB indexer (Phase 3)
│   └── retriever.py        # Semantic search retriever (Phase 3)
└── charts/
    └── chart_builder.py    # Auto Plotly chart generator (Phase 4)
```

---

## Sample questions
- "What are total sales by region?"
- "Which product category is most profitable?"
- "Show me monthly revenue trends for 2017"
- "Top 10 customers by sales"
- "Which states have negative profit?"
- "Average discount by customer segment"
