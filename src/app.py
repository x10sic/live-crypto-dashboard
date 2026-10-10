"""Live crypto dashboard.

Run:  streamlit run src/app.py        (or via docker compose → :8501)
"""
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from config import CLOUD_MODE, DASHBOARD_REFRESH_SEC
from db import init_db, insert_prices, latest_prices, price_history

st.set_page_config(page_title="Live Crypto Dashboard", layout="wide")
st.title("Live Crypto Dashboard")


@st.cache_data(ttl=DASHBOARD_REFRESH_SEC)
def load_latest() -> pd.DataFrame:
    init_db()
    if CLOUD_MODE:
        # No background worker on Streamlit Cloud: fetch + store inline.
        # Guarded so a failed fetch never breaks the page.
        try:
            from fetch_prices import fetch_once

            insert_prices(fetch_once())
        except Exception:
            pass
    rows = latest_prices()
    return pd.DataFrame(
        rows, columns=["coin", "price_usd", "price_inr", "change_24h", "fetched_at"]
    )


@st.cache_data(ttl=DASHBOARD_REFRESH_SEC)
def load_history(coin: str) -> pd.DataFrame:
    rows = price_history(coin, hours=24)
    df = pd.DataFrame(rows, columns=["fetched_at", "price_usd"])
    if not df.empty:
        df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    return df


df = load_latest()

if df.empty:
    st.warning("No data yet — the fetcher is still warming up. Wait a minute, then refresh.")
    st.stop()

cards = st.columns(len(df))
for card, (_, row) in zip(cards, df.iterrows()):
    change = row["change_24h"]
    delta = f"{change:.2f}% (24h)" if pd.notna(change) else None
    card.metric(row["coin"].title(), f"${row['price_usd']:,.2f}", delta)

coin = st.selectbox("Coin", df["coin"].tolist())
hist = load_history(coin)
if hist.empty:
    st.info("Not enough history yet for a chart — check back in a few minutes.")
else:
    fig = px.line(hist, x="fetched_at", y="price_usd",
                  title=f"{coin.title()} — last 24h (USD)")
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"Prices via CoinGecko · refreshes every ~{DASHBOARD_REFRESH_SEC}s")

time.sleep(DASHBOARD_REFRESH_SEC)
st.rerun()
