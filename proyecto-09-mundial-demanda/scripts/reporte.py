# -*- coding: utf-8 -*-
"""Corre las consultas de negocio (tablas con pandas), genera las figuras
(matplotlib) y muestra la recomendación.

La base sigue en SQL; pandas solo le da mejor presentación a la salida.
Uso:  python scripts/reporte.py
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mundial_demanda import analisis, consultas, visual
from mundial_demanda.datos import DB_DEFAULT, construir_db


def main() -> None:
    ruta = os.path.abspath(DB_DEFAULT)
    if not os.path.exists(ruta):
        construir_db(ruta)
    con = sqlite3.connect(ruta)

    for titulo, sql in consultas.CONSULTAS.items():
        print(f"\n### {titulo}")
        df = pd.read_sql_query(sql, con)          # SQL -> DataFrame de pandas
        print(df.to_string(index=False))

    print("\n### Figuras generadas (matplotlib)")
    for figura in visual.generar_todas(con):
        print(f"  {figura}")

    print("\n=== RECOMENDACIÓN DE NEGOCIO ===")
    print(analisis.recomendacion(con)["texto"])
    con.close()


if __name__ == "__main__":
    main()
