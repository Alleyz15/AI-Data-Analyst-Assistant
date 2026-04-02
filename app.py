from __future__ import annotations

import streamlit as st

from src.data_loader import load_csv
from src.analysis import (
    basic_overview,
    compute_kpi,
    insights_for_top_n,
    insights_for_trend,
    monthly_trend,
    top_n_by_category,
)
from src.charts import bar_chart, histogram, line_chart


st.set_page_config(page_title="AI Data Analyst Assistant", layout="wide")

st.title("AI Data Analyst Assistant")
st.caption("Upload a CSV to get basic analysis and a simple chart.")

with st.sidebar:
    st.header("Load data")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    encoding = st.text_input("Optional encoding (leave blank for default)", value="")

if uploaded is None:
    st.info("Upload a CSV to begin.")
    st.stop()

try:
    df = load_csv(uploaded, encoding=(encoding or None))
except Exception as exc:
    st.error("Could not read this CSV. Try a different file or encoding.")
    st.exception(exc)
    st.stop()

overview = basic_overview(df)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Preview")
    st.write(f"Rows: **{overview['rows']}** | Columns: **{overview['cols']}**")
    st.dataframe(df.head(50), use_container_width=True)

with col_right:
    st.subheader("Column types")
    st.dataframe(overview["dtypes"].rename("dtype"), use_container_width=True)

st.divider()

col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("Missing values (top)")
    missing = overview["missing"]
    missing_nonzero = missing[missing > 0]
    if len(missing_nonzero) == 0:
        st.write("No missing values detected.")
    else:
        st.dataframe(missing_nonzero.head(30).rename("missing_count"), use_container_width=True)

with col_b:
    st.subheader("Numeric summary")
    numeric_summary = overview["numeric_summary"]
    if numeric_summary.empty:
        st.write("No numeric columns found.")
    else:
        st.dataframe(numeric_summary, use_container_width=True)

st.divider()

st.subheader("Chart")
if len(overview["numeric_columns"]) == 0:
    st.write("Upload a dataset with at least one numeric column to see a chart.")
else:
    selected_col = st.selectbox("Choose a numeric column", overview["numeric_columns"])
    st.plotly_chart(histogram(df, selected_col), use_container_width=True)

st.divider()

st.subheader("Business Q&A (no AI yet — reliable templates)")
st.caption(
    "Pick a common business question type. This is deterministic (no LLM), so it stays explainable and presentation-friendly."
)

question_type = st.selectbox(
    "Question type",
    [
        "KPI (single number)",
        "Top categories (grouped table)",
        "Monthly trend (date-based)",
    ],
)

numeric_cols = overview["numeric_columns"]
all_cols = overview["all_columns"]

if question_type == "KPI (single number)":
    if not numeric_cols:
        st.warning("This dataset has no numeric columns.")
    else:
        metric_col = st.selectbox("Metric column", numeric_cols, key="kpi_metric")
        agg = st.selectbox("Aggregation", ["sum", "mean", "median", "min", "max", "count"], key="kpi_agg")
        value = compute_kpi(df, metric_col, agg)
        if value is None:
            st.write("No numeric values available for this KPI.")
        else:
            st.metric(label=f"{agg}({metric_col})", value=f"{value:,.2f}" if isinstance(value, float) else str(value))
            st.write(
                "Insight: KPIs are single-number summaries. In real dashboards, you'd usually pair this with a trend or a breakdown."
            )

elif question_type == "Top categories (grouped table)":
    if not numeric_cols:
        st.warning("This dataset has no numeric columns.")
    else:
        category_candidates = [c for c in all_cols if c not in numeric_cols]
        if not category_candidates:
            st.warning("No non-numeric (category) columns found for grouping.")
        else:
            category_col = st.selectbox("Category column", category_candidates, key="top_cat")
            metric_col = st.selectbox("Metric column", numeric_cols, key="top_metric")
            agg = st.selectbox("Aggregation", ["sum", "mean", "count"], key="top_agg")
            n = st.slider("Top N", 5, 30, 10, key="top_n")

            top = top_n_by_category(df, category_col, metric_col, agg, n)
            value_col = f"{agg}_{metric_col}"

            st.dataframe(top, use_container_width=True)
            st.plotly_chart(
                bar_chart(top, category_col, value_col, title=f"Top {n} {category_col} by {agg}({metric_col})"),
                use_container_width=True,
            )

            st.markdown("**Business insights**")
            for line in insights_for_top_n(top, category_col, value_col):
                st.write(f"- {line}")

else:  # Monthly trend
    if not numeric_cols:
        st.warning("This dataset has no numeric columns.")
    else:
        date_col = st.selectbox("Date column", all_cols, key="trend_date")
        metric_col = st.selectbox("Metric column", numeric_cols, key="trend_metric")
        agg = st.selectbox("Aggregation", ["sum", "mean", "count"], key="trend_agg")

        trend = monthly_trend(df, date_col, metric_col, agg)
        value_col = f"{agg}_{metric_col}"

        if trend.empty:
            st.write("No valid dates detected after parsing. Try a different date column.")
        else:
            st.dataframe(trend, use_container_width=True)
            st.plotly_chart(
                line_chart(trend, "month", value_col, title=f"Monthly {agg}({metric_col})"),
                use_container_width=True,
            )

            st.markdown("**Business insights**")
            for line in insights_for_trend(trend, value_col):
                st.write(f"- {line}")
