# -*- coding: utf-8 -*-
"""Consultas SQL de negocio sobre la base del Mundial.

Las consultas se guardan como constantes (sin interpolar valores -> seguras) para
que sirvan de muestra del manejo de SQL: JOIN entre tablas, LEFT JOIN para marcar
días de partido, agregación con GROUP BY y orden.
"""
from __future__ import annotations

import sqlite3

# Ocupación y precio promedio por ciudad.
OCUPACION_POR_CIUDAD = """
SELECT h.ciudad,
       ROUND(AVG(o.ocupacion_pct), 1) AS ocupacion_pct,
       ROUND(AVG(o.precio_mxn))       AS precio_mxn
FROM ocupacion o
JOIN hoteles h ON h.id = o.hotel_id
GROUP BY h.ciudad
ORDER BY ocupacion_pct DESC;
"""

# Top 10 fechas-ciudad de mayor demanda, marcando si hubo partido (LEFT JOIN).
TOP_DEMANDA = """
SELECT o.fecha,
       h.ciudad,
       ROUND(AVG(o.ocupacion_pct), 1) AS ocupacion_pct,
       CASE WHEN p.fecha IS NOT NULL THEN 'partido' ELSE '' END AS evento
FROM ocupacion o
JOIN hoteles h ON h.id = o.hotel_id
LEFT JOIN partidos p ON p.ciudad = h.ciudad AND p.fecha = o.fecha
GROUP BY o.fecha, h.ciudad
ORDER BY ocupacion_pct DESC
LIMIT 10;
"""

# El hallazgo clave: día de partido vs día normal (demanda y precio).
PARTIDO_VS_NORMAL = """
SELECT CASE WHEN p.fecha IS NOT NULL THEN 'Día de partido'
            ELSE 'Día normal' END         AS tipo,
       ROUND(AVG(o.ocupacion_pct), 1)     AS ocupacion_pct,
       ROUND(AVG(o.precio_mxn))           AS precio_mxn,
       COUNT(*)                           AS registros
FROM ocupacion o
JOIN hoteles h ON h.id = o.hotel_id
LEFT JOIN partidos p ON p.ciudad = h.ciudad AND p.fecha = o.fecha
GROUP BY tipo
ORDER BY ocupacion_pct DESC;
"""

# Hoteles con mayor ingreso estimado (ocupación x precio x habitaciones).
TOP_HOTELES_INGRESO = """
SELECT h.nombre,
       h.ciudad,
       ROUND(SUM(o.ocupacion_pct / 100.0 * o.precio_mxn * h.habitaciones)) AS ingreso_mxn
FROM ocupacion o
JOIN hoteles h ON h.id = o.hotel_id
GROUP BY h.id
ORDER BY ingreso_mxn DESC
LIMIT 5;
"""

CONSULTAS = {
    "Ocupación y precio por ciudad": OCUPACION_POR_CIUDAD,
    "Top fechas de mayor demanda": TOP_DEMANDA,
    "Día de partido vs día normal": PARTIDO_VS_NORMAL,
    "Hoteles con mayor ingreso": TOP_HOTELES_INGRESO,
}


def correr(con: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]:
    """Ejecuta una consulta y devuelve (columnas, filas)."""
    cur = con.execute(sql)
    columnas = [d[0] for d in cur.description]
    return columnas, cur.fetchall()
