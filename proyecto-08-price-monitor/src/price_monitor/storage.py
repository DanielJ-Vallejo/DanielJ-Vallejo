"""SQLite price history with drop detection."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT NOT NULL,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    scraped_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_prices_site_title ON prices (site, title);
"""


class PriceStore:
    def __init__(self, db_path: Path | str):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def record(self, site: str, items: list[dict]) -> int:
        """Store one scrape snapshot; returns rows inserted."""
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.conn.executemany(
            "INSERT INTO prices (site, title, price, scraped_at) VALUES (?, ?, ?, ?)",
            [(site, it["title"], it["price"], now) for it in items],
        )
        self.conn.commit()
        return len(items)

    def history(self, site: str | None = None) -> pd.DataFrame:
        query = "SELECT site, title, price, scraped_at FROM prices"
        params: tuple = ()
        if site:
            query += " WHERE site = ?"
            params = (site,)
        return pd.read_sql_query(query, self.conn, params=params)

    def price_drops(self, site: str, min_drop_pct: float = 5.0) -> pd.DataFrame:
        """Items whose latest price is >= ``min_drop_pct`` below the previous one.

        Compares the two most recent snapshots per item.
        """
        df = self.history(site)
        if df.empty:
            return df.assign(prev_price=[], drop_pct=[])
        df = df.sort_values("scraped_at")
        last_two = df.groupby("title").tail(2)
        counts = last_two.groupby("title")["price"].count()
        eligible = counts[counts == 2].index
        rows = []
        for title in eligible:
            prev, last = last_two[last_two["title"] == title]["price"].tolist()
            if prev <= 0:
                continue
            drop_pct = 100.0 * (prev - last) / prev
            if drop_pct >= min_drop_pct:
                rows.append(
                    {"title": title, "prev_price": prev, "price": last,
                     "drop_pct": round(drop_pct, 2)}
                )
        return pd.DataFrame(rows)
