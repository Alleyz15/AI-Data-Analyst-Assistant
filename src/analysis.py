from __future__ import annotations

import pandas as pd


def _safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def coerce_numeric(series: pd.Series) -> pd.Series:
    """Convert a Series to numeric where possible.

    Non-convertible values become NaN (keeps the app robust).
    """
    return pd.to_numeric(series, errors="coerce")


def coerce_datetime(series: pd.Series) -> pd.Series:
    """Convert a Series to datetime where possible.

    Non-convertible values become NaT.
    """
    return pd.to_datetime(series, errors="coerce")


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


def compute_kpi(df: pd.DataFrame, metric_col: str, agg: str) -> float | int | None:
    """Compute a single-number KPI for a numeric column."""
    values = coerce_numeric(df[metric_col])
    if values.dropna().empty:
        return None

    agg = agg.lower()
    if agg == "sum":
        return float(values.sum())
    if agg == "mean":
        return float(values.mean())
    if agg == "median":
        return float(values.median())
    if agg == "min":
        return float(values.min())
    if agg == "max":
        return float(values.max())
    if agg == "count":
        return int(values.count())
    raise ValueError(f"Unsupported aggregation: {agg}")


def top_n_by_category(
    df: pd.DataFrame,
    category_col: str,
    metric_col: str,
    agg: str,
    n: int,
) -> pd.DataFrame:
    """Compute a Top-N table for a category column grouped by a metric."""
    metric = coerce_numeric(df[metric_col])
    working = df[[category_col]].copy()
    working[metric_col] = metric

    agg = agg.lower()
    if agg == "sum":
        grouped = working.groupby(category_col, dropna=False)[metric_col].sum()
    elif agg == "mean":
        grouped = working.groupby(category_col, dropna=False)[metric_col].mean()
    elif agg == "count":
        grouped = working.groupby(category_col, dropna=False)[metric_col].count()
    else:
        raise ValueError(f"Unsupported aggregation: {agg}")

    out = grouped.sort_values(ascending=False).head(int(n)).reset_index()
    out = out.rename(columns={metric_col: f"{agg}_{metric_col}"})
    return out


def monthly_trend(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    agg: str,
) -> pd.DataFrame:
    """Compute a monthly trend table from a date column and numeric metric."""
    dates = coerce_datetime(df[date_col])
    metric = coerce_numeric(df[metric_col])

    temp = pd.DataFrame({"_date": dates, metric_col: metric}).dropna(subset=["_date"])
    if temp.empty:
        return pd.DataFrame(columns=["month", f"{agg}_{metric_col}"])

    temp["month"] = temp["_date"].dt.to_period("M").dt.to_timestamp()
    agg = agg.lower()
    if agg == "sum":
        trend = temp.groupby("month")[metric_col].sum()
    elif agg == "mean":
        trend = temp.groupby("month")[metric_col].mean()
    elif agg == "count":
        trend = temp.groupby("month")[metric_col].count()
    else:
        raise ValueError(f"Unsupported aggregation: {agg}")

    out = trend.reset_index().sort_values("month")
    out = out.rename(columns={metric_col: f"{agg}_{metric_col}"})
    return out


def insights_for_top_n(top_df: pd.DataFrame, category_col: str, value_col: str) -> list[str]:
    """Generate 2–3 short, rule-based insights for a Top-N table."""
    if top_df.empty:
        return ["No results for this question."]

    values = pd.to_numeric(top_df[value_col], errors="coerce")
    values = values.dropna()
    if values.empty:
        return ["The result column is not numeric, so insights are limited."]

    insights: list[str] = []
    leader = str(top_df.iloc[0][category_col])
    leader_value = float(values.iloc[0])
    total = float(values.sum())
    share = _safe_divide(leader_value, total)

    if share is not None:
        insights.append(f"Top category is '{leader}' with {leader_value:,.2f} (about {share:.0%} of the Top-N total).")
    else:
        insights.append(f"Top category is '{leader}' with {leader_value:,.2f}.")

    if len(values) >= 2:
        second = float(values.iloc[1])
        diff = leader_value - second
        insights.append(f"Gap between #1 and #2 is {diff:,.2f}.")

    insights.append("This view helps prioritize where the metric concentrates.")
    return insights[:3]


def insights_for_trend(trend_df: pd.DataFrame, value_col: str) -> list[str]:
    """Generate 2–3 short, rule-based insights for a monthly trend table."""
    if trend_df.empty or value_col not in trend_df.columns:
        return ["No trend data available (try a different date/metric column)."]

    values = pd.to_numeric(trend_df[value_col], errors="coerce").dropna()
    if len(values) < 2:
        return ["Not enough points to describe a trend."]

    first = float(values.iloc[0])
    last = float(values.iloc[-1])
    change = last - first
    pct = _safe_divide(change, abs(first))

    if pct is None:
        summary = f"Change from first to last period: {change:,.2f}."
    else:
        summary = f"Change from first to last period: {change:,.2f} ({pct:+.0%})."

    peak = float(values.max())
    trough = float(values.min())

    return [summary, f"Peak value is {peak:,.2f}; lowest is {trough:,.2f}.", "Use this to spot seasonality or growth/decline."]
