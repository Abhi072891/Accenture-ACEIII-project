import argparse
import sqlite3

import numpy as np
import pandas as pd

from src.config import DB_PATH, PROCESSED_DIR, RAW_DIR, SQL_DIR, ensure_directories


def load_raw_data() -> pd.DataFrame:
    combined_path = RAW_DIR / "all_tickers_daily.csv"
    if combined_path.exists():
        return pd.read_csv(combined_path, parse_dates=["date"])

    files = sorted(RAW_DIR.glob("*_daily.csv"))
    files = [path for path in files if path.name != "all_tickers_daily.csv"]
    if not files:
        raise FileNotFoundError("No raw CSV files found. Run `python -m src.ingest` first.")
    return pd.concat([pd.read_csv(path, parse_dates=["date"]) for path in files], ignore_index=True)


def add_features(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expected = {"date", "ticker", "open", "high", "low", "close", "volume"}
    missing = expected.difference(data.columns)
    if missing:
        raise ValueError(f"Raw data is missing required columns: {sorted(missing)}")

    data = data.copy()
    data["date"] = pd.to_datetime(data["date"])
    data = data.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"])
    numeric_columns = ["open", "high", "low", "close", "volume"]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    data[numeric_columns] = data.groupby("ticker", group_keys=False)[numeric_columns].apply(
        lambda group: group.ffill().bfill()
    )
    data = data.dropna(subset=["open", "high", "low", "close", "volume"])

    grouped = data.groupby("ticker", group_keys=False)
    data["daily_return"] = grouped["close"].pct_change()
    data["price_direction"] = np.where(data["daily_return"] > 0, "up", "down")
    data.loc[data["daily_return"].isna(), "price_direction"] = "flat"

    for window in [20, 50, 200]:
        data[f"ma_{window}"] = grouped["close"].transform(lambda series: series.rolling(window).mean())

    data["rolling_volatility_20"] = grouped["daily_return"].transform(
        lambda series: series.rolling(20).std()
    )
    data["ma_signal"] = np.select(
        [
            data["ma_20"].gt(data["ma_50"]),
            data["ma_20"].lt(data["ma_50"]),
        ],
        ["short_term_above_medium", "short_term_below_medium"],
        default="insufficient_history",
    )
    data["month"] = data["date"].dt.to_period("M").astype(str)

    monthly = (
        data.groupby(["ticker", "month"], as_index=False)
        .agg(
            month_start=("date", "min"),
            month_end=("date", "max"),
            trading_days=("date", "count"),
            avg_close=("close", "mean"),
            end_close=("close", "last"),
            monthly_return=("close", lambda values: values.iloc[-1] / values.iloc[0] - 1),
            avg_daily_return=("daily_return", "mean"),
            up_days=("price_direction", lambda values: (values == "up").sum()),
            down_days=("price_direction", lambda values: (values == "down").sum()),
            avg_volume=("volume", "mean"),
        )
        .sort_values(["ticker", "month"])
    )
    monthly["probability_up"] = monthly["up_days"] / monthly["trading_days"]
    monthly["probability_down"] = monthly["down_days"] / monthly["trading_days"]
    return data.reset_index(drop=True), monthly


def write_sqlite(daily: pd.DataFrame, monthly: pd.DataFrame) -> None:
    schema_path = SQL_DIR / "schema.sql"
    with sqlite3.connect(DB_PATH) as conn:
        if schema_path.exists():
            conn.executescript(schema_path.read_text())
        daily.to_sql("stock_prices", conn, if_exists="replace", index=False)
        monthly.to_sql("monthly_summary", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date ON stock_prices(ticker, date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_monthly_summary_ticker_month ON monthly_summary(ticker, month)")


def preprocess() -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_directories()
    daily, monthly = add_features(load_raw_data())
    daily.to_csv(PROCESSED_DIR / "stock_prices_features.csv", index=False)
    monthly.to_csv(PROCESSED_DIR / "monthly_summary.csv", index=False)
    write_sqlite(daily, monthly)
    print(f"Processed {len(daily):,} daily rows and {len(monthly):,} monthly rows.")
    print(f"SQLite database written to {DB_PATH}")
    return daily, monthly


if __name__ == "__main__":
    argparse.ArgumentParser(description="Clean stock data, add features, and write SQLite.").parse_args()
    preprocess()
