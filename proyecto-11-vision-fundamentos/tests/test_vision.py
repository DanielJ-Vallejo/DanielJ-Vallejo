"""Pruebas: operaciones de visión desde cero + carga de experimentos reales."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vision import experimentos
from vision import fundamentos as f


def test_convolucion_identidad():
    img = np.arange(25, dtype=float).reshape(5, 5)
    identidad = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=float)
    assert np.allclose(f.convolucion2d(img, identidad), img)


def test_kernel_gaussiano_suma_uno():
    assert np.isclose(f.kernel_gaussiano(5, 1.0).sum(), 1.0)


def test_a_grises_forma():
    img = np.zeros((10, 8, 3), dtype=np.uint8)
    assert f.a_grises(img).shape == (10, 8)


def test_bordes_detecta_el_borde():
    img = np.zeros((10, 10), dtype=float)
    img[:, 5:] = 255                       # un borde vertical
    bordes = f.bordes_sobel(img)
    assert bordes[:, 4:6].max() > bordes[:, 0:2].max()


def test_umbral_binaria():
    img = np.array([[10, 200], [50, 90]], dtype=float)
    assert f.umbral(img, 70).tolist() == [[0, 1], [0, 1]]


def test_contar_objetos():
    b = np.zeros((10, 10), dtype=np.uint8)
    b[1:3, 1:3] = 1                        # objeto 1
    b[6:9, 6:9] = 1                        # objeto 2
    assert f.contar_objetos(b) == 2


def test_cargar_runs():
    df = experimentos.cargar_runs()
    assert len(df) == 9
    assert {"arquitectura", "imagenes", "mAP50", "mAP50_95"} <= set(df.columns)
    assert df["mAP50"].between(0, 1).all()
