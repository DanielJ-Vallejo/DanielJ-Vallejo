# -*- coding: utf-8 -*-
"""Operaciones de visión por computadora desde cero (solo numpy).

La idea: entender qué hay DEBAJO de las librerías. Una imagen es un arreglo de
números, y casi todo (desenfoque, bordes) es una convolución. Nada de OpenCV/torch.
"""
from __future__ import annotations

import numpy as np

SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
SOBEL_Y = SOBEL_X.T


def a_grises(img_rgb: np.ndarray) -> np.ndarray:
    """RGB -> escala de grises con pesos perceptuales (luminancia)."""
    pesos = np.array([0.299, 0.587, 0.114])
    return img_rgb[..., :3] @ pesos


def convolucion2d(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Convolución 2D desde cero (padding por borde), vectorizada sobre la imagen.

    Recorre las posiciones del kernel (p.ej. 9 para 3x3) y acumula la imagen
    desplazada y multiplicada por cada peso. Esto ES un filtro de imagen.
    """
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2
    pad = np.pad(img, ((ph, ph), (pw, pw)), mode="edge")
    out = np.zeros(img.shape, dtype=float)
    for i in range(kh):
        for j in range(kw):
            out += kernel[i, j] * pad[i:i + img.shape[0], j:j + img.shape[1]]
    return out


def kernel_gaussiano(tam: int = 5, sigma: float = 1.0) -> np.ndarray:
    """Kernel gaussiano normalizado (suma 1) para desenfocar."""
    ejes = np.arange(tam) - tam // 2
    xx, yy = np.meshgrid(ejes, ejes)
    k = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
    return k / k.sum()


def desenfoque_gaussiano(img: np.ndarray, tam: int = 5,
                         sigma: float = 1.0) -> np.ndarray:
    """Suaviza la imagen (quita ruido) convolucionando con un kernel gaussiano."""
    return convolucion2d(img, kernel_gaussiano(tam, sigma))


def bordes_sobel(img_gris: np.ndarray) -> np.ndarray:
    """Magnitud del gradiente (Sobel): resalta los bordes de la imagen."""
    gx = convolucion2d(img_gris, SOBEL_X)
    gy = convolucion2d(img_gris, SOBEL_Y)
    return np.sqrt(gx**2 + gy**2)


def umbral(img: np.ndarray, t: float) -> np.ndarray:
    """Umbralizado binario: 1 donde img > t, 0 en el resto."""
    return (img > t).astype(np.uint8)


def contar_objetos(binaria: np.ndarray) -> int:
    """Cuenta componentes conexas (objetos) en una imagen binaria, desde cero.

    En cada pixel encendido no visitado, hace un flood-fill (vecindad-4) que marca
    todo el objeto. Cada flood-fill nuevo = un objeto más.
    """
    visitado = np.zeros_like(binaria, dtype=bool)
    alto, ancho = binaria.shape
    objetos = 0
    for y in range(alto):
        for x in range(ancho):
            if binaria[y, x] and not visitado[y, x]:
                objetos += 1
                pila = [(y, x)]
                visitado[y, x] = True
                while pila:
                    cy, cx = pila.pop()
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        ny, nx = cy + dy, cx + dx
                        if (0 <= ny < alto and 0 <= nx < ancho
                                and binaria[ny, nx] and not visitado[ny, nx]):
                            visitado[ny, nx] = True
                            pila.append((ny, nx))
    return objetos


def imagen_ejemplo(tam: int = 200, semilla: int = 0) -> np.ndarray:
    """Imagen RGB sintética con 3 formas sobre fondo oscuro (para demo y pruebas)."""
    rng = np.random.default_rng(semilla)
    img = np.full((tam, tam, 3), 30, dtype=np.uint8)
    img[30:80, 40:110] = (220, 80, 80)        # rectángulo
    img[120:170, 30:80] = (80, 220, 120)      # cuadrado
    yy, xx = np.ogrid[:tam, :tam]
    disco = (yy - 140) ** 2 + (xx - 150) ** 2 <= 30 ** 2
    img[disco] = (90, 130, 240)               # disco
    ruido = rng.integers(0, 15, size=img.shape, dtype=np.uint8)
    return np.clip(img.astype(int) + ruido, 0, 255).astype(np.uint8)
