from __future__ import annotations

import pandas as pd


def load_csv(file_like, *, encoding: str | None = None) -> pd.DataFrame:
    """Load a CSV from a file-like object (e.g., Streamlit upload).

    Parameters
    ----------
    file_like:
        File-like object returned by Streamlit's uploader.
    encoding:
        Optional encoding (e.g., 'utf-8', 'latin-1'). If None, pandas will decide.

    Returns
    -------
    pd.DataFrame
    """
    return pd.read_csv(file_like, encoding=encoding)
