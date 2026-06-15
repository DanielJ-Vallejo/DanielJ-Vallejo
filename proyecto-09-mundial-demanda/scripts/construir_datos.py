# -*- coding: utf-8 -*-
"""Crea (o recrea) la base SQLite con los datos sintéticos del Mundial.

Uso:  python scripts/construir_datos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mundial_demanda.datos import construir_db

if __name__ == "__main__":
    ruta = construir_db()
    print(f"Base creada en {ruta}")
