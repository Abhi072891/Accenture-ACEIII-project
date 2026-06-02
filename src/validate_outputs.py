import argparse
import sqlite3
from pathlib import Path

from src.config import DB_PATH, FIGURES_DIR, PROCESSED_DIR, REPORTS_DIR, RAW_DIR


REQUIRED_FIGURES = [
    "closing_price_trend.png",
    "moving_average_trend.png",
    "daily_returns_distribution.png",
    "volume_trend.png",
    "correlation_heatmap.png",
    "probability_up_down_by_ticker.png",
]


def require_file(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty required file: {path}")


def validate() -> None:
    require_file(RAW_DIR / "all_tickers_daily.csv")
    require_file(PROCESSED_DIR / "stock_prices_features.csv")
    require_file(PROCESSED_DIR / "monthly_summary.csv")
    require_file(DB_PATH)
    require_file(REPORTS_DIR / "daily_insights.md")
    for figure in REQUIRED_FIGURES:
        require_file(FIGURES_DIR / figure)

    with sqlite3.connect(DB_PATH) as conn:
        daily_rows = conn.execute("SELECT COUNT(*) FROM stock_prices").fetchone()[0]
        monthly_rows = conn.execute("SELECT COUNT(*) FROM monthly_summary").fetchone()[0]
        ticker_count = conn.execute("SELECT COUNT(DISTINCT ticker) FROM stock_prices").fetchone()[0]
    if daily_rows < 1_000 or monthly_rows < 24 or ticker_count < 3:
        raise ValueError(
            f"Unexpected database size: {daily_rows} daily rows, {monthly_rows} monthly rows, {ticker_count} tickers."
        )
    print("Validation passed.")
    print(f"Daily rows: {daily_rows:,}; monthly rows: {monthly_rows:,}; tickers: {ticker_count}")


if __name__ == "__main__":
    argparse.ArgumentParser(description="Validate generated data, database, charts, and reports.").parse_args()
    validate()
