# BusinessIntelligence.ai

An autonomous KPI intelligence engine that pairs a **deterministic Python math layer** with a
**generative AI synthesis layer** (Gemini 3.6 Flash) to explain KPI movements, cite evidence,
abstain when data is insufficient, and enforce role-based access — all inside a Streamlit dashboard.

## Why two layers?

| Layer | File(s) | Responsibility |
|---|---|---|
| Deterministic Math Engine | `src/contribution_engine.py`, `src/anomaly_engine.py` | Pure pandas/Python. Computes anomalies (z-score + absolute impact) and decomposes revenue variance into Volume vs. Price drivers. Numbers are never touched by the LLM. |
| Generative Synthesis | `src/llm_synthesizer.py` | Retrieves relevant unstructured logs and asks Gemini to narrate the *why*, strictly grounded in the math JSON, with an explicit abstention rule when evidence is missing. |

This separation means the LLM is never allowed to invent a number — it can only explain numbers
that Python already calculated.

## Project structure

```
.
├── app.py                          # Streamlit dashboard (4 demo scenarios)
├── semantic_contract.json          # Governance layer: KPI definition, owner, RBAC rules
├── requirements.txt
├── .env.example                    # Copy to .env and add your Gemini API key
├── .gitignore
├── data/
│   ├── orders_daily.csv            # order_date, region, revenue, units, discount_percent, return_status
│   ├── unstructured_logs.csv       # log_date, region, log_type, log_text
│   └── marketing_campaigns_weekly.csv  # week_start, region, channel, spend, clicks, impressions
└── src/
    ├── __init__.py
    ├── anomaly_engine.py           # Rolling z-score + absolute-impact anomaly detector
    ├── contribution_engine.py      # Volume vs. Price variance decomposition
    └── llm_synthesizer.py          # Log retrieval + Gemini narrative generation (standalone CLI script)
```

`app.py` imports the backend modules as a package (`from src.contribution_engine import analyze_drivers`),
so it must always be run from the **project root**, and `src/__init__.py` must be present.

## Setup

1. **Clone and enter the repo**
   ```bash
   git clone <your-repo-url>
   cd BusinessIntelligence
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Gemini API key**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```
   Get a key at https://aistudio.google.com/app/apikey. The key is loaded automatically via
   `python-dotenv`, and can also be pasted directly into the sidebar text input in the app.

5. **Confirm the data files are in `data/`** (already included in this repo — see structure above).

## Running the app

From the project root:

```bash
streamlit run app.py
```

This opens the dashboard at `http://localhost:8501` with four tabs:

1. **Multi-Factor Drop** — live Northeast revenue anomaly (Aug 24, 2026), dynamically computed by
   `contribution_engine.py`, with an "Run AI Synthesis" button that calls Gemini 3.6 Flash to
   generate a grounded narrative and recommendation.
2. **Low-Confidence / Abstain** — demonstrates the safety gate that makes the model abstain instead
   of guessing when no supporting logs or campaign data exist.
3. **Sparse History** — cohort-benchmarking fallback for a SKU with too little history for a normal
   30-day baseline.
4. **Role-Based Security** — same underlying data rendered differently (full / regional / redacted)
   depending on the selected persona, per `semantic_contract.json`.

## Running the math/AI pipeline standalone (without Streamlit)

```bash
python src/anomaly_engine.py        # prints flagged anomalies as JSON
python src/contribution_engine.py   # prints the Volume/Price variance decomposition
python src/llm_synthesizer.py       # runs the full retrieval + Gemini synthesis pipeline
```

Note: these scripts expect to be run from the project root, since they reference
`data/orders_daily.csv` and `data/unstructured_logs.csv` with relative paths.

## Model

The app and `src/llm_synthesizer.py` both call **`gemini-3.6-flash`** via the `google-genai` SDK.

## Governance

`semantic_contract.json` defines the KPI's formula, owner, update cadence, and role-based access
rules. `app.py` renders this contract in an expandable panel so any consumer of the dashboard can
audit exactly how "Revenue" is defined before trusting the AI's narrative.

## Feedback loop

The sidebar includes a lightweight feedback form (👍/👎 + free-text notes). Submissions are appended
to `feedback_store.json` (git-ignored, created at runtime) for later review.
