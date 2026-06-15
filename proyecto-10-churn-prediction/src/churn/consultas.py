# -*- coding: utf-8 -*-
"""Segmentos de churn en SQL (sin interpolar valores -> seguras para bandit).

Muestran el manejo de SQL para análisis: agregación con GROUP BY, conteos y
tasas por segmento, y categorización con CASE WHEN.
"""
from __future__ import annotations

import sqlite3

# Tasa de abandono por tipo de contrato.
TASA_POR_CONTRATO = """
SELECT tipo_contrato,
       COUNT(*)                              AS clientes,
       ROUND(AVG(churn) * 100, 1)            AS churn_pct,
       ROUND(AVG(cargo_mensual))             AS cargo_prom
FROM clientes
GROUP BY tipo_contrato
ORDER BY churn_pct DESC;
"""

# Tasa de abandono por antigüedad (buckets de tenure).
TASA_POR_TENURE = """
SELECT CASE
         WHEN tenure_meses < 12 THEN '0-11 meses'
         WHEN tenure_meses < 24 THEN '12-23 meses'
         WHEN tenure_meses < 48 THEN '24-47 meses'
         ELSE '48+ meses'
       END                            AS antiguedad,
       COUNT(*)                       AS clientes,
       ROUND(AVG(churn) * 100, 1)     AS churn_pct
FROM clientes
GROUP BY antiguedad
ORDER BY churn_pct DESC;
"""

# Tasa de abandono según llamadas a soporte.
TASA_POR_SOPORTE = """
SELECT CASE WHEN llamadas_soporte >= 3 THEN '3+ llamadas'
            ELSE '0-2 llamadas' END   AS soporte,
       COUNT(*)                       AS clientes,
       ROUND(AVG(churn) * 100, 1)     AS churn_pct
FROM clientes
GROUP BY soporte
ORDER BY churn_pct DESC;
"""

CONSULTAS = {
    "Churn por tipo de contrato": TASA_POR_CONTRATO,
    "Churn por antigüedad": TASA_POR_TENURE,
    "Churn por llamadas a soporte": TASA_POR_SOPORTE,
}


def correr(con: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]:
    """Ejecuta una consulta y devuelve (columnas, filas)."""
    cur = con.execute(sql)
    return [d[0] for d in cur.description], cur.fetchall()
