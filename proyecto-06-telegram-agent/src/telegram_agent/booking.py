"""Appointment storage and slot logic on SQLite (no external services)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from .config import BusinessProfile

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    customer TEXT NOT NULL,
    service TEXT NOT NULL,
    slot TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class BookingStore:
    """Thin SQLite wrapper for appointments."""

    def __init__(self, db_path: Path | str):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def booked_slots(self) -> set[str]:
        rows = self.conn.execute("SELECT slot FROM bookings").fetchall()
        return {r[0] for r in rows}

    def book(self, chat_id: int, customer: str, service: str, slot: str) -> bool:
        """Insert a booking; returns False if the slot was just taken."""
        try:
            self.conn.execute(
                "INSERT INTO bookings (chat_id, customer, service, slot) "
                "VALUES (?, ?, ?, ?)",
                (chat_id, customer, service, slot),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def bookings_for(self, chat_id: int) -> list[tuple[int, str, str]]:
        """(id, service, slot) of future bookings for one chat."""
        rows = self.conn.execute(
            "SELECT id, service, slot FROM bookings "
            "WHERE chat_id = ? AND slot >= datetime('now') ORDER BY slot",
            (chat_id,),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]

    def cancel(self, booking_id: int, chat_id: int) -> bool:
        cur = self.conn.execute(
            "DELETE FROM bookings WHERE id = ? AND chat_id = ?",
            (booking_id, chat_id),
        )
        self.conn.commit()
        return cur.rowcount > 0


def generate_slots(
    profile: BusinessProfile,
    start: datetime,
    days_ahead: int = 7,
    taken: set[str] | None = None,
    max_slots: int = 24,
) -> list[str]:
    """Free slot timestamps (ISO ``YYYY-MM-DD HH:MM``) for the next days.

    Honors opening hours, open weekdays and already-booked slots; never
    offers a slot in the past.
    """
    taken = taken or set()
    slots: list[str] = []
    day = start.replace(hour=0, minute=0, second=0, microsecond=0)
    for _ in range(days_ahead):
        if day.weekday() in profile.days_open:
            t = day.replace(hour=profile.opening_hour)
            end = day.replace(hour=profile.closing_hour)
            while t + timedelta(minutes=profile.slot_minutes) <= end:
                iso = t.strftime("%Y-%m-%d %H:%M")
                if t > start and iso not in taken:
                    slots.append(iso)
                    if len(slots) >= max_slots:
                        return slots
                t += timedelta(minutes=profile.slot_minutes)
        day += timedelta(days=1)
    return slots
