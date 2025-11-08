# Capital-IQ — AI-Powered Financial Analyzer

An end‑to‑end app to analyze credit‑card transactions, detect fraud/anomalies, visualize spending, chat about your finances in plain English, and simulate “what‑if” scenarios.

This README covers both the theory (problem, data, model, metrics) and the implementation (architecture, setup, APIs, UI, and operations).

## Highlights

- Upload CSVs to analyze spending and detect anomalies (fraud) using a trained ML model
- Interactive charts for spend by category and plan vs actual
- Natural‑language chatbot and what‑if simulator powered by Groq LLMs
- Confusion matrix visualization generated on demand from your uploaded CSV

---

## System Architecture

- Frontend: React (Create React App), Chart.js, Axios
- Backend: Flask API (Python), scikit‑learn, pandas, joblib
- LLM: Groq API (model: llama‑3.3‑70b‑versatile) for query parsing and simulations
- Artifacts: `ml_assets/` holds the trained model, scaler, and metrics
- Data: sample/synthetic CSV via `generate_data.py`; training CSV `creditcard.csv`

Flow of data
1) User uploads CSV in the UI → 2) Flask validates and processes → 3) Model predicts anomalies and computes metrics → 4) Frontend renders metrics, charts, anomalies; users can chat or simulate scenarios.

---

## Theory: Fraud Detection and Financial Insights

### Dataset and Features
- Base dataset: Kaggle “Credit Card Fraud Detection” (anonymized) where `V1…V28` are PCA‑derived features; additional columns `Time`, `Amount`, and target `Class` (0=legit, 1=fraud).
- For user uploads, the app expects the same structure (see CSV schema below). A `Category` column is recommended for spending analysis.

### Preprocessing
- Standardize `Amount` and `Time` with StandardScaler → create `scaled_amount`, `scaled_time`; drop raw `Amount` and `Time` before training and inference.
- Keep feature order consistent with training via `model.feature_names_in_`.

### Model
- Algorithm: Logistic Regression (binary classification). It’s interpretable, fast, and competitive on this task.
- Train/validation split: stratified 80/20 to preserve class imbalance distribution.
- Class imbalance: the dataset is highly imbalanced. Precision/Recall, F1, Specificity, and MCC provide more meaningful evaluation than accuracy alone.

### Metrics (computed in `train_model.py`)
- Confusion Matrix entries: TP, TN, FP, FN
- Accuracy = (TP + TN) / (TP + TN + FP + FN)
- Precision = TP / (TP + FP)
- Recall (Sensitivity) = TP / (TP + FN)
- Specificity = TN / (TN + FP)
- F1‑Score = 2 · (Precision · Recall) / (Precision + Recall)
- Matthews Correlation Coefficient (MCC) ∈ [−1, 1] balances all four counts

Why these metrics? In fraud detection, catching rare positives without too many false alarms is critical; Precision/Recall, F1, and MCC reflect this trade‑off better than plain accuracy.

---

## Repository Layout

```
backend/
  app.py                # Flask API: analyze/query/simulate/confusion-matrix
  train_model.py        # Trains Logistic Regression; saves model/scaler/metrics to ml_assets/
  generate_data.py      # Creates realistic synthetic CSV for demos (large_test_data.csv)
  creditcard.csv        # Training dataset (Kaggle)
  ml_assets/            # Saved artifacts: fraud_detection_model.pkl, scaler.pkl, model_metrics.pkl
  requirements.txt      # Python dependencies
frontend/
  src/                  # React app (FinAnalysis, charts, chatbot, simulator)
  package.json          # npm scripts and deps
README.md               # This file
```

---

## Prerequisites

- Python 3.10–3.12 recommended (compatible with listed scikit‑learn and pandas)
- Node.js 18+ and npm
- Groq API key (for chatbot and what‑if simulator)

---

## Setup (Windows PowerShell)

### 1) Backend

Create and activate a virtual environment, then install dependencies.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

Configure environment variables (Groq):

- Create `backend/.env` with:

```
GROQ_API_KEY=your_groq_api_key_here
```

Train the model and produce artifacts (first‑time setup or whenever retraining):

```powershell
python train_model.py
```

Optional: generate a demo CSV if you don’t have one yet:

```powershell
python generate_data.py
```

Run the API server (default http://127.0.0.1:5000):

```powershell
python app.py
```

### 2) Frontend

Install dependencies and configure the API URL.

```powershell
cd ..\frontend
npm install
```

Create `frontend/.env` with:

```
REACT_APP_API_URL=http://127.0.0.1:5000
```

Start the React dev server (http://localhost:3000):

```powershell
npm start
```

---

## Using the App

1) In the left panel, upload your CSV and click “Analyze Transactions”.
2) View model metrics and the confusion matrix image generated from your file.
3) In the right panel, explore:
   - Expenditure Analysis (by category, total, and savings planner)
   - 💬 AI Assistant: ask natural‑language questions (uses your uploaded/synthetic CSV)
   - 🔮 What‑If Simulator: simulate purchases or budget changes

Notes
- After you upload a CSV, the backend stores a working copy as `backend/large_test_data.csv` for query/simulation.

---

## CSV Schema

Minimum for spending analysis
- `Amount` (number)
- `Category` (string)

