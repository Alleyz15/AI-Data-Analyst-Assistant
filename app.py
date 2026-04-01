from __future__ import annotations

import streamlit as st

from src.data_loader import load_csv
from src.analysis import basic_overview
from src.charts import histogram


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
