# -*- coding: utf-8 -*-
"""Análisis comparativo de los 9 experimentos YOLO (datos REALES de Daniel).

Lee el results.csv de cada run (arquitectura × tamaño de dataset), toma las
métricas de la última época y arma una tabla para comparar el trade-off
datos/desempeño. Las arquitecturas y tamaños se leen del nombre del archivo.
"""
from __future__ import annotations

import os
import re

import pandas as pd

RUNS = os.path.join(os.path.dirname(__file__), "..", "..", "data", "runs")
_PATRON = re.compile(r"(yolov\d+n)_(\d+)imgs")


def cargar_runs(dir_runs: str = RUNS) -> pd.DataFrame:
    """Tabla (arquitectura, imagenes, mAP50, mAP50_95) — una fila por run."""
    filas = []
    for archivo in sorted(os.listdir(dir_runs)):
        m = _PATRON.search(archivo)
        if not archivo.endswith(".csv") or not m:
            continue
        df = pd.read_csv(os.path.join(dir_runs, archivo))
        df.columns = [c.strip() for c in df.columns]
        ultima = df.iloc[-1]
        filas.append({
            "arquitectura": m.group(1),
            "imagenes": int(m.group(2)),
            "mAP50": round(float(ultima["metrics/mAP50(B)"]), 4),
            "mAP50_95": round(float(ultima["metrics/mAP50-95(B)"]), 4),
        })
    tabla = pd.DataFrame(filas).sort_values(["arquitectura", "imagenes"])
    return tabla.reset_index(drop=True)


def mejor_run(dir_runs: str = RUNS) -> dict:
    """Devuelve el run con mayor mAP50."""
    df = cargar_runs(dir_runs)
    return df.loc[df["mAP50"].idxmax()].to_dict()
