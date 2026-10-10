"""Postgres helpers: schema, inserts, reads."""
import psycopg2
from psycopg2.extras import execute_values

from config import DATABASE_URL, POSTGRES


def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**POSTGRES)


INIT_SQL = """
CREATE TABLE IF NOT EXISTS prices (
    id SERIAL PRIMARY KEY,
    coin TEXT NOT NULL,
    price_usd DOUBLE PRECISION NOT NULL,
    price_inr DOUBLE PRECISION,
    change_24h DOUBLE PRECISION,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_prices_coin_time ON prices (coin, fetched_at DESC);
"""


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(INIT_SQL)


def insert_prices(rows) -> None:
    """rows: iterable of (coin, price_usd, price_inr, change_24h)."""
    rows = list(rows)
    if not rows:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO prices (coin, price_usd, price_inr, change_24h) VALUES %s",
                rows,
            )


def latest_prices():
    """One row per coin: (coin, price_usd, price_inr, change_24h, fetched_at)."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (coin)
                    coin, price_usd, price_inr, change_24h, fetched_at
                FROM prices
                ORDER BY coin, fetched_at DESC
                """
            )
            return cur.fetchall()


def price_history(coin: str, hours: int = 24):
    """(fetched_at, price_usd) pairs for one coin, oldest first."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT fetched_at, price_usd FROM prices
                WHERE coin = %s
                  AND fetched_at > NOW() - (%s || ' hours')::INTERVAL
                ORDER BY fetched_at
                """,
                (coin, hours),
            )
            return cur.fetchall()
