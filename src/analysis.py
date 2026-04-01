from __future__ import annotations

import pandas as pd


def basic_overview(df: pd.DataFrame) -> dict:
    """Compute small, UI-friendly summary stats."""
    missing_counts = df.isna().sum().sort_values(ascending=False)

    numeric_cols = df.select_dtypes(include="number").columns
    numeric_summary = df[numeric_cols].describe().T if len(numeric_cols) else pd.DataFrame()

    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "dtypes": df.dtypes.astype(str),
        "missing": missing_counts,
        "numeric_summary": numeric_summary,
        "numeric_columns": list(numeric_cols),
        "all_columns": list(df.columns),
    }
