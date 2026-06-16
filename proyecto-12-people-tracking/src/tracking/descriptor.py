# -*- coding: utf-8 -*-
"""Similitud de apariencia entre descriptores (histogramas de color HSV).

El histograma en sí se calcula en `scripts/seguir.py` (necesita OpenCV); aquí
solo va la comparación, que es pura álgebra y se puede probar.
"""
from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Similitud del coseno en [0, 1] para vectores no negativos (histogramas)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))
