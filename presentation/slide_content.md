# Stock Market Trend Analysis - Slide Content

## 1. Title Slide
- Stock Market Trend Analysis
- Historical OHLCV pattern analysis
- Python, SQLite, Streamlit, and GenAI-style insights
Suggested visual: Dashboard screenshot.
Speaker emphasis: The project turns raw market data into explainable historical insights.

## 2. Problem Statement
- Stock data is noisy and difficult to interpret from raw rows
- Teams need clean visuals, metrics, and responsible interpretation
- Historical analysis must not be presented as guaranteed prediction
Suggested visual: Raw data to insight flow.
Speaker emphasis: The problem is insight extraction, not trading automation.

## 3. Objectives
- Collect and cache two years of daily data for 3-5 tickers
- Store cleaned features in SQLite with reusable SQL queries
- Generate charts, insights, and a demo dashboard
Suggested visual: Objective checklist.
Speaker emphasis: Every objective has a visible project artifact.

## 4. Solution Overview
- Download and cache yfinance OHLCV data
- Engineer trend, return, volatility, and monthly features
- Present results through SQL, figures, insights, and Streamlit
Suggested visual: End-to-end workflow diagram.
Speaker emphasis: The full workflow is reproducible from one command.

## 5. Tool Stack
- yfinance for ingestion; pandas and NumPy for processing
- SQLite for storage and evaluator-friendly querying
- Matplotlib, Seaborn, Streamlit, and optional OpenAI for presentation
Suggested visual: Simple layered tool stack.
Speaker emphasis: The stack is lightweight and practical for a trainee project.

## 6. Features
- Raw data cache and clear API failure handling
- Returns, direction, moving averages, volatility, and monthly summaries
- Deterministic insight fallback when no OpenAI key is available
Suggested visual: Feature grid.
Speaker emphasis: Reliability matters because the project must run during a live demo.

## 7. Workflow / System Architecture
- `data/raw` to `data/processed` to SQLite
- `outputs/figures` and `outputs/reports` hold presentation artifacts
- Streamlit reads generated artifacts for the dashboard
Suggested visual: Folder-aware architecture diagram.
Speaker emphasis: The project separates ingestion, processing, storage, reporting, and UI.

## 8. Dataset Overview & Preprocessing
- Default tickers: AAPL, MSFT, GOOGL, AMZN, NVDA
- Missing numeric values are filled by ticker after sorting
- Monthly aggregation supports cleaner trend comparison
Suggested visual: Processed table preview or SQLite preview.
Speaker emphasis: Preprocessing makes the later charts and metrics credible.

## 9. Exploratory Data Analysis
- Closing price and volume charts reveal broad movement and activity
- Return distributions show typical movement and outliers
- Correlation and probability charts summarize relationships and frequency
Suggested visual: EDA figure gallery.
Speaker emphasis: EDA converts noisy rows into patterns that can be explained.

## 10. Data Visualization & Insights
- Moving averages smooth price noise and show trend regimes
- Correlation explains whether selected stocks moved together
- Up/down probability is historical frequency, not forecast confidence
Suggested visual: Moving average chart plus probability chart.
Speaker emphasis: Each chart answers a specific presentation question.

## 11. GenAI Integration
- Generates `outputs/reports/daily_insights.md`
- Uses OpenAI when configured, otherwise template fallback
- Explains chart meaning, risk, and limitations from computed metrics
Suggested visual: Daily insights report screenshot.
Speaker emphasis: GenAI is used to explain metrics, not invent recommendations.

## 12. Key Insights & Recommendations
- Compare trend strength using price and moving averages
- Use volatility and return spread to discuss risk
- Use monthly summaries before drawing broad conclusions
Suggested visual: Dashboard Trend and Probability tabs.
Speaker emphasis: Recommendations are analytical next steps, not buy/sell advice.

## 13. Challenges & Learnings
- API dependency requires local caching
- Long moving averages need enough history
- Probability analysis must be framed responsibly
Suggested visual: Challenge to solution table.
Speaker emphasis: The project balances automation with careful interpretation.

## 14. Project Demo & Git Repository Demonstration
- Run validation, then open the dashboard
- Show SQL queries, generated charts, and insights report
- Walk through README, `src`, `sql`, and `presentation`
Suggested visual: Terminal, dashboard, and repo screenshots.
Speaker emphasis: The demo proves the project is reproducible and organized.

## 15. Conclusion & Future Scope
- Complete pipeline: ingestion, SQL, EDA, insights, dashboard
- Future: indicators, benchmark comparison, and deployment
- Future: research-only forecasting with proper backtesting
Suggested visual: Current system plus future roadmap.
Speaker emphasis: The foundation is complete, responsible, and extensible.
