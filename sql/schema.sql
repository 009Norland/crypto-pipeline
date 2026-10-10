CREATE TABLE IF NOT EXISTS raw_prices (
    coin_id     TEXT        NOT NULL,
    price       NUMERIC     NOT NULL,
    market_cap  NUMERIC,
    volume_24h  NUMERIC,
    fetched_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (coin_id, fetched_at)
);