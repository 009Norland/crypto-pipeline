from checks import check_counts, check_rows
from extract import fetch_prices
from load import load_prices
from transform import build_model

COINS = ("bitcoin", "ethereum", "solana", "cardano", "dogecoin")

def run():
    rows = fetch_prices(coin_ids=COINS)
    check_rows(rows, COINS)
    load_prices(rows)
    build_model()
    check_counts()

if __name__ == "__main__":
   run()