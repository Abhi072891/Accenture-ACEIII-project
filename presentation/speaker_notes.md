# Speaker Notes

## Member 1: Slides 1-4
Open by introducing the project as an educational stock market trend analysis system. Explain that the team is analyzing historical OHLCV data, meaning open, high, low, close, and volume. Clarify early that the project identifies patterns from history and does not claim to predict future prices reliably.

For the problem statement, describe how stock data is noisy and difficult to interpret directly from raw rows. A viewer can see prices moving daily, but without preprocessing and visualization it is hard to identify trend direction, volatility, or repeated behavior. Emphasize that responsible analysis should separate historical evidence from trading advice.

For objectives, connect each goal to a concrete artifact: raw cached CSV files, a SQLite database, generated charts, a GenAI-style report, and the Streamlit dashboard. This helps the audience understand that the project is not only a notebook but a small reproducible system.

For the solution overview, walk through the pipeline: data is downloaded, cached, cleaned, enriched with features, stored in SQLite, visualized, summarized, and then displayed in the dashboard. Close by saying the same flow can be rerun from the command line, which supports the demo and GitHub review.

## Member 2: Slides 5-8
Start with the tool stack. Explain that Python was selected because it has a strong data ecosystem. yfinance provides quick access to public market data, pandas and NumPy handle transformations, SQLite keeps the processed data queryable, and Matplotlib, Seaborn, and Streamlit provide visuals and dashboarding.

For features, focus on why each feature exists. Caching avoids repeated API calls during demos. Daily return and price direction make movement measurable. Moving averages smooth daily noise. Rolling volatility helps discuss risk. Monthly aggregation gives a higher-level trend summary that is easier to present.

For architecture, describe the folder flow. `data/raw` keeps downloaded inputs, `data/processed` keeps enriched outputs, `data/stock_trends.db` stores SQL-ready tables, `outputs/figures` stores charts, `outputs/reports` stores the generated insights, and `app.py` reads those outputs into Streamlit.

For dataset and preprocessing, mention the default five tickers: AAPL, MSFT, GOOGL, AMZN, and NVDA. The project uses at least two years of daily data. Explain missing value handling, duplicate removal, return calculation, up/down direction labeling, moving averages, volatility, and monthly summaries. Emphasize that preprocessing is what makes the later visuals credible.

## Member 3: Slides 9-12
Begin EDA by explaining that the charts are designed for presentation, not overcrowded analysis. The closing price trend compares tickers over time. The return distribution shows typical daily movement and outlier behavior. The volume trend helps identify periods of unusually high market activity. The correlation heatmap shows whether stocks moved similarly.

For visualization insights, explain moving averages. A 20-day average reacts faster, a 50-day average is more medium-term, and a 200-day average is a longer trend reference. When short-term averages are above medium-term averages, that can describe a stronger recent trend, but it is still historical evidence rather than a prediction.

For GenAI integration, explain the two paths. If an OpenAI key exists, the report is generated through the API using computed metrics. If there is no key, the script still produces a deterministic template report. This keeps the demo reliable and avoids failure during presentation.

For key insights and recommendations, speak carefully. Use phrases such as "historically showed", "in this dataset", and "descriptive pattern". Discuss comparing up-day probabilities, volatility, monthly trends, and correlations. Make clear that the recommendation is to use these metrics for analysis and communication, not as direct trading advice.

## Member 4: Slides 13-15 + Demo Close
For challenges and learnings, focus on practical engineering decisions. API dependency can fail, so raw data is cached. Moving averages need enough history, especially the 200-day average. Charts can become unreadable if too many signals are placed on one slide. Historical probabilities must be presented responsibly.

For the project demo slide, transition into the live system. Show the repository structure first, then run or describe the full pipeline command. Open the dashboard, select different tickers, and point to metrics, trend charts, probability bars, and generated insights. Then show `sql/sample_queries.sql` to prove the data is queryable.

For conclusion, summarize the completed end-to-end flow: API ingestion, preprocessing, SQLite storage, EDA, probability analysis, GenAI-style reporting, and Streamlit dashboard. For future scope, mention deployment, scheduled refresh, more indicators, benchmark comparison, and research-only model evaluation.

Close the demo by returning to the dashboard and reminding the audience that the project focuses on insights and responsible interpretation. Mention that the GitHub repository contains commands, validation, presentation notes, demo script, and generated artifacts instructions so another trainee can reproduce the work.
