# Demo Script

## Run the project
From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.run_pipeline
python -m src.validate_outputs
streamlit run app.py
```

## 3-5 minute dashboard walkthrough
1. Open the Streamlit URL shown in the terminal.
2. Select one ticker in the sidebar. Do not switch too many times during the demo.
3. Explain the four metrics at the top: latest close, daily return, historical up-day frequency, and 20-day volatility.
4. Open the Trend tab and explain how moving averages smooth the raw closing-price line.
5. Open the Probability tab and say clearly that this is historical frequency, not prediction.
6. Open the Insights tab and show how the report explains what the charts mean.
7. Open the Slide Figures tab only long enough to show that every saved figure maps to a slide.

## What to say while showing SQL
- Open `sql/schema.sql` and explain that processed data is stored in two tables: daily prices and monthly summaries.
- Open `sql/sample_queries.sql` and point to the five required query types.
- Say: "This lets us validate insights with SQL, not only Python charts."

## What to say while showing charts
- Closing price trend: "This gives the high-level market movement across selected stocks."
- Moving average trend: "Moving averages smooth noise and help describe trend regimes."
- Returns distribution: "This shows how daily movement is usually clustered near zero, with occasional outliers."
- Correlation heatmap: "This shows whether selected tickers tended to move together."
- Probability chart: "This is empirical historical frequency, not a reliable trading forecast."

## What to say while showing GenAI output
- "The script uses OpenAI if an API key is present."
- "For classroom reliability, it falls back to deterministic template insights."
- "The report is grounded in computed metrics and includes a no-financial-advice disclaimer."
- "The report explains chart meaning: trend direction, smoothing, volatility, frequency, and caution."

## What to say while showing GitHub repo
- Show `README.md` for setup and methodology.
- Show `src/` for modular scripts.
- Show `sql/` for schema and analysis queries.
- Show `presentation/` for slide content, speaker notes, and demo checklist.
- Show `.gitignore` to explain generated data is not committed by default.

## Timing guide
- 0:00-0:45: README, folder structure, validation command.
- 0:45-2:30: Dashboard metrics, Trend tab, Probability tab.
- 2:30-3:30: Insights report and limitations.
- 3:30-5:00: SQL queries and generated figures, if time remains.
