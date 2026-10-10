CREATE TABLE IF NOT EXISTS dim_coin (
    coin_key  SERIAL PRIMARY KEY,
    coin_id   TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_price (
    coin_key    INT         NOT NULL REFERENCES dim_coin (coin_key),
    price       NUMERIC     NOT NULL,
    market_cap  NUMERIC,
    volume_24h  NUMERIC,
    fetched_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (coin_key, fetched_at)
);

-- Add any new coins
INSERT INTO dim_coin (coin_id)
SELECT DISTINCT coin_id FROM raw_prices
ON CONFLICT (coin_id) DO NOTHING;

-- Copy new price rows into the fact table
INSERT INTO fact_price (coin_key, price, market_cap, volume_24h, fetched_at)
SELECT d.coin_key, r.price, r.market_cap, r.volume_24h, r.fetched_at
FROM raw_prices r
JOIN dim_coin d ON d.coin_id = r.coin_id
ON CONFLICT (coin_key, fetched_at) DO NOTHING;