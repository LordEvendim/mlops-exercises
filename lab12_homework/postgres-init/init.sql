CREATE TABLE IF NOT EXISTS exchange_rates (
    symbol VARCHAR(10),
    exchange_rate FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_name VARCHAR(100),
    training_set_size INT,
    test_mae FLOAT
);