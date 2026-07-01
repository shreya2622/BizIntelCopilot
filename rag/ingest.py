"""
Phase 3a: Ingest PDFs into ChromaDB.

Usage:
    python rag/ingest.py --pdf path/to/report.pdf [--pdf path/to/other.pdf]

The chroma_store/ directory is created next to this file's parent (project root).
Run this once per PDF; re-running with the same file is safe (collection is cleared first).
"""

from __future__ import annotations

import argparse
import os

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

ROOT = os.path.join(os.path.dirname(__file__), "..")
CHROMA_DIR = os.path.join(ROOT, "chroma_store")
COLLECTION_NAME = "company_docs"
CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


def _read_pdf(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def ingest(pdf_paths: list[str]) -> None:
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Re-create collection so re-runs are idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME, embedding_function=ef)

    doc_id = 0
    for pdf_path in pdf_paths:
        print(f"Ingesting {pdf_path} …")
        text = _read_pdf(pdf_path)
        chunks = _chunk_text(text)
        source = os.path.basename(pdf_path)
        ids = [f"doc_{doc_id + i}" for i in range(len(chunks))]
        metas = [{"source": source, "chunk": i} for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=metas)
        doc_id += len(chunks)
        print(f"  → {len(chunks)} chunks indexed from {source}")

    print(f"\nTotal documents in collection: {collection.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="append", required=True, dest="pdfs")
    args = parser.parse_args()
    ingest(args.pdfs)
