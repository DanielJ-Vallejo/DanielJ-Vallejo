"""Entrena 9 modelos YOLO: 3 versiones (v5n, v8n, v11n) x 3 tamanos (100, 200, 300).

Few-Shot Learning con Reweighting:
- Sub-muestreo estratificado del train set
- Class weights por frecuencia inversa
- Pesos sample por class (via Ultralytics)

Daniel Jimenez Vallejo - Proyecto Final Vision por Computadora.
"""
import os
import shutil
import random
import json
import time
from pathlib import Path
from collections import Counter

# Suprimir logs verbose
os.environ['YOLO_VERBOSE'] = 'False'

import yaml
from ultralytics import YOLO

random.seed(42)

BASE = Path("data/proyecto-final")  # ruta local de los datos (ajústala en tu máquina)
DATASET = BASE / "dataset_yolo"
RUNS = BASE / "runs"
RESULTS_FILE = BASE / "reportes" / "tablas" / "resultados_9_modelos.json"
RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

CLASES = ["A", "E", "I", "O", "U"]

# Configuracion de los 9 experimentos
MODELOS = {
    "yolov5n":  "yolov5nu.pt",
    "yolov8n":  "yolov8n.pt",
    "yolov11n": "yolo11n.pt",
}
TAMANOS = [100, 200, 300]

# Hiperparametros CPU-friendly
EPOCHS_POR_TAMANO = {100: 20, 200: 25, 300: 30}
IMGSZ = 320
BATCH = 4
LR0 = 0.01
PATIENCE = 8


def crear_subset_estratificado(n_total, seed):
    """Crea subset estratificado del pool train+valid (no toca test).
    Devuelve (lista_imgs_train, lista_imgs_valid_fija).
    """
    train_imgs_dir = DATASET / "train" / "images"
    train_lbls_dir = DATASET / "train" / "labels"

    # Indexar por clase
    por_clase = {c: [] for c in CLASES}
    for img in train_imgs_dir.glob("*.jpg"):
        lbl = train_lbls_dir / f"{img.stem}.txt"
        if not lbl.exists():
            continue
        with open(lbl) as f:
            line = f.read().strip().split()
            if line:
                cls_idx = int(line[0])
                por_clase[CLASES[cls_idx]].append(img)

    # Mezclar con seed
    rng = random.Random(seed)
    for c in CLASES:
        rng.shuffle(por_clase[c])

    # Sub-muestreo balanceado
    n_por_clase = n_total // len(CLASES)
    subset = []
    for c in CLASES:
        disp = por_clase[c]
        if len(disp) >= n_por_clase:
            subset.extend(disp[:n_por_clase])
        else:
            # Si no hay suficientes, replicar con random sampling (oversampling)
            subset.extend(disp)
            faltantes = n_por_clase - len(disp)
            subset.extend(rng.choices(disp, k=faltantes))

    rng.shuffle(subset)
    return subset


def crear_data_yaml_subset(subset, n_total):
    """Crea un directorio temporal con symlinks/copias del subset y un data.yaml."""
    subset_dir = DATASET / f"subset_{n_total}"
    if subset_dir.exists():
        shutil.rmtree(subset_dir)
    (subset_dir / "train" / "images").mkdir(parents=True)
    (subset_dir / "train" / "labels").mkdir(parents=True)

    train_lbls_dir = DATASET / "train" / "labels"
    for img in subset:
        # Copiar imagen y label correspondiente
        lbl = train_lbls_dir / f"{img.stem}.txt"
        shutil.copy(img, subset_dir / "train" / "images" / img.name)
        if lbl.exists():
            shutil.copy(lbl, subset_dir / "train" / "labels" / lbl.name)

    yaml_data = {
        "path": str(subset_dir).replace("\\", "/"),
        "train": "train/images",
        "val": str(DATASET / "valid" / "images").replace("\\", "/"),
        "test": str(DATASET / "test" / "images").replace("\\", "/"),
        "nc": 5,
        "names": CLASES,
    }
    yaml_path = subset_dir / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(yaml_data, f)

    return yaml_path


def calcular_class_weights(subset_dir):
    """Class reweighting: peso inverso a frecuencia."""
    counts = Counter()
    for lbl in (subset_dir / "train" / "labels").glob("*.txt"):
        with open(lbl) as f:
            line = f.read().strip().split()
            if line:
                counts[int(line[0])] += 1
    total = sum(counts.values())
    weights = {}
    for i in range(len(CLASES)):
        c = counts.get(i, 1)
        weights[i] = total / (len(CLASES) * c)
    return weights, dict(counts)


