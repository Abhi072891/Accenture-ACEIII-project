import sqlite3

import pandas as pd
import streamlit as st

from src.config import DB_PATH, DEFAULT_PERIOD, DEFAULT_TICKERS, FIGURES_DIR, REPORTS_DIR


st.set_page_config(page_title="Stock Market Trend Analysis", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="stMetricLabel"] {
        color: #475569;
    }
    .demo-note {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0 1rem 0;
    }
    .caution-note {
        background: #fff7ed;
        border-left: 4px solid #ea580c;
        padding: 0.8rem 1rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    with sqlite3.connect(DB_PATH) as conn:
        daily = pd.read_sql_query("SELECT * FROM stock_prices", conn, parse_dates=["date"])
        monthly = pd.read_sql_query("SELECT * FROM monthly_summary", conn)
    return daily, monthly


@st.cache_resource(show_spinner=False)
def bootstrap_database_if_needed() -> str:
    if DB_PATH.exists():
        return "existing"

    from src.eda import generate_charts
    from src.genai_insights import generate_insights
    from src.ingest import ingest_data
    from src.preprocess import preprocess

    ingest_data(DEFAULT_TICKERS, period=DEFAULT_PERIOD)
    preprocess()
    generate_charts()
    generate_insights()
    return "generated"


def read_insights() -> str:
    path = REPORTS_DIR / "daily_insights.md"
    if path.exists():
        return path.read_text()
    return "Run `python -m src.genai_insights` to generate the insights report."


FIGURE_GUIDE = {
    "closing_price_trend.png": {
        "label": "Closing Price Trend",
        "meaning": "Compares long-run movement across the selected stocks and frames the overall trend discussion.",
    },
    "daily_returns_distribution.png": {
        "label": "Daily Returns Distribution",
        "meaning": "Explains typical daily movement, spread, and outlier behavior without implying prediction.",
    },
    "volume_trend.png": {
        "label": "Volume Trend",
        "meaning": "Highlights participation spikes that can coincide with news, earnings, or high-volatility periods.",
    },
    "correlation_heatmap.png": {
        "label": "Correlation Heatmap",
        "meaning": "Shows whether tickers historically moved together, useful for diversification context.",
    },
    "probability_up_down_by_ticker.png": {
        "label": "Historical Up/Down Probability",
        "meaning": "Summarizes empirical direction frequency. It is descriptive, not a trading forecast.",
    },
}


def format_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value * 100:.2f}%"


st.title("Stock Market Trend Analysis")
st.caption("Historical OHLCV trend exploration with SQLite, EDA charts, probability analysis, and GenAI-style insights.")

try:
    if not DB_PATH.exists():
        with st.spinner("First run setup: downloading stock data and building the SQLite database..."):
            bootstrap_database_if_needed()
        st.success("Demo database generated for this Streamlit environment.")
    else:
        bootstrap_database_if_needed()
    daily, monthly = load_data()
except Exception as exc:
    st.error("The dashboard could not prepare its data.")
    st.exception(exc)
    st.info(
        "On Streamlit Cloud, check that `requirements.txt` installed successfully and that outbound access to "
        "Yahoo Finance is available. Locally, run `python -m src.run_pipeline` from the repository root."
    )
    st.stop()

tickers = sorted(daily["ticker"].unique())
st.sidebar.title("Dashboard Controls")
selected = st.sidebar.selectbox("Ticker", tickers)
st.sidebar.markdown(
    """
    **About This Tool**
    Use this interface to query historical market data, evaluate volatility profiles, and generate AI-driven insights for selected tech assets.
    """
)
st.sidebar.divider()
st.sidebar.caption("System architecture relies on SQLite cache, pre-computed EDA artifacts, and GenAI markdown reports.")

selected_daily = daily[daily["ticker"] == selected].sort_values("date")
selected_monthly = monthly[monthly["ticker"] == selected].sort_values("month")
latest = selected_daily.iloc[-1]
first = selected_daily.iloc[0]
period_return = latest["close"] / first["close"] - 1

