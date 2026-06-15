# -*- coding: utf-8 -*-
"""Segmentos en SQL + modelo + recomendación de retención.

Uso:  python scripts/reporte.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from churn import analisis, consultas, modelo
from churn.datos import DB_DEFAULT, cargar_df, construir_db


def _tabla(columnas: list[str], filas: list[tuple]) -> None:
    anchos = [len(c) for c in columnas]
    for f in filas:
        for i, v in enumerate(f):
            anchos[i] = max(anchos[i], len(str(v)))
    print("  " + " | ".join(c.ljust(anchos[i]) for i, c in enumerate(columnas)))
    print("  " + "-+-".join("-" * a for a in anchos))
    for f in filas:
        print("  " + " | ".join(str(v).ljust(anchos[i]) for i, v in enumerate(f)))


def main() -> None:
    ruta = os.path.abspath(DB_DEFAULT)
    if not os.path.exists(ruta):
        construir_db(ruta)
    con = sqlite3.connect(ruta)
    for titulo, sql in consultas.CONSULTAS.items():
        print(f"\n### {titulo}")
        _tabla(*consultas.correr(con, sql))
    con.close()

    df = cargar_df(ruta)
    res = modelo.entrenar(df)
    print(f"\n### Modelo de predicción\nROC-AUC en prueba: {res['auc']}")
    print("Drivers del churn (coeficiente estandarizado):")
    for nombre, coef in res["drivers"]:
        print(f"  {nombre:>20}: {coef:+.2f}")

    print("\n=== RECOMENDACIÓN DE NEGOCIO ===")
    print(analisis.recomendacion(df)["texto"])


if __name__ == "__main__":
    main()
