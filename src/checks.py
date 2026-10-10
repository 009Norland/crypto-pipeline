from sqlalchemy import text

from load import engine


class DataQualityError(Exception):
    """Raised when data fails a quality check."""


def check_rows(rows, expected_coins):
    """Validate freshly fetched rows before they are loaded."""
    returned = {r["coin_id"] for r in rows}
    missing = set(expected_coins) - returned
    if missing:
        raise DataQualityError(f"Coins missing from API response: {sorted(missing)}")

    for r in rows:
        if r["price"] is None or r["price"] <= 0:
            raise DataQualityError(f"Invalid price for {r['coin_id']}: {r['price']}")


def check_counts():
    """Confirm the fact table has as many rows as the raw table."""
    with engine.connect() as conn:
        raw = conn.execute(text("SELECT COUNT(*) FROM raw_prices")).scalar()
        fact = conn.execute(text("SELECT COUNT(*) FROM fact_price")).scalar()
    if raw != fact:
        raise DataQualityError(f"Row count mismatch: raw={raw}, fact={fact}")