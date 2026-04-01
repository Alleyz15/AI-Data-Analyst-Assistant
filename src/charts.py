from __future__ import annotations

import pandas as pd
import plotly.express as px


def histogram(df: pd.DataFrame, column: str):
    """Create a simple histogram for one numeric column."""
    fig = px.histogram(df, x=column, nbins=30, title=f"Distribution of {column}")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig
