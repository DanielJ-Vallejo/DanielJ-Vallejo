# -*- coding: utf-8 -*-
"""De los datos a una recomendación de negocio: pricing en días de partido.

La idea: en los días de partido la demanda casi llena los hoteles, pero el precio
no la acompaña. Eso es dinero sobre la mesa. Aquí se cuantifica y se traduce en
una recomendación accionable para un hotel de las sedes.
"""
from __future__ import annotations

import sqlite3

from . import consultas

# Ingreso estimado total en días de partido (INNER JOIN -> solo esas fechas).
INGRESO_DIAS_PARTIDO = """
SELECT ROUND(SUM(o.ocupacion_pct / 100.0 * o.precio_mxn * h.habitaciones))
FROM ocupacion o
JOIN hoteles h ON h.id = o.hotel_id
JOIN partidos p ON p.ciudad = h.ciudad AND p.fecha = o.fecha;
"""


def recomendacion(con: sqlite3.Connection) -> dict:
    """Calcula la brecha demanda/precio y devuelve una recomendación de pricing."""
    _, filas = consultas.correr(con, consultas.PARTIDO_VS_NORMAL)
    por_tipo = {f[0]: f for f in filas}
    occ_p, precio_p = por_tipo["Día de partido"][1], por_tipo["Día de partido"][2]
    occ_n, precio_n = por_tipo["Día normal"][1], por_tipo["Día normal"][2]

    sube_demanda = (occ_p - occ_n) / occ_n
    sube_precio = (precio_p - precio_n) / precio_n
    brecha = sube_demanda - sube_precio
    # subida sugerida, capada al 20% para no arriesgar la ocupación
    subida = round(min(0.20, max(0.0, brecha)) * 100)

    ingreso_partidos = con.execute(INGRESO_DIAS_PARTIDO).fetchone()[0] or 0
    extra = round(ingreso_partidos * subida / 100)

    texto = (
        f"En días de partido la ocupación promedio sube a {occ_p}% "
        f"(vs {occ_n}% en día normal, +{round(sube_demanda * 100)}%), pero el "
        f"precio solo sube {round(sube_precio * 100)}%. La demanda casi llena los "
        f"hoteles y el precio no la acompaña.\n"
        f"Recomendación: subir las tarifas de día de partido ~{subida}%. Sobre la "
        f"demanda del Mundial en las sedes, eso son ~${extra:,.0f} MXN "
        f"adicionales — sin agregar un solo cuarto."
    )
    return {
        "ocupacion_partido": occ_p,
        "ocupacion_normal": occ_n,
        "precio_partido": precio_p,
        "precio_normal": precio_n,
        "subida_recomendada_pct": subida,
        "ingreso_extra_mxn": extra,
        "texto": texto,
    }
