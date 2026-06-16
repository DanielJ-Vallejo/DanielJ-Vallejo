"""Pruebas de las utilidades reproducibles: etiquetas YOLO e IoU."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsm_vision import etiquetas, iou


def test_parsear_label():
    cajas = etiquetas.parsear_label("0 0.5 0.5 0.2 0.2\n1 0.1 0.1 0.05 0.05\n")
    assert len(cajas) == 2
    assert cajas[0]["clase"] == 0
    assert cajas[0]["cx"] == 0.5


def test_parsear_label_ignora_lineas_malas():
    assert etiquetas.parsear_label("basura\n0 .5 .5 .2 .2") == [
        {"clase": 0, "cx": 0.5, "cy": 0.5, "w": 0.2, "h": 0.2}
    ]


def test_yolo_a_xyxy():
    assert etiquetas.yolo_a_xyxy(0.5, 0.5, 0.2, 0.2, 100, 100) == (40, 40, 60, 60)


def test_distribucion_clases():
    labels = [etiquetas.parsear_label("0 .5 .5 .2 .2\n0 .1 .1 .1 .1"),
              etiquetas.parsear_label("1 .5 .5 .2 .2")]
    assert etiquetas.distribucion_clases(labels) == {0: 2, 1: 1}


def test_iou_identicas():
    assert iou.iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0


def test_iou_sin_solape():
    assert iou.iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_iou_parcial():
    assert 0.0 < iou.iou((0, 0, 10, 10), (5, 5, 15, 15)) < 1.0
