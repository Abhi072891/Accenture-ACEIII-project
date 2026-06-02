DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS monthly_summary;

CREATE TABLE stock_prices (
    date TEXT NOT NULL,
    ticker TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    downloaded_at_utc TEXT,
    daily_return REAL,
    price_direction TEXT,
    ma_20 REAL,
    ma_50 REAL,
    ma_200 REAL,
    rolling_volatility_20 REAL,
    ma_signal TEXT,
    month TEXT,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE monthly_summary (
    ticker TEXT NOT NULL,
    month TEXT NOT NULL,
    month_start TEXT,
    month_end TEXT,
    trading_days INTEGER,
    avg_close REAL,
    end_close REAL,
    monthly_return REAL,
    avg_daily_return REAL,
    up_days INTEGER,
    down_days INTEGER,
    avg_volume REAL,
    probability_up REAL,
    probability_down REAL,
    PRIMARY KEY (ticker, month)
);
