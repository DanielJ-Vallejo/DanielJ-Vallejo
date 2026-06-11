"""Offline tests: HTML fixture parsing, price parsing, storage, drops, alerts."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from price_monitor.alerts import format_drops, send_telegram
from price_monitor.scraper import (
    SiteConfig,
    load_site_config,
    parse_listing,
    parse_price,
)
from price_monitor.storage import PriceStore

FIXTURE_HTML = """
<html><body>
  <article class="product_pod">
    <h3><a title="Libro A" href="a.html">Libro A...</a></h3>
    <p class="price_color">£51.77</p>
  </article>
  <article class="product_pod">
    <h3><a title="Libro B" href="b.html">Libro B...</a></h3>
    <p class="price_color">£13.99</p>
  </article>
  <article class="product_pod">
    <h3><a title="Sin precio" href="c.html">x</a></h3>
  </article>
</body></html>
"""

DEMO_CONFIG = Path(__file__).resolve().parents[1] / "sites" / "books_demo.yaml"


def _cfg() -> SiteConfig:
    return SiteConfig(
        name="test",
        url="http://example.invalid",
        item_selector="article.product_pod",
        title_selector="h3 a",
        title_attr="title",
        price_selector="p.price_color",
    )


def test_parse_listing_extracts_items_and_skips_incomplete():
    items = parse_listing(FIXTURE_HTML, _cfg())
    assert items == [
        {"title": "Libro A", "price": 51.77},
        {"title": "Libro B", "price": 13.99},
    ]


def test_demo_config_loads():
    cfg = load_site_config(DEMO_CONFIG)
    assert cfg.item_selector and cfg.url.startswith("https://books.toscrape.com")


def test_parse_price_formats():
    assert parse_price("$1,234.56") == 1234.56
    assert parse_price("£51.77") == 51.77
    assert parse_price("1.234,56 MXN") == 1234.56
    assert parse_price("2,999") == 2999.0          # lone comma as thousands
    assert parse_price("19,99") == 19.99           # lone comma as decimals
    assert parse_price("sin precio") is None


def test_store_records_and_reads(tmp_path):
    store = PriceStore(tmp_path / "p.sqlite3")
    n = store.record("demo", [{"title": "A", "price": 10.0}])
    assert n == 1
    df = store.history("demo")
    assert len(df) == 1 and df.loc[0, "price"] == 10.0
    store.close()


def test_price_drops_detects_only_real_drops(tmp_path):
    store = PriceStore(tmp_path / "p.sqlite3")
    store.record("demo", [{"title": "A", "price": 100.0},
                          {"title": "B", "price": 50.0}])
    store.record("demo", [{"title": "A", "price": 80.0},   # -20%
                          {"title": "B", "price": 50.0}])  # sin cambio
    drops = store.price_drops("demo", min_drop_pct=5.0)
    assert drops["title"].tolist() == ["A"]
    assert drops.loc[0, "drop_pct"] == 20.0
    store.close()


def test_price_drops_empty_history(tmp_path):
    store = PriceStore(tmp_path / "p.sqlite3")
    assert store.price_drops("demo").empty
    store.close()


def test_format_drops_message(tmp_path):
    store = PriceStore(tmp_path / "p.sqlite3")
    store.record("demo", [{"title": "A", "price": 100.0}])
    store.record("demo", [{"title": "A", "price": 90.0}])
    msg = format_drops("demo", store.price_drops("demo"))
    assert "demo" in msg and "100.00" in msg and "90.00" in msg
    store.close()


def test_send_telegram_unconfigured_is_safe(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    assert send_telegram("hola") is False
