CREATE TABLE IF NOT EXISTS exchange_rates (
    symbol VARCHAR(10),
    exchange_rate FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);