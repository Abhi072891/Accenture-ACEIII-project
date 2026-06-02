# Stock Market Trend Analysis

Enterprise-ready data pipeline and dashboard for analyzing historical stock trends and identifying patterns from daily OHLCV data. The project is designed for reproducible deployment: a single pipeline command autonomously bootstraps the local data cache, SQLite database, EDA charts, GenAI insight report, and the interactive Streamlit UI.

**Disclaimer:** This is a historical trend analysis tool built for educational and evaluation purposes. It is not financial advice and is not a reliable price prediction system.

## What This Project Demonstrates

- **Resilient Data Ingestion:** API-based stock data retrieval with local raw-data caching to prevent rate-limiting during live demos.
- **Feature Engineering:** Time-series preprocessing for daily returns, price direction, moving averages, rolling volatility, and macroeconomic monthly trends.
- **Robust Storage:** SQLite integration with reusable SQL queries and optimized indexing.
- **Automated Analytics:** Generation of presentation-ready static figures saved to `outputs/figures`.
- **GenAI Integration:** Dynamic insight generation utilizing the **Gemini 2.5 Flash API**, complete with a deterministic, fault-tolerant fallback mechanism for guaranteed uptime.
- **Interactive UI:** A highly polished Streamlit dashboard featuring zero-state cloud bootstrapping.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.run_pipeline
streamlit run app.py

```

Open the Streamlit URL shown in the terminal, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

This project utilizes a zero-state deployment architecture. Generated data, figures, reports, and the SQLite database are ignored by `.gitignore` so the source repository stays lightweight.

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud and choose **New app**.
3. Select the GitHub repository and branch.
4. Set the main file path to `app.py`.
5. **Add Secrets:** Navigate to Advanced Settings -> Secrets and add your Gemini API key:
```toml
GEMINI_API_KEY = "your_api_key_here"

```


6. Deploy.

*Note: The first cloud startup will take ~30 seconds because the application detects the missing `data/stock_trends.db` and autonomously triggers the backend ETL pipeline to recreate the database, figures, and insights within the cloud environment.*

## Demo Flow In 3-5 Minutes

1. Show this `README.md` to highlight the modular, enterprise-grade folder structure.
2. Open the Streamlit dashboard and select a ticker.
3. Explain the top-line metrics: Latest Close, Daily Return, Historical Up-Day Frequency, and 20-Day Volatility.
4. Navigate through the **Trend, Probability, Insights, and Static Analytics** tabs.
5. Highlight the fault-tolerant GenAI architecture in the Insights tab.
6. (Optional) Open `sql/sample_queries.sql` to demonstrate the underlying data is fully queryable.

## Repository Structure

```text
.
├── app.py                         # Interactive Streamlit dashboard
├── requirements.txt               # Python dependencies (includes google-genai)
├── src/
│   ├── ingest.py                  # yfinance download and raw CSV cache
│   ├── preprocess.py              # cleaning, features, monthly aggregation, SQLite write
│   ├── eda.py                     # presentation-ready figure generation
│   ├── genai_insights.py          # Gemini 2.5 Flash API integration and template fallback
│   ├── run_pipeline.py            # full pipeline orchestration
│   └── validate_outputs.py        # demo-readiness checks
├── sql/
│   ├── schema.sql                 # SQLite schema
│   └── sample_queries.sql         # required analysis queries
├── data/                          # generated raw, processed, and SQLite data (git-ignored)
├── outputs/
│   ├── figures/                   # generated chart PNGs (git-ignored)
│   └── reports/                   # generated Markdown insights (git-ignored)

```

## Pipeline Commands

Run the full pipeline:

```bash
python -m src.run_pipeline

```

Run individual stages:

```bash
python -m src.ingest
python -m src.preprocess
python -m src.eda
python -m src.genai_insights

```

Run with custom tickers:

```bash
python -m src.run_pipeline --tickers AAPL MSFT GOOGL AMZN NVDA --period 2y

```

Set up Gemini API locally (Windows Command Prompt):

```cmd
set GEMINI_API_KEY=your_api_key_here

```

*Without an API key, the project gracefully defaults to generating `outputs/reports/daily_insights.md` using a deterministic template fallback.*

## Chart Purpose

Each chart generated in `outputs/figures` serves a specific analytical role:

* `closing_price_trend.png`: Macroeconomic trend comparison for the entire portfolio.
* `moving_average_trend.png`: Visualizes signal vs. noise using 20, 50, and 200-day smoothing.
* `daily_returns_distribution.png`: Explains volatility, variance spread, and outlier magnitude.
* `volume_trend.png`: Contextualizes price movement with institutional trading conviction.
* `correlation_heatmap.png`: Maps co-movement to highlight systemic risk and diversification (or lack thereof).
* `probability_up_down_by_ticker.png`: Retrospective, empirical up/down frequency by ticker.

## SQL Analysis

`sql/sample_queries.sql` includes analytical queries testing the engineered database:

* Average daily return by ticker
* Highest volume days
* Moving average crossover points
* Probability of price increase by ticker
* Monthly trend summary

Run all sample queries locally:

```bash
sqlite3 data/stock_trends.db < sql/sample_queries.sql

```

## Limitations

* This project analyzes historical data only.
* It does not provide financial advice, buy/sell recommendations, or portfolio guidance.
* Historical up/down probability is descriptive frequency, not forecast confidence.
* Moving averages and rolling volatility are lagging indicators.

## Future Scope (Enterprise Vision)

* **Advanced Time Series Analysis:** Evolve descriptive moving averages into predictive SARIMA forecasting and stochastic process modeling.
* **RAG Architecture:** Upgrade the GenAI static prompt to a Retrieval-Augmented Generation (RAG) pipeline, vectorizing SEC filings and live financial news to ground the LLM in real-time macroeconomic context.
* **Deep Learning:** Expand the feature space and implement 1D Convolutional Neural Networks (ResNet) to identify non-linear market patterns.
* **Data Privacy Protocols:** Implement Local Differential Privacy and k-anonymity frameworks if expanding the platform to handle sensitive client portfolio data.

```

