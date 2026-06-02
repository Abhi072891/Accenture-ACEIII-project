import argparse
from datetime import datetime, timezone

import pandas as pd

from src.config import DEFAULT_PERIOD, DEFAULT_TICKERS, RAW_DIR, ensure_directories


def raw_path(ticker: str) -> str:
    return str(RAW_DIR / f"{ticker.upper()}_daily.csv")


def load_cached_ticker(ticker: str) -> pd.DataFrame | None:
    path = RAW_DIR / f"{ticker.upper()}_daily.csv"
    if not path.exists():
        return None
    data = pd.read_csv(path, parse_dates=["date"])
    if data.empty:
        return None
    return data


def normalize_downloaded_frame(frame: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [col[0].lower() for col in frame.columns]
    else:
        frame.columns = [str(col).lower() for col in frame.columns]

    # frame = frame.reset_index().rename(columns={"date": "date", "datetime": "date"})
    frame = frame.reset_index().rename(columns={"Date": "date", "Datetime": "date", "date": "date", "datetime": "date"})
    if "date" not in frame.columns and "index" in frame.columns:
        frame = frame.rename(columns={"index": "date"})

    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{ticker}: missing expected columns after download: {missing}")

    result = frame[required].copy()
    result["date"] = pd.to_datetime(result["date"]).dt.date
    result["ticker"] = ticker.upper()
    result["downloaded_at_utc"] = datetime.now(timezone.utc).isoformat()
    return result[["date", "ticker", "open", "high", "low", "close", "volume", "downloaded_at_utc"]]


def fetch_ticker(ticker: str, period: str = DEFAULT_PERIOD, force: bool = False) -> pd.DataFrame:
    ensure_directories()
    ticker = ticker.upper()
    cached = load_cached_ticker(ticker)
    if cached is not None and not force:
        return cached

    try:
        import yfinance as yf

        downloaded = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if downloaded.empty:
            raise ValueError("download returned no rows")
        data = normalize_downloaded_frame(downloaded, ticker)
        data.to_csv(raw_path(ticker), index=False)
        return data
    except Exception as exc:
        if cached is not None:
            print(f"Warning: API fetch failed for {ticker}; using cached file. Reason: {exc}")
            return cached
        raise RuntimeError(
            f"Could not fetch {ticker} and no cache exists at {raw_path(ticker)}. "
            "Check internet access, ticker symbol, or rerun after placing a compatible CSV in data/raw."
        ) from exc


def ingest_data(tickers: list[str], period: str = DEFAULT_PERIOD, force: bool = False) -> pd.DataFrame:
    frames = [fetch_ticker(ticker, period=period, force=force) for ticker in tickers]
    combined = pd.concat(frames, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    combined = combined.sort_values(["ticker", "date"]).reset_index(drop=True)
    combined.to_csv(RAW_DIR / "all_tickers_daily.csv", index=False)
    print(f"Ingested {len(combined):,} rows for {len(tickers)} tickers.")
    return combined


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and cache daily OHLCV stock data.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    parser.add_argument("--period", default=DEFAULT_PERIOD)
    parser.add_argument("--force", action="store_true", help="Refresh cached raw ticker files.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ingest_data(args.tickers, period=args.period, force=args.force)
