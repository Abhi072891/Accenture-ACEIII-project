import argparse
import os

import pandas as pd

from src.config import PROCESSED_DIR, REPORTS_DIR, ensure_directories


DISCLAIMER = "This is historical pattern analysis for education only and is not financial advice."


def load_metrics() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily_path = PROCESSED_DIR / "stock_prices_features.csv"
    monthly_path = PROCESSED_DIR / "monthly_summary.csv"
    if not daily_path.exists() or not monthly_path.exists():
        raise FileNotFoundError("Processed metrics not found. Run `python -m src.preprocess` first.")
    return pd.read_csv(daily_path, parse_dates=["date"]), pd.read_csv(monthly_path)


def summarize_metrics(daily: pd.DataFrame, monthly: pd.DataFrame) -> dict:
    latest_rows = daily.sort_values("date").groupby("ticker").tail(1)
    first_rows = daily.sort_values("date").groupby("ticker").head(1).set_index("ticker")
    direction = daily[daily["price_direction"].isin(["up", "down"])]
    probabilities = (
        direction.groupby("ticker")["price_direction"]
        .value_counts(normalize=True)
        .rename("probability")
        .reset_index()
    )
    up_probability = probabilities[probabilities["price_direction"] == "up"].set_index("ticker")["probability"]
    return_summary = (
        daily.dropna(subset=["daily_return"])
        .groupby("ticker")["daily_return"]
        .agg(avg_daily_return="mean", max_daily_return="max", min_daily_return="min")
    )
    return {
        "latest_date": daily["date"].max().date().isoformat(),
        "latest_rows": latest_rows,
        "first_rows": first_rows,
        "up_probability": up_probability,
        "monthly": monthly,
        "return_summary": return_summary,
    }


def template_insights(metrics: dict) -> str:
    lines = [
        "# Daily Stock Insights",
        "",
        f"Generated for latest available trading date: **{metrics['latest_date']}**.",
        "",
    ]
    for _, row in metrics["latest_rows"].sort_values("ticker").iterrows():
        ticker = row["ticker"]
        daily_return = row["daily_return"] * 100 if pd.notna(row["daily_return"]) else 0
        volatility = row["rolling_volatility_20"] * 100 if pd.notna(row["rolling_volatility_20"]) else None
        up_probability = metrics["up_probability"].get(ticker, float("nan")) * 100
        start_close = metrics["first_rows"].loc[ticker, "close"]
        period_return = (row["close"] / start_close - 1) * 100
        return_summary = metrics["return_summary"].loc[ticker]
        signal = row["ma_signal"].replace("_", " ")
        trend = "positive" if daily_return > 0 else "negative" if daily_return < 0 else "flat"
        regime = (
            "recent prices are running above the medium-term trend"
            if row["ma_signal"] == "short_term_above_medium"
            else "recent prices are below the medium-term trend"
            if row["ma_signal"] == "short_term_below_medium"
            else "there is not enough moving-average history for a strong trend regime"
        )
        volatility_note = (
            f"20-day rolling volatility is {volatility:.2f}%."
            if volatility is not None
            else "Volatility history is still forming."
        )
        lines.extend(
            [
                f"## {ticker}",
                f"- Trend summary: latest close was {row['close']:.2f}; the latest daily move was {trend} at {daily_return:.2f}%, and the full-period return was {period_return:.1f}%.",
                f"- Chart meaning: the price and moving-average chart indicates that {regime}.",
                f"- Volatility note: {volatility_note} The return distribution should be used to explain typical movement and outlier days.",
                f"- Probability context: historical up-day probability was {up_probability:.1f}%; this is frequency analysis, not forecast confidence.",
                f"- Risk/caution: observed daily returns ranged from {return_summary['min_daily_return'] * 100:.2f}% to {return_summary['max_daily_return'] * 100:.2f}%, so short-term movements can reverse quickly.",
                "",
            ]
        )
    lines.extend(
        [
            "## How to Use These Insights in the Presentation",
            "- Use the closing-price chart to introduce broad trend direction.",
            "- Use moving averages to explain trend smoothing and lag.",
            "- Use return distribution and volatility to discuss risk and outliers.",
            "- Use probability charts only as historical frequency evidence.",
            "",
            "## Disclaimer",
            DISCLAIMER,
            "It is not a reliable price prediction system.",
            "",
        ]
    )
    return "\n".join(lines)


# def openai_insights(metrics: dict) -> str | None:
#     if not os.getenv("OPENAI_API_KEY"):
#         return None
#     try:
#         from openai import OpenAI

#         latest = metrics["latest_rows"][
#             ["ticker", "date", "close", "daily_return", "rolling_volatility_20", "ma_signal"]
#         ].to_dict(orient="records")
#         client = OpenAI()
#         response = client.chat.completions.create(
#             model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "Write concise educational stock-market trend insights from computed metrics. "
#                         "Explain what charts mean, not only what they show. Do not provide investment advice "
#                         "or buy/sell recommendations."
#                     ),
#                 },
#                 {
#                     "role": "user",
#                     "content": (
#                         "Create a Markdown report with trend summary, volatility note, moving average signal, "
#                         "chart interpretation, risk/caution note, and disclaimer that this is not reliable "
#                         f"price prediction. Metrics: {latest}"
#                     ),
#                 },
#             ],
#             temperature=0.2,
#         )
#         content = response.choices[0].message.content
#         if content and DISCLAIMER.lower() not in content.lower():
#             content = f"{content}\n\n## Disclaimer\n{DISCLAIMER}\n"
#         return content
#     except Exception as exc:
#         print(f"Warning: OpenAI insight generation failed; using template fallback. Reason: {exc}")
#         return None

def gemini_insights(metrics: dict) -> str | None:
    if not os.getenv("GEMINI_API_KEY"):
        return None
    try:
        # Import the new, officially supported SDK
        from google import genai
        
        # The new client automatically picks up the GEMINI_API_KEY environment variable
        client = genai.Client()

        latest = metrics["latest_rows"][
            ["ticker", "date", "close", "daily_return", "rolling_volatility_20", "ma_signal"]
        ].to_dict(orient="records")
        
        prompt = (
            "You are a financial data assistant. Write concise educational stock-market trend insights from computed metrics. "
            "Explain what charts mean, not only what they show. Do not provide investment advice "
            "or buy/sell recommendations.\n\n"
            "Create a Markdown report with trend summary, volatility note, moving average signal, "
            "chart interpretation, risk/caution note, and disclaimer that this is not reliable "
            f"price prediction. Metrics: {latest}"
        )
        
        # We will use gemini-2.5-flash, the current standard for fast, high-quality text generation
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        content = response.text
        
        if content and DISCLAIMER.lower() not in content.lower():
            content = f"{content}\n\n## Disclaimer\n{DISCLAIMER}\n"
        return content
    except Exception as exc:
        print(f"Warning: Gemini insight generation failed; using template fallback. Reason: {exc}")
        return None

def generate_insights() -> str:
    ensure_directories()
    daily, monthly = load_metrics()
    metrics = summarize_metrics(daily, monthly)
    # report = openai_insights(metrics) or template_insights(metrics)
    report = gemini_insights(metrics) or template_insights(metrics)
    output_path = REPORTS_DIR / "daily_insights.md"
    output_path.write_text(report)
    print(f"Saved insights report to {output_path}")
    return report


if __name__ == "__main__":
    argparse.ArgumentParser(description="Generate daily stock insights with OpenAI or fallback templates.").parse_args()
    generate_insights()
