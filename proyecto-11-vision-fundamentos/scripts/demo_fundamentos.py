# -*- coding: utf-8 -*-
"""Demo de visión desde cero: aplica cada operación a una imagen sintética y
guarda una figura con el pipeline paso a paso.

Uso:  python scripts/demo_fundamentos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vision import fundamentos as f

plt.switch_backend("Agg")
REPORTS = Path(__file__).resolve().parents[1] / "reports"


def main() -> None:
    img = f.imagen_ejemplo()
    gris = f.a_grises(img)
    blur = f.desenfoque_gaussiano(gris, 5, 1.2)
    bordes = f.bordes_sobel(blur)
    binaria = f.umbral(gris, 70)
    n = f.contar_objetos(binaria)

    pasos = [("1. Original", img), ("2. Grises", gris), ("3. Desenfoque", blur),
             ("4. Bordes (Sobel)", bordes), (f"5. Umbral → {n} objetos", binaria)]
    fig, axes = plt.subplots(1, 5, figsize=(16, 4))
    for ax, (titulo, arr) in zip(axes, pasos):
        ax.imshow(arr, cmap=None if arr.ndim == 3 else "gray")
        ax.set_title(titulo, fontsize=10)
        ax.axis("off")
    fig.suptitle("Visión por computadora desde cero (solo numpy)")
    REPORTS.mkdir(exist_ok=True)
    ruta = REPORTS / "pipeline_vision.png"
    fig.savefig(ruta, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"Objetos detectados: {n}")
    print(f"Figura -> {ruta}")


if __name__ == "__main__":
    main()
