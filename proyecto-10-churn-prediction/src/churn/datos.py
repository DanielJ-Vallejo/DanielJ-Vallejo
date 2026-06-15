# -*- coding: utf-8 -*-
"""Genera un dataset sintético de clientes (estilo telco) con etiqueta de churn.

Determinista (semilla fija). El churn se genera de una función logística sobre
variables con efecto real (contrato mes a mes, poca antigüedad, cargo alto y muchas
llamadas a soporte suben la probabilidad de abandono), para que el modelo tenga
señal y los segmentos en SQL sean interpretables.
"""
from __future__ import annotations

import os
import sqlite3

import numpy as np
import pandas as pd

SEMILLA = 42
CONTRATOS = {0: "mes a mes", 1: "anual", 2: "bianual"}
DB_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                          "churn.db")


def generar(n: int = 2000, semilla: int = SEMILLA) -> pd.DataFrame:
    """Devuelve un DataFrame de n clientes con sus variables y la etiqueta churn."""
    rng = np.random.default_rng(semilla)
    tenure = rng.integers(1, 73, n)
    contrato = rng.choice([0, 1, 2], n, p=[0.55, 0.30, 0.15])
    cargo = rng.uniform(200, 1500, n).round(0)
    extras = rng.integers(0, 6, n)
    soporte = rng.poisson(1.5, n).clip(0, 10)
    factura_e = rng.integers(0, 2, n)

    z = (-1.0
         + 1.8 * (contrato == 0)
         - 0.03 * tenure
         + 0.0010 * (cargo - 700)
         + 0.25 * soporte
         - 0.10 * extras)
    prob = 1 / (1 + np.exp(-z))
    churn = (rng.random(n) < prob).astype(int)

    return pd.DataFrame({
        "id": np.arange(1, n + 1),
        "tenure_meses": tenure,
        "tipo_contrato": [CONTRATOS[c] for c in contrato],
        "cargo_mensual": cargo,
        "servicios_extra": extras,
        "llamadas_soporte": soporte,
        "factura_electronica": factura_e,
        "churn": churn,
    })


def construir_db(path: str = DB_DEFAULT, semilla: int = SEMILLA) -> str:
    """(Re)crea la base SQLite con la tabla 'clientes'. Devuelve la ruta."""
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)
    df = generar(semilla=semilla)
    con = sqlite3.connect(path)
    df.to_sql("clientes", con, index=False)
    con.close()
    return path


def cargar_df(path: str = DB_DEFAULT) -> pd.DataFrame:
    """Lee la tabla 'clientes' a un DataFrame (construye la base si falta)."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        construir_db(path)
    con = sqlite3.connect(path)
    try:
        return pd.read_sql_query("SELECT * FROM clientes", con)
    finally:
        con.close()


if __name__ == "__main__":
    ruta = construir_db()
    print(f"Base creada en {ruta}")