up_days = (selected_daily["price_direction"] == "up").sum()
down_days = (selected_daily["price_direction"] == "down").sum()
direction_days = up_days + down_days
prob_up = up_days / direction_days if direction_days else 0
prob_down = down_days / direction_days if direction_days else 0
latest_signal = str(latest["ma_signal"]).replace("_", " ")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Close", f"${latest['close']:.2f}")
col2.metric("Daily Return", format_pct(latest["daily_return"]))
col3.metric("Historical Up Days", f"{prob_up * 100:.1f}%")
volatility = latest["rolling_volatility_20"]
col4.metric("20-Day Volatility", format_pct(volatility))

st.markdown(
    f"""
    <div class="demo-note">
    <strong>{selected} readout:</strong> across this dataset the period return is <strong>{period_return * 100:.1f}%</strong>,
    the latest moving-average signal is <strong>{latest_signal}</strong>, and historical up days are
    <strong>{prob_up * 100:.1f}%</strong>. Use this as historical context, not a price prediction.
    </div>
    """,
    unsafe_allow_html=True,
)

tab_trend, tab_probability, tab_insights, tab_figures, tab_limitations = st.tabs(
    ["Trend", "Probability", "Insights", "Static Analytics", "Limitations"]
)

with tab_trend:
    chart_col, note_col = st.columns([2.2, 1])
    with chart_col:
        st.subheader(f"{selected} Price Trend and Moving Averages")
        chart_data = selected_daily.set_index("date")[["close", "ma_20", "ma_50", "ma_200"]]
        st.line_chart(chart_data)
    with note_col:
        st.subheader("Trend Context")
        st.write(
            "Moving averages reduce day-to-day noise. The 20-day line reacts fastest, the 50-day line "
            "shows medium-term direction, and the 200-day line gives a longer trend reference."
        )
        st.write(
            f"For {selected}, the current signal is **{latest_signal}**, which describes the latest "
            "relationship between the 20-day and 50-day averages."
        )
    st.subheader("Monthly Return")
    monthly_chart = selected_monthly.set_index("month")["monthly_return"] * 100
    st.bar_chart(monthly_chart)
    st.caption("Aggregated monthly returns visualize broader macroeconomic momentum.")

with tab_probability:
    chart_col, table_col = st.columns([1, 1.4])
    with chart_col:
        st.subheader("Historical Direction Frequency")
        probability = pd.DataFrame(
            {"Direction": ["Up", "Down"], "Probability": [prob_up * 100, prob_down * 100]}
        ).set_index("Direction")
        st.bar_chart(probability)
        st.caption("Empirical frequency across completed trading days in the dataset.")
    with table_col:
        st.subheader("Last 12 Monthly Summaries")
        display_monthly = selected_monthly[
            ["month", "trading_days", "monthly_return", "up_days", "down_days", "probability_up"]
        ].tail(12).copy()
        display_monthly["monthly_return"] = display_monthly["monthly_return"].map(lambda value: f"{value * 100:.2f}%")
        display_monthly["probability_up"] = display_monthly["probability_up"].map(lambda value: f"{value * 100:.1f}%")
        st.dataframe(display_monthly, width="stretch", hide_index=True)
    st.markdown(
        """
        <div class="caution-note">
        <strong>Methodology Note:</strong> Probability here indicates historical up/down frequency. It does not estimate
        future return, guarantee direction, or replace rigorous risk analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_insights:
    st.subheader("AI-Generated Insight Report")
    st.write(
        "This dynamic report synthesizes computed metrics (trend, volatility, moving-average signals) into natural language, utilizing a deterministic fallback for guaranteed uptime."
    )
    st.markdown(read_insights())

with tab_figures:
    st.subheader("Static Analytical Figures")
    st.write("These pre-computed charts provide additional context on volatility distribution, moving averages, and asset correlation.")
    for filename, details in FIGURE_GUIDE.items():
        path = FIGURES_DIR / filename
        if path.exists():
            st.markdown(f"**{details['label']}**")
            st.caption(details["meaning"])
            st.image(str(path), caption=filename)

with tab_limitations:
    st.subheader("Limitations and Responsible Use")
    st.markdown(
        """
        - This platform analyzes historical OHLCV data only.
        - It is not financial advice and does not recommend buying, selling, or holding any asset.
        - Historical up/down probability is a descriptive frequency, not a reliable price prediction model.
        - Upstream market data can be delayed, revised, unavailable, or affected by ticker-specific corporate actions.
        - Moving averages and historical volatility are lagging indicators and should be interpreted alongside broader market context.
        """
    )