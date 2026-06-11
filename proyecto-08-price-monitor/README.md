# 📉 Configurable Price Monitor / Monitor de Precios Configurable

> **EN** — Web scraping productized: a YAML file describes any store's listing page,
> the monitor scrapes it on a schedule, stores price history in SQLite, detects drops
> and sends **free Telegram alerts**. Interactive Plotly dashboard included. Adapting it
> to a new site means writing 8 lines of YAML, not code.
>
> **ES** — Web scraping convertido en producto: un archivo YAML describe la página de
> cualquier tienda, el monitor la scrapea con horario, guarda el historial de precios en
> SQLite, detecta bajadas y manda **alertas gratis por Telegram**. Incluye dashboard
> interactivo con Plotly. Adaptarlo a un sitio nuevo son 8 líneas de YAML, no código.

![Python](https://img.shields.io/badge/python-3.11-blue) ![scraping](https://img.shields.io/badge/scraping-BeautifulSoup-green) ![cost](https://img.shields.io/badge/costo-%240-brightgreen) ![tests](https://img.shields.io/badge/tests-8%20passing-brightgreen)

---

## 🇪🇸 Español

### Casos de uso reales

- Una tienda vigila los precios de su **competencia** y recibe un Telegram cuando bajan.
- Un comprador espera la **bajada de un producto** específico.
- Un analista construye **historial de precios** para negociar con proveedores.

### Cómo funciona

```
YAML del sitio → scraper (requests + BeautifulSoup) → SQLite (historial)
                                                     → detección de bajadas → Telegram
                                                     → dashboard Streamlit + Plotly
```

```bash
pip install -r requirements.txt
python scripts/run_monitor.py            # scrapea el sitio demo y guarda snapshot
streamlit run app/streamlit_app.py       # dashboard con historial y export CSV
```

Prográmalo gratis con el **Programador de tareas** de Windows o `cron` en Linux para
construir historial. Con `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` definidos
(bot gratuito de @BotFather), las bajadas ≥5% llegan solas a tu Telegram.

### Un sitio nuevo = un YAML nuevo

```yaml
name: "mi-tienda"
url: "https://mitienda.com/ofertas"
item_selector: "div.producto"
title_selector: "h2.nombre"
price_selector: "span.precio"
```

El demo incluido apunta a [books.toscrape.com](https://books.toscrape.com), un sitio
**construido específicamente para practicar scraping** — la demo corre legal y
reproduciblemente en cualquier máquina. Para sitios reales: revisa siempre el
`robots.txt` y los términos de servicio del sitio antes de monitorearlo.

### Manejo de precios del mundo real

`parse_price()` entiende `$1,234.56`, `£51.77`, `1.234,56 MXN` y `19,99` — los tests
cubren cada formato, además del parser HTML (con fixture offline), el almacenamiento,
la detección de bajadas y que las alertas nunca tumben el scrape.

---

## 🇬🇧 English

Productized scraping: one YAML per store (CSS selectors), scheduled scraping with a
polite User-Agent, SQLite price history, drop detection comparing the last two
snapshots per item, free Telegram alerts and a Plotly/Streamlit dashboard with CSV
export. The bundled demo targets books.toscrape.com (a sandbox made for scraping
practice) so the full loop runs legally end to end — including in CI. Price parsing
handles US, UK and Latin American number formats, all unit-tested offline.

```
proyecto-08-price-monitor/
├── src/price_monitor/    # scraper (YAML-driven), storage, alerts
├── sites/books_demo.yaml # demo site config
├── scripts/run_monitor.py
├── app/streamlit_app.py  # Plotly dashboard
└── tests/                # 8 offline tests (fixture HTML, formats, drops)
```
