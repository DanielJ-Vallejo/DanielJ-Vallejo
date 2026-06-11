"""Business profile loaded from a YAML file.

Each client deployment only needs a different YAML — the code never changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class FaqEntry:
    question: str
    answer: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class BusinessProfile:
    name: str
    description: str
    services: list[str]
    opening_hour: int          # 24h format, e.g. 9
    closing_hour: int          # e.g. 18
    slot_minutes: int          # appointment duration
    days_open: list[int]       # 0=Monday ... 6=Sunday
    owner_chat_id: int | None  # Telegram chat that receives escalations
    faq: list[FaqEntry]

    def validate(self) -> None:
        if not 0 <= self.opening_hour < self.closing_hour <= 24:
            raise ValueError("opening_hour must be before closing_hour (0-24)")
        if self.slot_minutes <= 0 or self.slot_minutes > 8 * 60:
            raise ValueError("slot_minutes must be between 1 and 480")
        if not self.services:
            raise ValueError("at least one service is required")
        if any(d not in range(7) for d in self.days_open):
            raise ValueError("days_open must contain weekday numbers 0-6")


def load_profile(path: Path | str) -> BusinessProfile:
    """Load and validate a business profile YAML."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    faq = [
        FaqEntry(
            question=item["question"],
            answer=item["answer"],
            keywords=item.get("keywords", []),
        )
        for item in raw.get("faq", [])
    ]
    profile = BusinessProfile(
        name=raw["name"],
        description=raw.get("description", ""),
        services=raw.get("services", []),
        opening_hour=int(raw.get("opening_hour", 9)),
        closing_hour=int(raw.get("closing_hour", 18)),
        slot_minutes=int(raw.get("slot_minutes", 60)),
        days_open=list(raw.get("days_open", [0, 1, 2, 3, 4])),
        owner_chat_id=raw.get("owner_chat_id"),
        faq=faq,
    )
    profile.validate()
    return profile
