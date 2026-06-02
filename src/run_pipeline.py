import argparse

from src.eda import generate_charts
from src.genai_insights import generate_insights
from src.ingest import ingest_data
from src.preprocess import preprocess


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full stock trend analysis pipeline.")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"])
    parser.add_argument("--period", default="2y")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    ingest_data(args.tickers, period=args.period, force=args.force)
    preprocess()
    generate_charts()
    generate_insights()


if __name__ == "__main__":
    main()
