# AI Data Analyst Assistant (Python + Streamlit)

A beginner-friendly, professional mini project that loads a CSV, performs basic analysis with pandas, and shows a simple chart.

## What this first version does
- Upload a CSV in the UI
- Preview the data
- Show basic dataset summary (shape, dtypes, missing values)
- Show numeric summary statistics
- Generate a simple Plotly chart

## Project structure
```text
AI Data Analyst Assistant/
   app.py
   requirements.txt
   README.md
   .gitignore
   src/
      __init__.py
      data_loader.py
      analysis.py
      charts.py
```

## Tech stack
- Python
- pandas (data loading + analysis)
- Streamlit (UI)
- Plotly (charts)

## Quickstart
1) Create and activate a virtual environment (Windows PowerShell):
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`

2) Install dependencies:
   - `pip install -r requirements.txt`

3) Run the app:
   - `streamlit run app.py`

## VS Code setup notes
- Open this folder in VS Code.
- Select the interpreter: Ctrl+Shift+P → "Python: Select Interpreter" → choose `.venv`.

## Basic test (manual)
1) Start the app and upload any CSV.
2) Confirm you see:
   - Rows/columns count
   - A table preview
   - Missing values summary
   - A chart if there is at least one numeric column
