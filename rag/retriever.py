"""
Phase 3b: Retrieve relevant context from ChromaDB for a given question.
Returns an empty string gracefully if the chroma store hasn't been built yet.
"""

from __future__ import annotations

import os

import chromadb
from chromadb.utils import embedding_functions

ROOT = os.path.join(os.path.dirname(__file__), "..")
CHROMA_DIR = os.path.join(ROOT, "chroma_store")
COLLECTION_NAME = "company_docs"
TOP_K = 3


def retrieve(question: str) -> tuple[str, list[str]]:
    """
    Returns (combined_context_string, list_of_source_filenames).
    Returns ("", []) if the chroma store doesn't exist yet.
    """
    if not os.path.exists(CHROMA_DIR):
        return "", []

    try:
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        results = collection.query(query_texts=[question], n_results=min(TOP_K, collection.count()))
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        sources = list({m["source"] for m in metas})
        return "\n\n".join(docs), sources
    except Exception:
        return "", []
