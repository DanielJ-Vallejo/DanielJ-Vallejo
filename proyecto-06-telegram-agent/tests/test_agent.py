"""Tests for the Telegram agent core logic (no network, no Telegram)."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from telegram_agent.booking import BookingStore, generate_slots
from telegram_agent.config import BusinessProfile, FaqEntry, load_profile
from telegram_agent.faq import best_answer, normalize, score

EXAMPLE_YAML = Path(__file__).resolve().parents[1] / "config.example.yaml"


def _profile(**overrides) -> BusinessProfile:
    base = dict(
        name="Test",
        description="",
        services=["Corte"],
        opening_hour=9,
        closing_hour=12,
        slot_minutes=60,
        days_open=[0, 1, 2, 3, 4],
        owner_chat_id=None,
        faq=[
            FaqEntry(
                question="¿Cuánto cuesta el corte?",
                answer="$150",
                keywords=["precio", "costo"],
            ),
            FaqEntry(
                question="¿Dónde están ubicados?",
                answer="Coyoacán",
                keywords=["direccion", "donde"],
            ),
        ],
    )
    base.update(overrides)
    return BusinessProfile(**base)


def test_example_config_loads_and_validates():
    profile = load_profile(EXAMPLE_YAML)
    assert profile.name
    assert profile.faq and profile.services


def test_invalid_hours_rejected():
    with pytest.raises(ValueError, match="opening_hour"):
        _profile(opening_hour=20, closing_hour=10).validate()


def test_normalize_strips_accents_and_case():
    assert normalize("¿DÓNDE están?") == "¿donde estan?"


def test_faq_matches_with_accents_and_keywords():
    profile = _profile()
    assert best_answer("cuanto cuesta el corte??", profile.faq) == "$150"
    assert best_answer("precio", profile.faq) == "$150"          # keyword only
    assert best_answer("dónde están ubicados", profile.faq) == "Coyoacán"


def test_faq_low_confidence_returns_none():
    profile = _profile()
    assert best_answer("quiero adoptar un perro", profile.faq) is None


def test_score_is_bounded():
    entry = FaqEntry(question="hola", answer="x", keywords=["hola"])
    assert 0.0 <= score("hola", entry) <= 1.0


def test_generate_slots_respects_hours_and_weekdays():
    profile = _profile()  # open 9-12, Mon-Fri, 60 min
    monday = datetime(2026, 6, 8, 7, 0)  # Monday before opening
    slots = generate_slots(profile, monday, days_ahead=1)
    assert slots == ["2026-06-08 09:00", "2026-06-08 10:00", "2026-06-08 11:00"]


def test_generate_slots_skips_past_and_taken():
    profile = _profile()
    monday = datetime(2026, 6, 8, 9, 30)  # 9:00 already past
    slots = generate_slots(
        profile, monday, days_ahead=1, taken={"2026-06-08 10:00"}
    )
    assert slots == ["2026-06-08 11:00"]


def test_generate_slots_skips_closed_days():
    profile = _profile(days_open=[0])  # only Mondays
    saturday = datetime(2026, 6, 13, 8, 0)
    # Sat + Sun only → no open day in range
    assert generate_slots(profile, saturday, days_ahead=2) == []
    # Range reaches Monday 2026-06-15 → only Monday slots offered
    slots = generate_slots(profile, saturday, days_ahead=3)
    assert slots and all(s.startswith("2026-06-15") for s in slots)


def test_booking_store_books_once(tmp_path):
    store = BookingStore(tmp_path / "test.sqlite3")
    assert store.book(1, "Ana", "Corte", "2099-01-01 10:00") is True
    assert store.book(2, "Luis", "Corte", "2099-01-01 10:00") is False  # taken
    assert "2099-01-01 10:00" in store.booked_slots()
    store.close()


def test_booking_store_lists_and_cancels_only_own(tmp_path):
    store = BookingStore(tmp_path / "test.sqlite3")
    store.book(1, "Ana", "Corte", "2099-01-01 10:00")
    (bid, service, slot), = store.bookings_for(1)
    assert (service, slot) == ("Corte", "2099-01-01 10:00")
    assert store.cancel(bid, chat_id=2) is False   # someone else's booking
    assert store.cancel(bid, chat_id=1) is True
    assert store.bookings_for(1) == []
    store.close()
