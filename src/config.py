from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = ROOT_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
REPORTS_DIR = OUTPUTS_DIR / "reports"
SQL_DIR = ROOT_DIR / "sql"
DB_PATH = DATA_DIR / "stock_trends.db"

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
DEFAULT_PERIOD = "2y"


def ensure_directories() -> None:
    for directory in [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        FIGURES_DIR,
        REPORTS_DIR,
        SQL_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
