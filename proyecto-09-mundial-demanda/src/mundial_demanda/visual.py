# -*- coding: utf-8 -*-
"""Capa de presentación: SQL -> pandas -> figuras matplotlib.

La base de datos vive en SQL (SQLite); pandas la trae a un DataFrame para
manipularla/mostrarla y matplotlib genera figuras estáticas para los reportes.
Para datos de millones de filas se usaría polars (API parecida, mucho más rápido);
con este tamaño pandas es de sobra.
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import pandas as pd

from . import consultas

plt.switch_backend("Agg")  # backend sin ventana: sirve en servidor y en CI

REPORTS = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def _guardar(fig, nombre: str, ruta: str | None) -> str:
    ruta = os.path.abspath(ruta or os.path.join(REPORTS, nombre))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    fig.savefig(ruta, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return ruta


def fig_partido_vs_normal(con, ruta: str | None = None) -> str:
    """El gráfico clave: la demanda salta en día de partido, el precio no."""
    df = pd.read_sql_query(consultas.PARTIDO_VS_NORMAL, con)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
    colores = ["#d62728", "#1f77b4"]
    ax1.bar(df["tipo"], df["ocupacion_pct"], color=colores)
    ax1.set_title("Ocupación promedio (%)")
    ax1.set_ylim(0, 100)
    ax2.bar(df["tipo"], df["precio_mxn"], color=colores)
    ax2.set_title("Precio promedio (MXN)")
    fig.suptitle("Día de partido vs día normal: la demanda salta, el precio no")
    return _guardar(fig, "partido_vs_normal.png", ruta)


def fig_ocupacion_por_ciudad(con, ruta: str | None = None) -> str:
    """Ocupación diaria por ciudad: se ven los picos en días de partido."""
    df = pd.read_sql_query(
        """SELECT o.fecha, h.ciudad, AVG(o.ocupacion_pct) AS occ
           FROM ocupacion o JOIN hoteles h ON h.id = o.hotel_id
           GROUP BY o.fecha, h.ciudad""",
        con,
    )
    pivote = df.pivot(index="fecha", columns="ciudad", values="occ")
    pivote.index = pd.to_datetime(pivote.index)
    fig, ax = plt.subplots(figsize=(10, 4))
    pivote.plot(ax=ax, linewidth=1.8)
    ax.set_title("Ocupación diaria por ciudad — Mundial 2026")
    ax.set_ylabel("Ocupación %")
    ax.set_xlabel("")
    return _guardar(fig, "ocupacion_por_ciudad.png", ruta)


def generar_todas(con) -> list[str]:
    """Genera todas las figuras y devuelve sus rutas."""
    return [fig_partido_vs_normal(con), fig_ocupacion_por_ciudad(con)]
