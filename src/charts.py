from __future__ import annotations

import pandas as pd
import plotly.express as px


def histogram(df: pd.DataFrame, column: str):
    """Create a simple histogram for one numeric column."""
    fig = px.histogram(df, x=column, nbins=30, title=f"Distribution of {column}")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig


def bar_chart(df: pd.DataFrame, x_col: str, y_col: str, *, title: str):
    """Create a simple bar chart (e.g., Top-N categories)."""
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig


def line_chart(df: pd.DataFrame, x_col: str, y_col: str, *, title: str):
    """Create a simple line chart (e.g., monthly trend)."""
    fig = px.line(df, x=x_col, y=y_col, markers=True, title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig
