"""Pruebas de la lógica de tracking (sin cámara ni YOLO): IoU, similitud, IDs."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracking.descriptor import cosine_similarity
from tracking.geometria import compute_iou
from tracking.tracker import PersonTracker


def test_iou():
    assert compute_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert compute_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert 0.0 < compute_iou((0, 0, 10, 10), (5, 5, 15, 15)) < 1.0


def test_cosine_similarity():
    assert cosine_similarity(np.array([1.0, 0]), np.array([1.0, 0])) == 1.0
    assert cosine_similarity(np.array([1.0, 0]), np.array([0.0, 1])) == 0.0


def test_ids_estables_entre_frames():
    t = PersonTracker(min_similarity=0.3)
    feats = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    out1 = t.update([(0, 0, 10, 20, 0.9), (50, 0, 60, 20, 0.9)], feats)
    assert sorted(tr.track_id for tr in out1) == [1, 2]
    # mismas personas, cajas movidas un poco (IoU alto) -> mismos IDs
    out2 = t.update([(1, 0, 11, 20, 0.9), (51, 0, 61, 20, 0.9)], feats)
    assert sorted(tr.track_id for tr in out2) == [1, 2]


def test_objeto_nuevo_recibe_id_nuevo():
    t = PersonTracker(min_similarity=0.3)
    t.update([(0, 0, 10, 20, 0.9)], [np.array([1.0, 0.0])])
    out = t.update([(0, 0, 10, 20, 0.9), (100, 100, 110, 120, 0.9)],
                   [np.array([1.0, 0.0]), np.array([0.0, 1.0])])
    assert len(out) == 2
    assert max(tr.track_id for tr in out) == 2


def test_track_muere_tras_max_age():
    t = PersonTracker(max_age=2, min_similarity=0.3)
    t.update([(0, 0, 10, 20, 0.9)], [np.array([1.0, 0.0])])
    for _ in range(4):
        t.update([], [])
    assert t.tracks == []
