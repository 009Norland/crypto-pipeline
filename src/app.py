import re

from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy import text

from load import engine
from pipeline import run

app = Flask(__name__, static_folder="static")

ORDER = {"fact_price": "fetched_at DESC", "raw_prices": "fetched_at DESC", "dim_coin": "coin_key"}


def clean(row):
    """Make database values JSON-friendly."""
    return [
        float(v) if hasattr(v, "as_tuple") else v.isoformat() if hasattr(v, "isoformat") else v
        for v in row
    ]


def rows(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return list(result.keys()), [clean(r) for r in result.fetchall()]


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/overview")
def overview():
    _, data = rows("""
        SELECT d.coin_id, f.fetched_at, f.price
        FROM fact_price f JOIN dim_coin d USING (coin_key)
        WHERE f.fetched_at > now() - interval '7 days'
        ORDER BY f.fetched_at
    """)
    series = {}
    for coin, ts, price in data:
        series.setdefault(coin, []).append([ts, price])
    _, [[snapshots]] = rows("SELECT COUNT(DISTINCT fetched_at) FROM fact_price")
    latest = max((s[-1][0] for s in series.values()), default=None)
    return jsonify(series=series, snapshots=snapshots, latest=latest)


@app.post("/api/run")
def trigger():
    try:
        run()
    except Exception as e:
        return jsonify(error=str(e)), 500
    return jsonify(ok=True)


@app.post("/api/query")
def query():
    sql = (request.get_json(silent=True) or {}).get("sql", "").strip().rstrip(";").strip()
    if not re.match(r"(?is)^(select|with)\b", sql) or ";" in sql:
        return jsonify(error="Only a single SELECT question is allowed here."), 400
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            conn.exec_driver_sql("SET LOCAL statement_timeout = 5000")
            result = conn.execute(text(sql))
            cols = list(result.keys())
            data = [clean(r) for r in result.fetchmany(200)]
    except Exception as e:
        return jsonify(error=str(getattr(e, "orig", e)).strip()), 400
    return jsonify(cols=cols, rows=data)


@app.get("/api/table/<name>")
def table(name):
    if name not in ORDER:
        return jsonify(error="Unknown table"), 404
    cols, data = rows(f"SELECT * FROM {name} ORDER BY {ORDER[name]} LIMIT 50")
    return jsonify(cols=cols, rows=data)


if __name__ == "__main__":
    app.run(port=5000)
