"""Poll CoinGecko every FETCH_INTERVAL_SEC and store prices in Postgres.

Run:  python src/fetch_prices.py        (or via docker compose)
"""
import logging
import time

import requests

from config import COINGECKO_URL, COINS, FETCH_INTERVAL_SEC
from db import init_db, insert_prices

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def fetch_once():
    """Return [(coin, price_usd, price_inr, change_24h), ...]."""
    params = {
        "ids": ",".join(COINS),
        "vs_currencies": "usd,inr",
        "include_24hr_change": "true",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    rows = []
    for coin in COINS:
        quote = data.get(coin, {})
        if "usd" not in quote:
            logging.warning("No USD quote for %s, skipping", coin)
            continue
        rows.append((coin, quote["usd"], quote.get("inr"), quote.get("usd_24h_change")))
    return rows


def main() -> None:
    init_db()
    logging.info("DB ready. Polling %s every %ss.", COINS, FETCH_INTERVAL_SEC)
    while True:
        try:
            rows = fetch_once()
            insert_prices(rows)
            logging.info("Inserted %d rows.", len(rows))
        except Exception:
            logging.exception("Fetch cycle failed; retrying next interval.")
        time.sleep(FETCH_INTERVAL_SEC)


if __name__ == "__main__":
    main()
