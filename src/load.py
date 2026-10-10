import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()  # finds the .env file in the project root

DB_URL = URL.create(
    "postgresql+psycopg2",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.environ["POSTGRES_DB"],
)
engine = create_engine(DB_URL)

INSERT_SQL = text("""
    INSERT INTO raw_prices (coin_id, price, market_cap, volume_24h, fetched_at)
    VALUES (:coin_id, :price, :market_cap, :volume_24h, :fetched_at)
    ON CONFLICT (coin_id, fetched_at) DO NOTHING
""")


def load_prices(rows):
    """Insert rows into raw_prices. Re-running with the same data is safe."""
    with engine.begin() as conn:
        conn.execute(INSERT_SQL, rows)
    print(f"Loaded {len(rows)} rows")