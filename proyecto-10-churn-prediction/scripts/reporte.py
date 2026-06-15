# -*- coding: utf-8 -*-
"""Segmentos en SQL (tablas con pandas) + modelo + figuras + recomendación.

La base sigue en SQL; pandas y matplotlib solo presentan la salida.
Uso:  python scripts/reporte.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from churn import analisis, consultas, modelo, visual
from churn.datos import DB_DEFAULT, construir_db


def main() -> None:
    ruta = os.path.abspath(DB_DEFAULT)
    if not os.path.exists(ruta):
        construir_db(ruta)
    con = sqlite3.connect(ruta)

    for titulo, sql in consultas.CONSULTAS.items():
        print(f"\n### {titulo}")
        print(pd.read_sql_query(sql, con).to_string(index=False))

    df = pd.read_sql_query("SELECT * FROM clientes", con)
    res = modelo.entrenar(df)
    print(f"\n### Modelo de predicción\nROC-AUC en prueba: {res['auc']}")
    print("Drivers del churn (coeficiente estandarizado):")
    for nombre, coef in res["drivers"]:
        print(f"  {nombre:>20}: {coef:+.2f}")

    print("\n### Figuras generadas (matplotlib)")
    for figura in visual.generar_todas(con, df):
        print(f"  {figura}")

    print("\n=== RECOMENDACIÓN DE NEGOCIO ===")
    print(analisis.recomendacion(df)["texto"])
    con.close()


if __name__ == "__main__":
    main()
