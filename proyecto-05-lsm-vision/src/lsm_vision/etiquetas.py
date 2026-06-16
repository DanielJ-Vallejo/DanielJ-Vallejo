# -*- coding: utf-8 -*-
"""Etiquetas en formato YOLO: una línea por caja = `clase cx cy w h`,
con cx, cy, w, h normalizados (0–1) respecto al tamaño de la imagen.
"""
from __future__ import annotations

from collections import Counter


def parsear_label(texto: str) -> list[dict]:
    """Convierte el contenido de un .txt YOLO en una lista de cajas."""
    cajas = []
    for linea in texto.strip().splitlines():
        partes = linea.split()
        if len(partes) != 5:
            continue
        clase, cx, cy, w, h = partes
        cajas.append({"clase": int(clase), "cx": float(cx), "cy": float(cy),
                      "w": float(w), "h": float(h)})
    return cajas


def yolo_a_xyxy(cx: float, cy: float, w: float, h: float,
                ancho_img: int, alto_img: int) -> tuple:
    """Convierte (cx,cy,w,h) normalizado a (x1,y1,x2,y2) en píxeles."""
    x1 = (cx - w / 2) * ancho_img
    y1 = (cy - h / 2) * alto_img
    x2 = (cx + w / 2) * ancho_img
    y2 = (cy + h / 2) * alto_img
    return (x1, y1, x2, y2)


def distribucion_clases(labels: list[list[dict]]) -> dict:
    """Cuenta cuántas cajas hay por clase en un conjunto de labels."""
    cuenta: Counter = Counter()
    for cajas in labels:
        for caja in cajas:
            cuenta[caja["clase"]] += 1
    return dict(cuenta)
