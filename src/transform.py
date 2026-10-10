from pathlib import Path

from load import engine

MODEL_SQL = Path(__file__).resolve().parent.parent / "sql" / "model.sql"


def build_model():
    """Run sql/model.sql to refresh dim_coin and fact_price from raw_prices."""
    sql = MODEL_SQL.read_text()
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print("Warehouse model updated")