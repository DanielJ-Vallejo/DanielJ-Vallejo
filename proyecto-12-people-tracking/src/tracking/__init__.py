# -*- coding: utf-8 -*-
"""Seguimiento (tracking) de personas: asociación de detecciones entre frames.

La lógica de tracking (IoU + similitud de apariencia + algoritmo Húngaro) está
desacoplada de OpenCV/YOLO para poder probarla: recibe detecciones y descriptores
ya calculados. La parte de cámara/YOLO vive en `scripts/seguir.py`.
"""
__all__ = ["geometria", "descriptor", "tracker"]
