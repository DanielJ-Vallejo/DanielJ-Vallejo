"""Free price-drop alerts through the Telegram Bot API.

Reuses the zero-cost Telegram stack from proyecto-06: create a bot with
@BotFather, set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID, done.
"""

from __future__ import annotations

import os

import pandas as pd
import requests


def format_drops(site: str, drops: pd.DataFrame) -> str:
    lines = [f"📉 Bajadas de precio en {site}:"]
    for _, row in drops.iterrows():
        lines.append(
            f"• {row['title'][:60]} — ${row['prev_price']:,.2f} → "
            f"${row['price']:,.2f} (−{row['drop_pct']}%)"
        )
    return "\n".join(lines)


def send_telegram(message: str, timeout: int = 15) -> bool:
    """Send a message if TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID are set.

    Returns True on success, False when unconfigured or on API failure —
    alerting must never crash the scrape run.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=timeout,
        )
        return resp.ok
    except requests.RequestException:
        return False
