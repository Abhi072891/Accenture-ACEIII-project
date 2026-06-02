import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FIGURES_DIR, PROCESSED_DIR, ensure_directories


PALETTE = sns.color_palette("tab10")


def ticker_palette(data: pd.DataFrame) -> dict[str, tuple[float, float, float]]:
    tickers = sorted(data["ticker"].unique())
    return {ticker: PALETTE[index % len(PALETTE)] for index, ticker in enumerate(tickers)}


def load_processed() -> pd.DataFrame:
    path = PROCESSED_DIR / "stock_prices_features.csv"
    if not path.exists():
        raise FileNotFoundError("Processed data not found. Run `python -m src.preprocess` first.")
    return pd.read_csv(path, parse_dates=["date"])


def save_figure(filename: str) -> None:
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close()


def plot_closing_price(data: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 6))
    sns.lineplot(data=data, x="date", y="close", hue="ticker", palette=ticker_palette(data), linewidth=1.8)
    plt.title("Closing Price Trend")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend(title="Ticker", ncol=3)
    save_figure("closing_price_trend.png")


def plot_moving_average(data: pd.DataFrame) -> None:
    latest_ticker = data["ticker"].iloc[0]
    ticker_data = data[data["ticker"] == latest_ticker].tail(260)
    plt.figure(figsize=(11, 6))
    plt.plot(ticker_data["date"], ticker_data["close"], label="Close", linewidth=1.6)
    plt.plot(ticker_data["date"], ticker_data["ma_20"], label="20-day MA", linewidth=1.4)
    plt.plot(ticker_data["date"], ticker_data["ma_50"], label="50-day MA", linewidth=1.4)
    plt.plot(ticker_data["date"], ticker_data["ma_200"], label="200-day MA", linewidth=1.4)
    plt.title(f"Moving Average Trend: {latest_ticker}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    save_figure("moving_average_trend.png")


def plot_returns_distribution(data: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 6))
    filtered = data.dropna(subset=["daily_return"]).copy()
    filtered["daily_return_pct"] = filtered["daily_return"] * 100
    sns.histplot(data=filtered, x="daily_return_pct", hue="ticker", bins=45, kde=True, element="step")
    plt.title("Daily Returns Distribution")
    plt.xlabel("Daily Return (%)")
    plt.ylabel("Trading Days")
    save_figure("daily_returns_distribution.png")


def plot_volume(data: pd.DataFrame) -> None:
    sampled = data.copy()
    sampled["volume_millions"] = sampled["volume"] / 1_000_000
    plt.figure(figsize=(11, 6))
    sns.lineplot(
        data=sampled,
        x="date",
        y="volume_millions",
        hue="ticker",
        palette=ticker_palette(sampled),
        linewidth=1.2,
    )
    plt.title("Trading Volume Trend")
    plt.xlabel("Date")
    plt.ylabel("Volume (millions)")
    plt.legend(title="Ticker", ncol=3)
    save_figure("volume_trend.png")


def plot_correlation(data: pd.DataFrame) -> None:
    pivot = data.pivot(index="date", columns="ticker", values="daily_return")
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot.corr(), annot=True, cmap="vlag", center=0, vmin=-1, vmax=1, fmt=".2f")
    plt.title("Daily Return Correlation")
    save_figure("correlation_heatmap.png")


def plot_probability(data: pd.DataFrame) -> None:
    probability = (
        data[data["price_direction"].isin(["up", "down"])]
        .groupby(["ticker", "price_direction"])
        .size()
        .div(data[data["price_direction"].isin(["up", "down"])].groupby("ticker").size(), level="ticker")
        .reset_index(name="probability")
    )
    probability["probability_pct"] = probability["probability"] * 100
    plt.figure(figsize=(9, 6))
    sns.barplot(data=probability, x="ticker", y="probability_pct", hue="price_direction", palette=["#2f855a", "#c2410c"])
    plt.title("Historical Probability of Up/Down Days")
    plt.xlabel("Ticker")
    plt.ylabel("Probability (%)")
    plt.ylim(0, 100)
    plt.legend(title="Direction")
    save_figure("probability_up_down_by_ticker.png")


def generate_charts() -> None:
    ensure_directories()
    sns.set_theme(style="whitegrid", context="talk")
    data = load_processed()
    plot_closing_price(data)
    plot_moving_average(data)
    plot_returns_distribution(data)
    plot_volume(data)
    plot_correlation(data)
    plot_probability(data)
    print(f"Saved EDA figures to {FIGURES_DIR}")


if __name__ == "__main__":
    argparse.ArgumentParser(description="Generate presentation-ready stock EDA charts.").parse_args()
    generate_charts()
