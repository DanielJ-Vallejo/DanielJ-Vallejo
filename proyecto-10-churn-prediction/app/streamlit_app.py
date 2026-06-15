# -*- coding: utf-8 -*-
"""Dashboard de churn: segmentos en riesgo, drivers y recomendación.

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

from churn import analisis, consultas, modelo
from churn.datos import DB_DEFAULT, construir_db


@st.cache_resource
def conectar() -> sqlite3.Connection:
    ruta = os.path.abspath(DB_DEFAULT)
    if not os.path.exists(ruta):
        construir_db(ruta)
    return sqlite3.connect(ruta, check_same_thread=False)


st.set_page_config(page_title="Predicción de churn", layout="wide")
st.title("📉 Predicción de abandono de clientes (churn)")

con = conectar()
df = pd.read_sql_query("SELECT * FROM clientes", con)
rec = analisis.recomendacion(df)
res = modelo.entrenar(df)

c1, c2, c3 = st.columns(3)
c1.metric("Churn global", f"{rec['churn_global_pct']}%")
c2.metric("Segmento en riesgo", f"{rec['segmento_riesgo_n']} clientes",
          f"{rec['segmento_riesgo_churn_pct']}% churn")
c3.metric("ROC-AUC del modelo", res["auc"])

st.success(rec["texto"])

st.subheader("Churn por tipo de contrato")
seg = pd.read_sql_query(consultas.TASA_POR_CONTRATO, con)
st.plotly_chart(px.bar(seg, x="tipo_contrato", y="churn_pct",
                       color="tipo_contrato", title="Churn % por contrato"),
                use_container_width=True)

st.subheader("Drivers del churn (qué empuja el abandono)")
drivers = pd.DataFrame(res["drivers"], columns=["variable", "coeficiente"])
st.plotly_chart(px.bar(drivers, x="coeficiente", y="variable", orientation="h",
                       title="Coeficientes (mayor = más churn)"),
                use_container_width=True)
