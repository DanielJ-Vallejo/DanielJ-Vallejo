# -*- coding: utf-8 -*-
"""IoU (Intersection over Union) entre cajas en formato (x1, y1, x2, y2)."""
from __future__ import annotations


def iou(caja_a: tuple, caja_b: tuple) -> float:
    """IoU en [0, 1]: 0 = no se solapan, 1 = idénticas."""
    ax1, ay1, ax2, ay2 = caja_a[:4]
    bx1, by1, bx2, by2 = caja_b[:4]
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0
