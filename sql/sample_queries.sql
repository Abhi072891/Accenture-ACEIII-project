-- Average daily return by ticker
SELECT
    ticker,
    ROUND(AVG(daily_return) * 100, 4) AS avg_daily_return_pct
FROM stock_prices
WHERE daily_return IS NOT NULL
GROUP BY ticker
ORDER BY avg_daily_return_pct DESC;

-- Highest volume days
SELECT
    ticker,
    date,
    close,
    CAST(volume AS INTEGER) AS volume
FROM stock_prices
ORDER BY volume DESC
LIMIT 15;

-- Moving average crossover points: 20-day MA crossing 50-day MA
WITH signals AS (
    SELECT
        ticker,
        date,
        close,
        ma_20,
        ma_50,
        CASE
            WHEN ma_20 > ma_50 THEN 1
            WHEN ma_20 < ma_50 THEN -1
            ELSE 0
        END AS signal
    FROM stock_prices
    WHERE ma_20 IS NOT NULL AND ma_50 IS NOT NULL
),
crossovers AS (
    SELECT
        *,
        LAG(signal) OVER (PARTITION BY ticker ORDER BY date) AS previous_signal
    FROM signals
)
SELECT
    ticker,
    date,
    close,
    ROUND(ma_20, 2) AS ma_20,
    ROUND(ma_50, 2) AS ma_50,
    CASE
        WHEN signal = 1 THEN 'bullish crossover'
        WHEN signal = -1 THEN 'bearish crossover'
    END AS crossover_type
FROM crossovers
WHERE previous_signal IS NOT NULL
  AND signal != previous_signal
  AND signal != 0
ORDER BY date DESC;

-- Probability of price increase by ticker
SELECT
    ticker,
    ROUND(AVG(CASE WHEN price_direction = 'up' THEN 1.0 ELSE 0.0 END) * 100, 2) AS probability_up_pct,
    ROUND(AVG(CASE WHEN price_direction = 'down' THEN 1.0 ELSE 0.0 END) * 100, 2) AS probability_down_pct
FROM stock_prices
WHERE price_direction IN ('up', 'down')
GROUP BY ticker
ORDER BY probability_up_pct DESC;

-- Monthly trend summary
SELECT
    ticker,
    month,
    trading_days,
    ROUND(monthly_return * 100, 2) AS monthly_return_pct,
    up_days,
    down_days,
    ROUND(probability_up * 100, 2) AS probability_up_pct,
    ROUND(avg_volume, 0) AS avg_volume
FROM monthly_summary
ORDER BY month DESC, ticker;
