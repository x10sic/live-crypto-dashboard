"""Central settings, read from environment (see .env.example)."""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # env vars still work; .env file just won't auto-load

POSTGRES = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "dbname": os.getenv("POSTGRES_DB", "crypto"),
    "user": os.getenv("POSTGRES_USER", "crypto"),
    "password": os.getenv("POSTGRES_PASSWORD", "crypto"),
}

# Full connection string (e.g. Neon). When set, it overrides POSTGRES_* above.
# Neon strings already carry ?sslmode=require — keep it in the URL.
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Cloud mode (Streamlit Cloud has no background worker): the app itself
# fetches CoinGecko and stores prices on each refresh cycle, so it is
# self-feeding. Local/Docker flow is unchanged when this is false.
CLOUD_MODE = os.getenv("CLOUD_MODE", "false").lower() in ("1", "true", "yes")

COINS = [c.strip() for c in os.getenv("COINS", "bitcoin,ethereum,solana").split(",") if c.strip()]
FETCH_INTERVAL_SEC = int(os.getenv("FETCH_INTERVAL_SEC", "60"))
DASHBOARD_REFRESH_SEC = int(os.getenv("DASHBOARD_REFRESH_SEC", "60"))

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
