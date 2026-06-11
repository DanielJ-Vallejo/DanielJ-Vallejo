"""Genera todas las graficas y tablas para el reporte final.

Daniel Jimenez Vallejo - Proyecto Final Vision por Computadora.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
from pathlib import Path
from ultralytics import YOLO
import cv2

BASE      = Path(r".\Proyecto final")
DATASET   = BASE / "dataset_yolo"
RUNS      = BASE / "runs"
REPORTES  = BASE / "reportes"
FIGURAS   = REPORTES / "figuras"
TABLAS    = REPORTES / "tablas"
RESULTS_FILE = TABLAS / "resultados_9_modelos.json"
CLASES    = ["A", "E", "I", "O", "U"]

FIGURAS.mkdir(parents=True, exist_ok=True)
TABLAS.mkdir(parents=True, exist_ok=True)

COLORES = {"yolov5n": "#e74c3c", "yolov8n": "#3498db", "yolov11n": "#2ecc71"}
TAMANOS = [100, 200, 300]

with open(RESULTS_FILE) as f:
    resultados = json.load(f)
df = pd.DataFrame(resultados)

plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold"})


# ── 1. mAP@0.5 vs tamano de dataset ─────────────────────────────────────────
print("Generando figura 1: mAP vs tamano...")
fig, ax = plt.subplots(figsize=(8, 5))
for modelo, color in COLORES.items():
    vals = [df[(df.modelo == modelo) & (df.n_imagenes == n)]["map50"].values[0]
            for n in TAMANOS]
    ax.plot(TAMANOS, vals, "o-", color=color, label=modelo, linewidth=2.5, markersize=8)
    for n, v in zip(TAMANOS, vals):
        ax.annotate(f"{v:.3f}", (n, v), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9, color=color)

ax.set_xlabel("Tamaño del dataset (imágenes de entrenamiento)")
ax.set_ylabel("mAP@0.5")
ax.set_title("mAP@0.5 vs Tamaño de Dataset\n(tendencia a la estabilización progresiva)")
ax.set_xticks(TAMANOS)
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(0.4, 1.0)
plt.tight_layout()
plt.savefig(FIGURAS / "1_map_vs_tamano.png", dpi=150, bbox_inches="tight")
plt.close()
print("  OK: 1_map_vs_tamano.png")


# ── 2. Precision y Recall por modelo (dataset 300) ──────────────────────────
print("Generando figura 2: Precision y Recall...")
fig, ax = plt.subplots(figsize=(8, 5))
df300 = df[df.n_imagenes == 300].sort_values("modelo")
modelos = df300["modelo"].tolist()
precs   = df300["precision"].tolist()
recalls = df300["recall"].tolist()
maps    = df300["map50"].tolist()
x = np.arange(len(modelos))
w = 0.25
b1 = ax.bar(x - w, precs,   w, label="Precisión",  color="#3498db", alpha=0.85)
b2 = ax.bar(x,     recalls, w, label="Recall",      color="#e74c3c", alpha=0.85)
b3 = ax.bar(x + w, maps,    w, label="mAP@0.5",     color="#2ecc71", alpha=0.85)
for bars in [b1, b2, b3]:
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8)
ax.set_xticks(x)
ax.set_xticklabels(modelos)
ax.set_ylabel("Valor")
ax.set_title("Precisión, Recall y mAP@0.5 — Dataset 300 imágenes")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
ax.set_ylim(0, 1.05)
plt.tight_layout()
plt.savefig(FIGURAS / "2_prec_recall_300.png", dpi=150, bbox_inches="tight")
plt.close()
print("  OK: 2_prec_recall_300.png")


# ── 3. Evolucion de metricas por modelo (subplots) ──────────────────────────
print("Generando figura 3: Evolucion metricas...")
metricas = ["precision", "recall", "map50", "map50_95"]
labels   = ["Precisión", "Recall", "mAP@0.5", "mAP@0.5:0.95"]
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, met, lbl in zip(axes.flat, metricas, labels):
    for modelo, color in COLORES.items():
        vals = [df[(df.modelo == modelo) & (df.n_imagenes == n)][met].values[0]
                for n in TAMANOS]
        ax.plot(TAMANOS, vals, "o-", color=color, label=modelo, linewidth=2, markersize=6)
    ax.set_title(lbl)
    ax.set_xticks(TAMANOS)
    ax.set_xlabel("Imágenes")
    ax.set_ylabel(lbl)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.3, 1.0)
plt.suptitle("Evolución de Métricas por Modelo y Tamaño de Dataset", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURAS / "3_evolucion_metricas.png", dpi=150, bbox_inches="tight")
plt.close()
print("  OK: 3_evolucion_metricas.png")


# ── 4. FPS por configuracion ─────────────────────────────────────────────────
print("Generando figura 4: FPS...")
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(resultados))
fps_vals = [r["fps"] for r in resultados]
etiq     = [f"{r['modelo']}\n{r['n_imagenes']}imgs" for r in resultados]
bars = ax.bar(x, fps_vals, color=[COLORES[r["modelo"]] for r in resultados], alpha=0.85, width=0.6)
for bar, v in zip(bars, fps_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            f"{v:.1f}", ha="center", va="bottom", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(etiq, fontsize=8)
ax.set_ylabel("FPS (CPU)")
ax.set_title("FPS por Configuración de Entrenamiento (CPU)")
patches = [mpatches.Patch(color=c, label=m) for m, c in COLORES.items()]
ax.legend(handles=patches)
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(FIGURAS / "4_fps.png", dpi=150, bbox_inches="tight")
plt.close()
print("  OK: 4_fps.png")


# ── 5. Matriz de confusion del mejor modelo ──────────────────────────────────
print("Generando figura 5: Matriz de confusion del mejor modelo...")
best = df.loc[df["map50"].idxmax()]
best_run = f"{best['modelo']}_{int(best['n_imagenes'])}imgs"
cm_path  = RUNS / best_run / "confusion_matrix_normalized.png"

if cm_path.exists():
    img = cv2.imread(str(cm_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(img)
    ax.axis("off")
    ax.set_title(f"Matriz de Confusión Normalizada — {best_run}\n(mAP@0.5={best['map50']:.3f})",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURAS / "5_confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("  OK: 5_confusion_matrix.png (de YOLO runs)")
else:
    # Calcular manualmente con el modelo
    best_pt = RUNS / best_run / "weights" / "best.pt"
    if best_pt.exists():
        model = YOLO(str(best_pt))
        val_res = model.val(
            data=str(DATASET / "data.yaml"),
            split="test", imgsz=320, batch=4, device="cpu",
            verbose=False, plots=False
        )
        # Extraer confusion matrix
        cm = val_res.confusion_matrix.matrix[:5, :5]
        cm_norm = cm / (cm.sum(axis=1, keepdims=True) + 1e-6)
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
                    xticklabels=CLASES, yticklabels=CLASES, ax=ax)
        ax.set_xlabel("Predicción")
        ax.set_ylabel("Real")
        ax.set_title(f"Matriz de Confusión Normalizada — {best_run}", fontweight="bold")
        plt.tight_layout()
        plt.savefig(FIGURAS / "5_confusion_matrix.png", dpi=150, bbox_inches="tight")
        plt.close()
        print("  OK: 5_confusion_matrix.png (calculada)")
    else:
        print(f"  SKIP: no se encontro {best_pt}")


# ── 6. Distribucion del dataset (EDA) ────────────────────────────────────────
print("Generando figura 6: Distribucion dataset...")
distrib = {
    "train": {"A": 25, "E": 20, "I": 19, "O": 76, "U": 70},
    "valid": {"A": 4,  "E": 2,  "I": 2,  "O": 15, "U": 15},
    "test":  {"A": 4,  "E": 2,  "I": 1,  "O": 17, "U": 17},
}
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
cols = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]
for ax, (split, counts) in zip(axes, distrib.items()):
    bars = ax.bar(counts.keys(), counts.values(), color=cols)
    ax.set_title(f"{split.capitalize()}  ({sum(counts.values())} imgs)", fontweight="bold")
    ax.set_xlabel("Clase (vocal LSM)")
    ax.set_ylabel("Cantidad de imágenes")
    for bar, v in zip(bars, counts.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(v), ha="center", va="bottom", fontsize=9)
plt.suptitle("Distribución de Clases por Split — Dataset Vocales LSM", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURAS / "6_distribucion_dataset.png", dpi=150, bbox_inches="tight")
plt.close()
print("  OK: 6_distribucion_dataset.png")


# ── 7. Tabla resumen CSV ─────────────────────────────────────────────────────
print("Generando tabla resumen CSV...")
df_out = df[["modelo","n_imagenes","precision","recall","map50","map50_95","fps","train_time_sec"]].copy()
df_out.columns = ["Modelo","Imagenes","Precision","Recall","mAP@0.5","mAP@0.5:0.95","FPS","Tiempo_s"]
df_out[["Precision","Recall","mAP@0.5","mAP@0.5:0.95"]] = df_out[["Precision","Recall","mAP@0.5","mAP@0.5:0.95"]].round(3)
df_out.to_csv(TABLAS / "tabla_comparativa.csv", index=False)
print("  OK: tabla_comparativa.csv")

resumen = df.groupby("modelo").agg(
    Precision_media=("precision","mean"),
    Recall_medio=("recall","mean"),
    mAP50_medio=("map50","mean"),
    FPS_medio=("fps","mean"),
).round(3).reset_index()
resumen.to_csv(TABLAS / "tabla_resumen_por_modelo.csv", index=False)
print("  OK: tabla_resumen_por_modelo.csv")


print("\n=== TODAS LAS FIGURAS GENERADAS ===")
for f in sorted(FIGURAS.glob("*.png")):
    print(f"  {f.name}")
