"""
Phase 2: Text-to-SQL agent backed by Groq + DuckDB.

The agent receives a natural-language question, builds a SQL query using
schema context from schema_metadata.yaml, executes it against DuckDB, and
returns (sql, dataframe, error).
"""

from __future__ import annotations

import os
import re
import duckdb
import pandas as pd
import yaml
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

ROOT = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(ROOT, "superstore.db")
SCHEMA_PATH = os.path.join(ROOT, "schema_metadata.yaml")

_SCHEMA_CONTEXT: str | None = None


def _schema_context() -> str:
    global _SCHEMA_CONTEXT
    if _SCHEMA_CONTEXT is None:
        with open(SCHEMA_PATH) as f:
            meta = yaml.safe_load(f)
        lines = [f"Database: {meta['database']}", meta["description"].strip(), ""]
        for table, tinfo in meta["tables"].items():
            lines.append(f"Table: {table}")
            lines.append(f"  {tinfo['description'].strip()}")
            lines.append("  Columns:")
            for col, cinfo in tinfo["columns"].items():
                lines.append(f"    {col} ({cinfo['type']}): {cinfo['description']}")
            lines.append("")
        _SCHEMA_CONTEXT = "\n".join(lines)
    return _SCHEMA_CONTEXT


def _extract_sql(text: str) -> str:
    """Pull the first SQL block out of an LLM response."""
    # Try fenced code block first
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: grab everything from SELECT/WITH to end
    match = re.search(r"((?:SELECT|WITH)\b.*)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def _get_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set. Add it to your .env file.")
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=api_key)


def run_sql_agent(
    question: str,
    rag_context: str = "",
) -> tuple[str, pd.DataFrame | None, str | None]:
    """
    Returns (sql_query, dataframe_or_None, error_or_None).
    If rag_context is provided it is prepended to give the LLM domain knowledge.
    """
    schema = _schema_context()
    rag_section = f"\nAdditional domain context:\n{rag_context}\n" if rag_context else ""

    system_prompt = f"""You are a senior data analyst. Given a user question and the
database schema below, write a single DuckDB-compatible SQL SELECT query that answers
the question precisely. Return ONLY the SQL inside a ```sql ... ``` code block.
Do not explain anything else.

{schema}{rag_section}
Rules:
- Use only the table and columns listed above.
- Column names with spaces have been replaced by underscores (e.g. "Order Date" → Order_Date).
- For date filtering use CAST(column AS DATE) or date literals like DATE '2017-01-01'.
- Limit to 500 rows unless the user asks for all.
- Never use DELETE, DROP, INSERT, UPDATE or DDL statements.
"""

    llm = _get_llm()
    messages = [
        ("system", system_prompt),
        ("human", question),
    ]
    response = llm.invoke(messages)
    sql = _extract_sql(response.content)

    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute(sql).df()
        con.close()
        return sql, df, None
    except Exception as exc:
        return sql, None, str(exc)