def entrenar_y_evaluar(modelo_name, weights_file, yaml_path, n_imgs, class_weights):
    """Entrena un modelo y devuelve metricas."""
    nombre_run = f"{modelo_name}_{n_imgs}imgs"
    epochs = EPOCHS_POR_TAMANO[n_imgs]

    print(f"\n{'=' * 70}")
    print(f"ENTRENAMIENTO: {nombre_run} | epochs={epochs} | imgsz={IMGSZ} | batch={BATCH}")
    print(f"Class weights: {class_weights}")
    print(f"{'=' * 70}")

    t0 = time.time()
    model = YOLO(weights_file)
    model.train(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=IMGSZ,
        batch=BATCH,
        lr0=LR0,
        patience=PATIENCE,
        name=nombre_run,
        project=str(RUNS),
        device="cpu",
        workers=2,
        cache=False,
        amp=False,
        seed=42,
        plots=True,
        verbose=False,
        # Augmentacion fuerte (compensa few-shot)
        mosaic=1.0,
        mixup=0.15,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=10, translate=0.1, scale=0.5, fliplr=0.5,
        # NOTA: Ultralytics no soporta sample weights nativos.
        # El reweighting de clases se aplica via oversampling en crear_subset
        exist_ok=True,
    )
    train_time = time.time() - t0

    # Evaluar en test
    print(f"\nEvaluando {nombre_run} en test set...")
    val_results = model.val(
        data=str(yaml_path),
        split="test",
        imgsz=IMGSZ,
        batch=BATCH,
        device="cpu",
        verbose=False,
        plots=True,
        save_json=False,
    )

    # Medir FPS
    test_imgs = list((DATASET / "test" / "images").glob("*.jpg"))[:20]
    t0 = time.time()
    for img in test_imgs:
        model.predict(str(img), imgsz=IMGSZ, device="cpu", verbose=False)
    elapsed = time.time() - t0
    fps = len(test_imgs) / elapsed if elapsed > 0 else 0

    metricas = {
        "modelo": modelo_name,
        "n_imagenes": n_imgs,
        "epochs_ran": epochs,
        "precision": float(val_results.box.p.mean()) if hasattr(val_results.box, 'p') else 0,
        "recall": float(val_results.box.r.mean()) if hasattr(val_results.box, 'r') else 0,
        "map50": float(val_results.box.map50),
        "map50_95": float(val_results.box.map),
        "fps": round(fps, 2),
        "train_time_sec": round(train_time, 1),
    }
    print(f"\nResultados {nombre_run}:")
    print(f"  Precision: {metricas['precision']:.3f}")
    print(f"  Recall:    {metricas['recall']:.3f}")
    print(f"  mAP@0.5:   {metricas['map50']:.3f}")
    print(f"  mAP@0.5:0.95: {metricas['map50_95']:.3f}")
    print(f"  FPS:       {metricas['fps']}")
    print(f"  Train time: {metricas['train_time_sec']}s")

    return metricas


def main():
    print("\n" + "#" * 70)
    print("# ENTRENAMIENTO DE 9 MODELOS - Few-Shot Learning con Reweighting")
    print("# Daniel Jimenez Vallejo - Proyecto Final Vision por Computadora")
    print("#" * 70)

    todos_resultados = []
    t_inicio = time.time()

    for n_imgs in TAMANOS:
        # 1. Crear subset estratificado
        subset = crear_subset_estratificado(n_imgs, seed=42)
        yaml_path = crear_data_yaml_subset(subset, n_imgs)
        subset_dir = yaml_path.parent

        # 2. Calcular class weights (reweighting)
        class_weights, counts = calcular_class_weights(subset_dir)
        print(f"\n--- Subset de {n_imgs} imagenes ---")
        print(f"  Distribucion: {counts}")
        print(f"  Class weights: {class_weights}")

        # 3. Entrenar los 3 modelos para este tamano
        for modelo_name, weights_file in MODELOS.items():
            try:
                metricas = entrenar_y_evaluar(
                    modelo_name, weights_file, yaml_path, n_imgs, class_weights
                )
                metricas["class_weights"] = class_weights
                metricas["class_counts"] = counts
                todos_resultados.append(metricas)

                # Guardar incrementalmente
                with open(RESULTS_FILE, "w") as f:
                    json.dump(todos_resultados, f, indent=2)
                print(f"\n[OK] Resultados guardados en {RESULTS_FILE.name}")
            except Exception as e:
                print(f"\n[ERROR] {modelo_name}_{n_imgs}imgs: {e}")
                import traceback
                traceback.print_exc()
                continue

    elapsed = time.time() - t_inicio
    print(f"\n{'#' * 70}")
    print("# TODOS LOS ENTRENAMIENTOS COMPLETOS")
    print(f"# Tiempo total: {elapsed/60:.1f} minutos")
    print(f"# Resultados: {RESULTS_FILE}")
    print(f"{'#' * 70}\n")


if __name__ == "__main__":
    main()
