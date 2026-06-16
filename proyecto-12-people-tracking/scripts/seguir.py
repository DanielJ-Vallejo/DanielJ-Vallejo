# -*- coding: utf-8 -*-
"""Seguimiento de personas en video/webcam: YOLO detecta, el tracker asigna IDs.

Requiere las dependencias de la app (no las de prueba):
    pip install -r requirements-app.txt
Uso:
    python scripts/seguir.py --fuente 0             # webcam
    python scripts/seguir.py --fuente video.mp4     # archivo de video
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracking.tracker import PersonTracker

H_BINS, S_BINS = 16, 16


def extract_features(frame: np.ndarray, bbox: tuple) -> np.ndarray:
    """Histograma de color HSV del torso de la persona (descriptor visual)."""
    x1, y1, x2, y2 = (int(v) for v in bbox[:4])
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    if x2 <= x1 or y2 <= y1:
        return np.zeros(H_BINS * S_BINS, dtype=np.float32)
    crop = frame[y1:y2, x1:x2]
    alto = crop.shape[0]
    crop = crop[alto // 4: 3 * alto // 4, :]          # torso (evita fondo)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [H_BINS, S_BINS],
                        [0, 180, 0, 256]).flatten()
    total = hist.sum()
    return hist / total if total > 0 else hist


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fuente", default="0", help="0 = webcam, o ruta a un video")
    ap.add_argument("--modelo", default="yolov8n.pt")
    args = ap.parse_args()

    fuente = int(args.fuente) if args.fuente.isdigit() else args.fuente
    modelo = YOLO(args.modelo)
    tracker = PersonTracker()
    cap = cv2.VideoCapture(fuente)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        res = modelo(frame, classes=[0], verbose=False)[0]   # clase 0 = persona
        dets = [(*(int(v) for v in b.xyxy[0]), float(b.conf)) for b in res.boxes]
        feats = [extract_features(frame, d[:4]) for d in dets]
        for t in tracker.update(dets, feats):
            x1, y1, x2, y2 = (int(v) for v in t.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {t.track_id}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Seguimiento de personas", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
