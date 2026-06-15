# -*- coding: utf-8 -*-
"""Dashboard interactivo: demanda y pricing hotelero durante el Mundial 2026.

Uso:  streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mundial_demanda import analisis, consultas
from mundial_demanda.datos import DB_DEFAULT, construir_db


@st.cache_resource
def conectar() -> sqlite3.Connection:
    ruta = os.path.abspath(DB_DEFAULT)
    if not os.path.exists(ruta):
        construir_db(ruta)
    return sqlite3.connect(ruta, check_same_thread=False)


def df(con: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, con)


st.set_page_config(page_title="Demanda Mundial 2026", layout="wide")
st.title("⚽ Demanda y pricing hotelero — Mundial 2026")
st.caption("Sedes en México: CDMX · Guadalajara · Monterrey. "
           "Datos sintéticos, análisis con SQL.")

con = conectar()
rec = analisis.recomendacion(con)

c1, c2, c3 = st.columns(3)
c1.metric("Ocupación en día de partido", f"{rec['ocupacion_partido']}%",
          f"vs {rec['ocupacion_normal']}% normal")
c2.metric("Subida de precio sugerida", f"{rec['subida_recomendada_pct']}%")
c3.metric("Ingreso adicional estimado", f"${rec['ingreso_extra_mxn']:,.0f} MXN")

st.success(rec["texto"])

st.subheader("Mapa de calor: ocupación por ciudad y fecha")
occ = df(con, """
    SELECT o.fecha, h.ciudad, ROUND(AVG(o.ocupacion_pct), 1) AS ocupacion
    FROM ocupacion o JOIN hoteles h ON h.id = o.hotel_id
    GROUP BY o.fecha, h.ciudad
""")
mapa = occ.pivot(index="ciudad", columns="fecha", values="ocupacion")
st.plotly_chart(
    px.imshow(mapa, aspect="auto", color_continuous_scale="YlOrRd",
              labels=dict(color="Ocupación %")),
    use_container_width=True,
)

st.subheader("Día de partido vs día normal: la demanda salta, el precio no")
pn = df(con, consultas.PARTIDO_VS_NORMAL)
a, b = st.columns(2)
a.plotly_chart(px.bar(pn, x="tipo", y="ocupacion_pct", color="tipo",
                      title="Ocupación promedio (%)"), use_container_width=True)
b.plotly_chart(px.bar(pn, x="tipo", y="precio_mxn", color="tipo",
                      title="Precio promedio (MXN)"), use_container_width=True)

st.subheader("Hoteles con mayor ingreso estimado")
st.dataframe(df(con, consultas.TOP_HOTELES_INGRESO), use_container_width=True)
