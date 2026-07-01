"""
Phase 4: Auto-generate a Plotly figure from a query result dataframe.

The LLM classifies the result as: bar | line | pie | table (no chart).
We then build the appropriate Plotly figure.
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def _classify_chart(question: str, df: pd.DataFrame) -> str:
    """Ask the LLM which chart type best suits the result."""
    col_info = ", ".join(f"{c} ({df[c].dtype})" for c in df.columns)
    prompt = f"""Given a user question and the column types of the query result,
choose the best chart type from: bar, line, pie, table.

Rules:
- line: result has a date/time column and one numeric column (trend over time)
- pie: result has exactly 2 columns — one categorical and one numeric, and <= 10 rows
- bar: result has one categorical and one or more numeric columns
- table: anything else, or more than 3 columns

User question: {question}
Result columns: {col_info}
Rows returned: {len(df)}

Reply with ONLY one word: bar, line, pie, or table."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _heuristic_chart(df)

    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=api_key)
        response = llm.invoke([("human", prompt)])
        chart_type = response.content.strip().lower().split()[0]
        if chart_type not in ("bar", "line", "pie", "table"):
            chart_type = _heuristic_chart(df)
    except Exception:
        chart_type = _heuristic_chart(df)

    return chart_type


def _heuristic_chart(df: pd.DataFrame) -> str:
    """Fallback chart type without LLM."""
    if df.shape[1] < 2:
        return "table"
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    date_cols = [c for c in df.columns if "date" in c.lower() or df[c].dtype == "datetime64[ns]"]
    if date_cols and numeric_cols:
        return "line"
    if len(df.columns) == 2 and numeric_cols and len(df) <= 10:
        return "pie"
    if numeric_cols:
        return "bar"
    return "table"


def _first_col(df: pd.DataFrame, dtype_filter=None) -> str:
    if dtype_filter:
        cols = df.select_dtypes(include=dtype_filter).columns.tolist()
        return cols[0] if cols else df.columns[0]
    return df.columns[0]


def build_chart(question: str, df: pd.DataFrame) -> go.Figure | None:
    """
    Returns a Plotly Figure or None if chart type is 'table' / df is too wide.
    """
    if df is None or df.empty:
        return None

    chart_type = _classify_chart(question, df)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
    date_cols = [c for c in df.columns if "date" in c.lower()]

    try:
        if chart_type == "line":
            x_col = date_cols[0] if date_cols else (cat_cols[0] if cat_cols else df.columns[0])
            y_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.line(df, x=x_col, y=y_col, title=question, markers=True,
                          color_discrete_sequence=["#a78bfa"])

        elif chart_type == "pie":
            label_col = cat_cols[0] if cat_cols else df.columns[0]
            value_col = numeric_cols[0] if numeric_cols else df.columns[1]
            fig = px.pie(df, names=label_col, values=value_col, title=question,
                         color_discrete_sequence=["#a78bfa","#60a5fa","#34d399","#f472b6","#fb923c","#facc15"])

        elif chart_type == "bar":
            x_col = cat_cols[0] if cat_cols else df.columns[0]
            y_cols = numeric_cols[:3]
            if len(y_cols) == 1:
                fig = px.bar(df, x=x_col, y=y_cols[0], title=question,
                             color_discrete_sequence=["#a78bfa"])
            else:
                fig = px.bar(df.melt(id_vars=[x_col], value_vars=y_cols),
                             x=x_col, y="value", color="variable", barmode="group",
                             title=question,
                             color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399"])
        else:
            return None

        fig.update_layout(
            plot_bgcolor="rgba(15,12,41,0.6)",
            paper_bgcolor="rgba(15,12,41,0.6)",
            font=dict(size=13, color="#e2e8f0"),
            title_font=dict(size=14, color="#cbd5e1"),
            xaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(color="#94a3b8"),
                title_font=dict(color="#94a3b8"),
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.06)",
                tickfont=dict(color="#94a3b8"),
                title_font=dict(color="#94a3b8"),
            ),
            legend=dict(font=dict(color="#cbd5e1")),
            margin=dict(l=40, r=20, t=50, b=40),
        )
        return fig

    except Exception:
        return None
