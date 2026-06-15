# -*- coding: utf-8 -*-
"""Capa de presentación del churn: SQL/pandas -> figuras matplotlib.

La base vive en SQL; pandas la trae y matplotlib genera figuras estáticas para
los reportes y el README.
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd

from . import consultas, modelo

plt.switch_backend("Agg")  # backend sin ventana (servidor/CI)

REPORTS = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def _guardar(fig, nombre: str, ruta: str | None) -> str:
    ruta = os.path.abspath(ruta or os.path.join(REPORTS, nombre))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return ruta


def fig_churn_por_contrato(con, ruta: str | None = None) -> str:
    """Tasa de churn por tipo de contrato (el segmento más revelador)."""
    df = pd.read_sql_query(consultas.TASA_POR_CONTRATO, con)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["tipo_contrato"], df["churn_pct"], color="#d62728")
    ax.set_title("Tasa de churn por tipo de contrato")
    ax.set_ylabel("Churn %")
    return _guardar(fig, "churn_por_contrato.png", ruta)


def fig_drivers(df_clientes: pd.DataFrame, ruta: str | None = None) -> str:
    """Drivers del churn (coeficientes del modelo): qué empuja el abandono."""
    res = modelo.entrenar(df_clientes)
    nombres = [d[0] for d in res["drivers"]][::-1]
    coefs = [d[1] for d in res["drivers"]][::-1]
    colores = ["#1f77b4" if c < 0 else "#d62728" for c in coefs]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(nombres, coefs, color=colores)
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.set_title(f"Drivers del churn (ROC-AUC {res['auc']})")
    return _guardar(fig, "churn_drivers.png", ruta)


def generar_todas(con, df_clientes: pd.DataFrame) -> list[str]:
    return [fig_churn_por_contrato(con), fig_drivers(df_clientes)]
