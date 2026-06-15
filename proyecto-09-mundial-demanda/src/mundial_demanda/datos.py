# -*- coding: utf-8 -*-
"""Genera datos sintéticos realistas de demanda hotelera durante el Mundial 2026
y los carga en SQLite.

Determinista (semilla fija) para que las consultas den resultados reproducibles.
Los datos son sintéticos pero modelan patrones reales: la ocupación se dispara en
los días de partido de cada sede y el precio sube MENOS que la demanda (ahí está
la oportunidad de pricing que revela el análisis).
"""
from __future__ import annotations

import os
import random
import sqlite3
from datetime import date, timedelta

SEMILLA = 2026
INICIO = date(2026, 6, 11)
FIN = date(2026, 7, 19)

# Sedes mexicanas del Mundial 2026 y sus días de partido (sintéticos).
PARTIDOS: dict[str, list[date]] = {
    "CDMX": [date(2026, 6, 11), date(2026, 6, 17), date(2026, 6, 24),
             date(2026, 6, 30), date(2026, 7, 5)],
    "Guadalajara": [date(2026, 6, 13), date(2026, 6, 18), date(2026, 6, 23),
                    date(2026, 6, 27)],
    "Monterrey": [date(2026, 6, 14), date(2026, 6, 20), date(2026, 6, 25),
                  date(2026, 6, 29)],
}
CIUDADES = tuple(PARTIDOS)

_OCC_BASE = {"CDMX": 0.58, "Guadalajara": 0.52, "Monterrey": 0.50}
_PRECIO_CIUDAD = {"CDMX": 1.0, "Guadalajara": 0.90, "Monterrey": 0.88}
_BASE_PRECIO = {3: 1100, 4: 1900, 5: 3200}  # MXN por noche según estrellas
_NOMBRES = ["Plaza", "Real", "Centro", "Mirador", "Sol", "Aurora",
            "Catedral", "Jardín", "Reforma", "Alameda"]

DB_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                          "mundial.db")


def _fechas() -> list[date]:
    out, d = [], INICIO
    while d <= FIN:
        out.append(d)
        d += timedelta(days=1)
    return out


def _ocupacion(estrellas: int, ciudad: str, d: date,
               dias_partido: list[date], rng: random.Random) -> float:
    occ = _OCC_BASE[ciudad] + 0.03 * (estrellas - 4)
    if d.weekday() >= 4:                       # vie/sáb/dom
        occ += 0.08
    if d in dias_partido or (d - timedelta(days=1)) in dias_partido:
        occ += 0.38                            # el pico de demanda del partido
    occ += rng.uniform(-0.05, 0.05)
    return round(max(0.30, min(1.0, occ)) * 100, 1)


def _precio(estrellas: int, ciudad: str, ocupacion_pct: float) -> float:
    base = _BASE_PRECIO[estrellas] * _PRECIO_CIUDAD[ciudad]
    # el precio sigue a la demanda solo débilmente -> deja margen sin explotar
    precio = base * (1 + 0.25 * (ocupacion_pct / 100 - 0.5))
    return float(round(precio, -1))


def generar() -> dict[str, list[tuple]]:
    """Devuelve filas para las 3 tablas (hoteles, partidos, ocupacion)."""
    rng = random.Random(SEMILLA)
    hoteles, ocupacion = [], []
    hid = 0
    for ciudad in CIUDADES:
        for nombre in _NOMBRES:
            hid += 1
            estrellas = rng.choices([3, 4, 5], weights=[4, 4, 2])[0]
            habitaciones = rng.randint(40, 200)
            hoteles.append((hid, f"Hotel {nombre}", ciudad, estrellas,
                            habitaciones))
            for d in _fechas():
                occ = _ocupacion(estrellas, ciudad, d, PARTIDOS[ciudad], rng)
                ocupacion.append((hid, d.isoformat(), occ,
                                  _precio(estrellas, ciudad, occ)))
    partidos = [(c, f.isoformat()) for c, fs in PARTIDOS.items() for f in fs]
    return {"hoteles": hoteles, "partidos": partidos, "ocupacion": ocupacion}


def construir_db(path: str = DB_DEFAULT) -> str:
    """(Re)crea la base SQLite con los datos sintéticos. Devuelve la ruta."""
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.remove(path)
    datos = generar()
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE hoteles (
            id INTEGER PRIMARY KEY, nombre TEXT, ciudad TEXT,
            estrellas INTEGER, habitaciones INTEGER
        );
        CREATE TABLE partidos (ciudad TEXT, fecha TEXT);
        CREATE TABLE ocupacion (
            hotel_id INTEGER, fecha TEXT, ocupacion_pct REAL, precio_mxn REAL,
            FOREIGN KEY (hotel_id) REFERENCES hoteles(id)
        );
        """
    )
    con.executemany("INSERT INTO hoteles VALUES (?,?,?,?,?)", datos["hoteles"])
    con.executemany("INSERT INTO partidos VALUES (?,?)", datos["partidos"])
    con.executemany("INSERT INTO ocupacion VALUES (?,?,?,?)", datos["ocupacion"])
    con.commit()
    con.close()
    return path


if __name__ == "__main__":
    ruta = construir_db()
    print(f"Base creada en {ruta}")
