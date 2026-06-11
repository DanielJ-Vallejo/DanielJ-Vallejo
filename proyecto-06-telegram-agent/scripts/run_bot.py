"""Run the Telegram agent.

Setup (100% free):
1. Talk to @BotFather on Telegram → /newbot → copy the token.
2. ``set TELEGRAM_BOT_TOKEN=123:abc`` (or export on Linux).
3. Edit ``config.example.yaml`` with the business info → save as ``config.yaml``.
4. ``python scripts/run_bot.py``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from telegram_agent.bot import build_application  # noqa: E402
from telegram_agent.config import load_profile  # noqa: E402


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit(
            "Missing TELEGRAM_BOT_TOKEN environment variable.\n"
            "Create a free bot with @BotFather and set the token."
        )
    config_path = PROJECT_ROOT / "config.yaml"
    if not config_path.exists():
        config_path = PROJECT_ROOT / "config.example.yaml"
        print("config.yaml not found — using config.example.yaml (demo profile)")
    profile = load_profile(config_path)
    app = build_application(token, profile, PROJECT_ROOT / "bookings.sqlite3")
    print(f"Bot for '{profile.name}' running. Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
