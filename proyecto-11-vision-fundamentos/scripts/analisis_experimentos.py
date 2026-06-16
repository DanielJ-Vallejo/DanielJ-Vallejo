# -*- coding: utf-8 -*-
"""Análisis comparativo de los 9 experimentos YOLO: imprime la tabla y guarda la
gráfica del trade-off datos/desempeño.

Uso:  python scripts/analisis_experimentos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vision import experimentos

plt.switch_backend("Agg")
REPORTS = Path(__file__).resolve().parents[1] / "reports"


def main() -> None:
    df = experimentos.cargar_runs()
    print(df.to_string(index=False))
    mejor = experimentos.mejor_run()
    print(f"\nMejor run: {mejor['arquitectura']} con {mejor['imagenes']} imágenes "
          f"→ mAP50 {mejor['mAP50']}")

    fig, ax = plt.subplots(figsize=(8, 5))
    for arq, grupo in df.groupby("arquitectura"):
        ax.plot(grupo["imagenes"], grupo["mAP50"], marker="o", label=arq)
    ax.set_xlabel("Imágenes de entrenamiento")
    ax.set_ylabel("mAP@0.5")
    ax.set_title("Trade-off datos vs desempeño — 9 experimentos YOLO (datos reales)")
    ax.legend()
    REPORTS.mkdir(exist_ok=True)
    ruta = REPORTS / "tradeoff_experimentos.png"
    fig.savefig(ruta, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"Figura -> {ruta}")


if __name__ == "__main__":
    main()
