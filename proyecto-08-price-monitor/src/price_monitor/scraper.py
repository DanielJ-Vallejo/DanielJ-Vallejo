"""Configurable scraping: one YAML describes a site, no code changes.

A *site config* declares the listing URL, a CSS selector per item and
selectors/attributes for each field. Adapting the monitor to a new store is
editing YAML — the selling point for client work. A demo config for
``books.toscrape.com`` (a site built for scraping practice) ships with the
project so everything can be exercised legally end to end.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

USER_AGENT = "price-monitor/1.0 (+portfolio project; respectful scraping)"
PRICE_RE = re.compile(r"([\d.,]+)")


@dataclass
class SiteConfig:
    name: str
    url: str
    item_selector: str
    title_selector: str
    price_selector: str
    title_attr: str | None = None    # read attribute instead of text
    link_selector: str | None = None
    extra_headers: dict = field(default_factory=dict)


def load_site_config(path: Path | str) -> SiteConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return SiteConfig(**raw)


def parse_price(text: str) -> float | None:
    """'$1,234.56' / '£51.77' / '1.234,56 MXN' → float (best effort)."""
    match = PRICE_RE.search(text.replace("\xa0", " "))
    if not match:
        return None
    raw = match.group(1)
    # If both separators appear, the last one is the decimal mark
    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        # lone comma: decimal if it has 2 digits after, thousands otherwise
        head, _, tail = raw.rpartition(",")
        raw = f"{head.replace(',', '')}.{tail}" if len(tail) == 2 else raw.replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_listing(html: str, cfg: SiteConfig) -> list[dict]:
    """Extract {title, price} records from a listing page's HTML."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for node in soup.select(cfg.item_selector):
        title_node = node.select_one(cfg.title_selector)
        price_node = node.select_one(cfg.price_selector)
        if title_node is None or price_node is None:
            continue
        title = (
            title_node.get(cfg.title_attr, "").strip()
            if cfg.title_attr
            else title_node.get_text(strip=True)
        )
        price = parse_price(price_node.get_text(strip=True))
        if title and price is not None:
            items.append({"title": title, "price": price})
    return items


def fetch_listing(cfg: SiteConfig, timeout: int = 30) -> list[dict]:
    """Download the listing page and parse it."""
    headers = {"User-Agent": USER_AGENT, **cfg.extra_headers}
    resp = requests.get(cfg.url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return parse_listing(resp.text, cfg)
