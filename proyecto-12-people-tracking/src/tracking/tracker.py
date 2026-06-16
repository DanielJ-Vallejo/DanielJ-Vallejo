# -*- coding: utf-8 -*-
"""Tracker de personas sin entrenamiento.

Asocia las detecciones de cada frame con los tracks existentes combinando dos
señales — solapamiento espacial (IoU) y similitud de apariencia (coseno sobre el
histograma HSV) — y resuelve la asignación óptima con el algoritmo Húngaro.
Cada persona recibe un ID entero estable mientras siga siendo vista.

Diseño original de Daniel (práctica de seguimiento de personas), reempaquetado y
desacoplado de OpenCV para ser reproducible y probable.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from .descriptor import cosine_similarity
from .geometria import compute_iou


class Track:
    """Una persona en seguimiento: ID, última caja y descriptor visual (EMA)."""

    def __init__(self, track_id: int, bbox: tuple, feature: np.ndarray):
        self.track_id = track_id
        self.bbox = bbox
        self.feature = np.asarray(feature, dtype=float).copy()
        self.hits = 1
        self.time_since_update = 0

    def update(self, bbox: tuple, feature: np.ndarray, ema_alpha: float = 0.7):
        """Confirma el track con una nueva detección; suaviza el descriptor (EMA)."""
        self.bbox = bbox
        self.feature = ema_alpha * self.feature + (1.0 - ema_alpha) * np.asarray(
            feature, dtype=float)
        self.hits += 1
        self.time_since_update = 0

    def mark_missed(self):
        self.time_since_update += 1


class PersonTracker:
    """Mantiene los tracks activos y los actualiza frame a frame."""

    def __init__(self, max_age: int = 30, min_similarity: float = 0.5,
                 iou_weight: float = 0.5):
        self.max_age = max_age
        self.min_similarity = min_similarity
        self.iou_weight = iou_weight
        self.tracks: list[Track] = []
        self._next_id = 1

    def _build_score_matrix(self, detections: list, det_features: list) -> np.ndarray:
        score = np.zeros((len(self.tracks), len(detections)), dtype=np.float32)
        for i, track in enumerate(self.tracks):
            for j, det in enumerate(detections):
                iou = compute_iou(track.bbox, det[:4])
                sim = cosine_similarity(track.feature, det_features[j])
                blend = self.iou_weight * iou + (1.0 - self.iou_weight) * sim
                # max(blend, sim): en cortes de escena el IoU cae a 0; permitir
                # un match por sola apariencia evita reasignar IDs nuevos.
                score[i, j] = max(blend, sim)
        return score

    def _create_track(self, bbox: tuple, feature: np.ndarray):
        self.tracks.append(Track(self._next_id, bbox, feature))
        self._next_id += 1

    def _remove_dead_tracks(self):
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

    def update(self, detections: list, det_features: list) -> list[Track]:
        """Asocia las detecciones del frame (con sus descriptores ya calculados)
        y devuelve los tracks confirmados en este frame."""
        if not self.tracks:
            for det, feat in zip(detections, det_features):
                self._create_track(det[:4], feat)
            return [t for t in self.tracks if t.time_since_update == 0]

        if not detections:
            for t in self.tracks:
                t.mark_missed()
            self._remove_dead_tracks()
            return []

        score = self._build_score_matrix(detections, det_features)
        row_ind, col_ind = linear_sum_assignment(-score)  # Húngaro maximiza score
        matched_t, matched_d = set(), set()
        for r, c in zip(row_ind, col_ind):
            if score[r, c] >= self.min_similarity:
                self.tracks[r].update(detections[c][:4], det_features[c])
                matched_t.add(r)
                matched_d.add(c)

        for i, t in enumerate(self.tracks):
            if i not in matched_t:
                t.mark_missed()
        for j, (det, feat) in enumerate(zip(detections, det_features)):
            if j not in matched_d:
                self._create_track(det[:4], feat)

        self._remove_dead_tracks()
        return [t for t in self.tracks if t.time_since_update == 0]
