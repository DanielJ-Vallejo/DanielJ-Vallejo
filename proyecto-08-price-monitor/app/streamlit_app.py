"""Price history dashboard.

    streamlit run app/streamlit_app.py

Reads prices.sqlite3 produced by scripts/run_monitor.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from price_monitor.storage import PriceStore  # noqa: E402

st.set_page_config(page_title="Monitor de Precios", page_icon="📉", layout="wide")
st.title("📉 Monitor de Precios")

DB = PROJECT_ROOT / "prices.sqlite3"
if not DB.exists():
    st.info(
        "Aún no hay datos. Ejecuta primero:\n\n"
        "```\npython scripts/run_monitor.py\n```\n"
        "y recarga esta página."
    )
    st.stop()

store = PriceStore(DB)
df = store.history()
store.close()

if df.empty:
    st.info("La base existe pero está vacía — corre el monitor primero.")
    st.stop()

df["scraped_at"] = pd.to_datetime(df["scraped_at"])

site = st.sidebar.selectbox("Sitio", sorted(df["site"].unique()))
site_df = df[df["site"] == site]
products = st.sidebar.multiselect(
    "Productos",
    sorted(site_df["title"].unique()),
    default=sorted(site_df["title"].unique())[:5],
)

col1, col2, col3 = st.columns(3)
col1.metric("Productos monitoreados", site_df["title"].nunique())
col2.metric("Snapshots", site_df["scraped_at"].nunique())
col3.metric("Precio promedio actual",
            f"${site_df.sort_values('scraped_at').groupby('title')['price'].last().mean():,.2f}")

if products:
    plot_df = site_df[site_df["title"].isin(products)]
    fig = px.line(
        plot_df,
        x="scraped_at",
        y="price",
        color="title",
        markers=True,
        title=f"Historial de precios — {site}",
        labels={"scraped_at": "Fecha", "price": "Precio", "title": "Producto"},
    )
    st.plotly_chart(fig, width="stretch")

st.subheader("Últimos precios")
latest = (
    site_df.sort_values("scraped_at")
    .groupby("title")
    .agg(precio_actual=("price", "last"), ultima_lectura=("scraped_at", "last"))
    .reset_index()
    .sort_values("precio_actual")
)
st.dataframe(latest, width="stretch")
st.download_button(
    "⬇️ Exportar historial (CSV)",
    data=site_df.to_csv(index=False).encode("utf-8"),
    file_name=f"historial_{site}.csv",
    mime="text/csv",
)
