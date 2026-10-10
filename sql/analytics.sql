-- 1. Percent change vs the previous snapshot
SELECT d.coin_id, f.fetched_at, f.price,
       ROUND(((f.price - LAG(f.price) OVER w) / LAG(f.price) OVER w * 100)::numeric, 4) AS pct_change
FROM fact_price f
JOIN dim_coin d USING (coin_key)
WINDOW w AS (PARTITION BY f.coin_key ORDER BY f.fetched_at)
ORDER BY f.fetched_at DESC, d.coin_id
LIMIT 10;

-- 2. Moving average over the last 6 snapshots
SELECT d.coin_id, f.fetched_at, f.price,
       ROUND(AVG(f.price) OVER (
           PARTITION BY f.coin_key ORDER BY f.fetched_at
           ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
       ), 4) AS moving_avg_6
FROM fact_price f
JOIN dim_coin d USING (coin_key)
ORDER BY f.fetched_at DESC, d.coin_id
LIMIT 10;

-- 3. Volatility: standard deviation of snapshot-to-snapshot returns
WITH returns AS (
    SELECT coin_key,
           (price - LAG(price) OVER (PARTITION BY coin_key ORDER BY fetched_at))
             / LAG(price) OVER (PARTITION BY coin_key ORDER BY fetched_at) AS ret
    FROM fact_price
)
SELECT d.coin_id,
       COUNT(r.ret) AS observations,
       ROUND((STDDEV(r.ret) * 100)::numeric, 4) AS volatility_pct
FROM returns r
JOIN dim_coin d USING (coin_key)
WHERE r.ret IS NOT NULL
GROUP BY d.coin_id
ORDER BY volatility_pct DESC;