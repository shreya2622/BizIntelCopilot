---
title: BizIntel Copilot
emoji: 📊
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
---

# BizIntel Copilot

RAG-Powered Natural Language Business Intelligence Assistant

**Stack:** LangChain · Groq (free LLM) · DuckDB · ChromaDB · Plotly · Streamlit

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

## Sample questions
- What are total sales by region?
- Which product category is most profitable?
- Show me monthly revenue trends for 2017
- Top 10 customers by sales
- Which states have negative profit?
- Average discount by customer segment