Required for anomaly detection and all model‑based features
- `Time` (number)
- `V1` … `V28` (numbers)
- `Amount` (number)

Optional but recommended
- `Category` (string) — enables category charts and savings planner
- `Class` (0/1) — needed if you want the confusion matrix computed from ground truth

The app will return a helpful error if required columns are missing.

---

## API Reference (Flask)

Base URL: `http://127.0.0.1:5000`

### POST /analyze
Multipart/form‑data with field `file` (CSV). Returns:

```
{
  "model_performance": { "accuracy": ..., "precision": ..., "recall": ..., "f1_score": ..., "specificity": ..., "mcc": ..., "tn": ..., "fp": ..., "fn": ..., "tp": ... },
  "user_anomalies": [ {"Time": ..., "Amount": ..., "Category": ..., ...} ],
  "expenditure_analysis": {
    "total_spend": number,
    "spend_by_category": { [category]: number },
    "savings_plan": { [category]: "You could save $X.XX/month by reducing …" }
  }
}
```

Notes
- Scales `Amount` and `Time` with the saved scaler; enforces the same feature order used during training.
- Saves your uploaded CSV as `large_test_data.csv` for follow‑up queries/simulations.

### POST /query
Natural‑language questions about your data (Groq parses the query to a structured intent).

Request

```json
{ "query": "How much did I spend on coffee last month vs this month?" }
```

Response (example)

```json
{
  "response": "You spent $45.00 last month and $62.00 this month on coffee.",
  "data": { "last_month": 45, "this_month": 62, "category": "coffee" }
}
```

Notes
- Requires a CSV to be available (uploaded earlier or `large_test_data.csv` generated).
- Time handling is a simple slicing heuristic for demo purposes (days 1–30 vs 31–60).

### POST /simulate
Free‑form scenario simulation using Groq (e.g., big purchase, cut a category, save more per month).

Request

```json
{ "scenario": "What happens to my 6-month savings plan if I buy a $1,000 laptop today?" }
```

Response (example)

```json
{
  "impact_description": "Purchasing a $1,000 laptop today would reduce your 6-month savings by approximately $167.",
  "original_6month_savings": "$2,500",
  "new_6month_savings": "$2,333",
  "monthly_change": "-$167",
  "recommendations": ["Consider saving for 2 more months before purchasing", "Look for deals or refurbished options"]
}
```

Notes
- Uses current dataset loaded in memory from `large_test_data.csv`.

### POST /confusion-matrix
Multipart/form‑data with `file` (CSV). Returns a base64‑encoded PNG of the confusion matrix computed by the trained model against the file’s labels.

Requirements
- CSV must include: `Time`, `Amount`, `V1…V28`; optional `Class` (if absent, the endpoint assumes zeros and may return an error if only a single class is present).

---

## Frontend Overview (React)

- `FinAnalysis` orchestrates the UI in left/right panels
  - Left: upload, Analyze, metrics, and confusion matrix image
  - Right tabs:
    - 📊 Analysis: category chart + plan vs actual + savings planner PDF export
    - 💬 AI Assistant: natural‑language questions via `/query`
    - 🔮 What‑If Simulator: free‑form scenarios via `/simulate`
- `MetricsDisplay`: shows Accuracy, Precision, Recall, F1, Specificity, MCC
- `ExpenditureChart` and `ExpenditureComparisonChart`: Chart.js bar charts
- `ConfusionMatrixImage`: fetches and enlarges confusion matrix (base64 image)
- `Chatbot` and `WhatIfSimulator`: simple forms posting to the backend

Environment
- Set `REACT_APP_API_URL` to your Flask base URL (default `http://127.0.0.1:5000`).

---

## Security & Privacy

- Never commit secrets; the Groq key lives in `backend/.env` (git‑ignored).
- LLM calls happen only on the server; the frontend never sees your key.
- Uploaded CSVs are read into memory; a working copy is saved as `large_test_data.csv` for interactive features. Purge or rotate this file as needed.

---

## Troubleshooting

AI features disabled
- If you see “GROQ_API_KEY environment variable not set. AI features will not work.” set `GROQ_API_KEY` in `backend/.env`.

Missing columns / 400 errors
- Your CSV must include the required columns listed in the schema section; for confusion matrix, include `Class`.

Model artifacts missing
- Run `python backend/train_model.py` to generate `ml_assets/` (model, scaler, metrics).

CORS / connectivity
- Frontend talks to the Flask server at `REACT_APP_API_URL`. Ensure ports match (5000 vs 3000) and that `flask-cors` is enabled (already configured in `app.py`).

Package compatibility
- Use a recent Python (3.10–3.12). If native builds fail on Windows, install the official Python from python.org and retry inside a fresh venv.

---

## Roadmap / Enhancements

- Threshold tuning and probability outputs for the classifier
- Class‑imbalance handling (e.g., class weights, SMOTE)
- Persistent storage for user sessions and uploaded datasets
- Authentication and multi‑user separation
- More robust time handling (true calendar months)
- Deployment scripts (Docker, Gunicorn, reverse proxy)

---

## Acknowledgments

- Kaggle Credit Card Fraud Detection dataset
- scikit‑learn, Flask, React, Chart.js
- Groq LLMs for natural‑language parsing and scenario summaries
