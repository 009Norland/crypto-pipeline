import requests
from datetime import datetime, timezone

BASE_URL = "https://api.coingecko.com/api/v3"


def fetch_prices(coin_ids=("bitcoin", "ethereum", "solana"), vs_currency="usd"):
    """Fetch current prices for the given coins and return a list of dicts."""
    resp = requests.get(
        f"{BASE_URL}/simple/price",
        params={
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
        },
        timeout=10,
    )
    resp.raise_for_status()

    fetched_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "coin_id": coin,
            "price": data[vs_currency],
            "market_cap": data.get(f"{vs_currency}_market_cap"),
            "volume_24h": data.get(f"{vs_currency}_24h_vol"),
            "fetched_at": fetched_at,
        }
        for coin, data in resp.json().items()
    ]


if __name__ == "__main__":
    for row in fetch_prices():
        print(row)