"""Scrape a configured site, store prices, alert on drops.

Usage::

    python scripts/run_monitor.py [--config sites/books_demo.yaml] [--min-drop 5]

Schedule it free with Task Scheduler (Windows) or cron (Linux) to build the
price history. Telegram alerts activate automatically when
TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from price_monitor.alerts import format_drops, send_telegram  # noqa: E402
from price_monitor.scraper import fetch_listing, load_site_config  # noqa: E402
from price_monitor.storage import PriceStore  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", default=str(PROJECT_ROOT / "sites" / "books_demo.yaml")
    )
    parser.add_argument("--min-drop", type=float, default=5.0)
    args = parser.parse_args()

    cfg = load_site_config(args.config)
    print(f"Scraping '{cfg.name}' ...")
    items = fetch_listing(cfg)
    print(f"  {len(items)} items found")

    store = PriceStore(PROJECT_ROOT / "prices.sqlite3")
    store.record(cfg.name, items)

    drops = store.price_drops(cfg.name, min_drop_pct=args.min_drop)
    if drops.empty:
        print("  no price drops vs previous snapshot")
    else:
        message = format_drops(cfg.name, drops)
        print(message)
        if send_telegram(message):
            print("  Telegram alert sent ✅")
        else:
            print("  (Telegram not configured — set TELEGRAM_BOT_TOKEN/CHAT_ID)")
    store.close()


if __name__ == "__main__":
    main()
