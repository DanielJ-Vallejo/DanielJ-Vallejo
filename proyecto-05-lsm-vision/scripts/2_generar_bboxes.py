"""Convierte el dataset Roboflow (clasificacion por carpetas) a formato YOLO detection
generando bboxes automaticamente con MediaPipe Hands.

Output: dataset_yolo/{train,valid,test}/{images,labels}/
"""
import random
from pathlib import Path
from collections import Counter

import cv2
import mediapipe as mp
from sklearn.model_selection import train_test_split
from tqdm import tqdm

random.seed(42)

# Paths
BASE = Path(r".\Proyecto final")
SRC_LSM = Path(r".\LSM ALL")
OUT = BASE / "dataset_yolo"

# Clases
CLASES = ["A", "E", "I", "O", "U"]
CLASE_TO_IDX = {c: i for i, c in enumerate(CLASES)}

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3,
    model_complexity=1,
)


def detectar_mano(img_path, padding=0.08):
    """Devuelve (xc, yc, w, h) normalizados o None si no detecta mano."""
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)
    if not res.multi_hand_landmarks:
        return None
    lm = res.multi_hand_landmarks[0].landmark
    xs = [p.x for p in lm]
    ys = [p.y for p in lm]
    x1 = max(0.0, min(xs) - padding)
    x2 = min(1.0, max(xs) + padding)
    y1 = max(0.0, min(ys) - padding)
    y2 = min(1.0, max(ys) + padding)
    xc = (x1 + x2) / 2
    yc = (y1 + y2) / 2
    bw = x2 - x1
    bh = y2 - y1
    if bw < 0.05 or bh < 0.05:
        return None
    return (xc, yc, bw, bh)


def recolectar_imagenes_lsm():
    """Junta todas las imagenes del dataset LSM original (todos los splits + originales)."""
    imgs = []  # list of (path, clase)
    for split in ["train", "valid", "test"]:
        for clase in CLASES:
            folder = SRC_LSM / split / clase
            if not folder.exists():
                continue
            for img in folder.glob("*.jpg"):
                imgs.append((img, clase))
    # Tambien los originales sin augmentar
    for clase in CLASES:
        folder = SRC_LSM / "LSM" / clase / clase
        if not folder.exists():
            continue
        for img in folder.glob("*"):
            if img.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                imgs.append((img, clase))
    return imgs


def recolectar_imagenes_scraped():
    """Junta las imagenes scrapeadas si existen."""
    imgs = []
    scraped_dir = BASE / "scraped"
    if not scraped_dir.exists():
        return imgs
    for clase in CLASES:
        folder = scraped_dir / clase
        if not folder.exists():
            continue
        for img in folder.glob("*"):
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}:
                imgs.append((img, clase))
    return imgs


def procesar(pares, split_name, ya_existen):
    """Genera labels YOLO para cada imagen y la copia a dataset_yolo/<split>/."""
    img_dir = OUT / split_name / "images"
    lbl_dir = OUT / split_name / "labels"
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)

    n_ok = 0
    n_fallback = 0
    n_skip = 0

    for src, clase in tqdm(pares, desc=split_name):
        # Generar nombre unico
        stem = f"{clase}_{src.parent.parent.name}_{src.stem}"[:80]
        stem = "".join(c if c.isalnum() or c in "_-" else "_" for c in stem)
        dst_img = img_dir / f"{stem}.jpg"
        dst_lbl = lbl_dir / f"{stem}.txt"

        if dst_img.name in ya_existen:
            # Evitar duplicados
            continue
        ya_existen.add(dst_img.name)

        # Detectar bbox
        bbox = detectar_mano(src)
        if bbox is None:
            # Fallback: bbox centrado cubriendo 90% (asume mano centrada)
            bbox = (0.5, 0.5, 0.9, 0.9)
            n_fallback += 1
        else:
            n_ok += 1

        # Copiar imagen (convertir a JPG si es necesario)
        img = cv2.imread(str(src))
        if img is None:
            n_skip += 1
            continue
        # Resize a 416 para uniformidad
        img = cv2.resize(img, (416, 416), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(dst_img), img, [cv2.IMWRITE_JPEG_QUALITY, 90])

        # Escribir label YOLO
        cls_idx = CLASE_TO_IDX[clase]
        xc, yc, bw, bh = bbox
        with open(dst_lbl, "w") as f:
            f.write(f"{cls_idx} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

    print(f"  [{split_name}] MediaPipe OK: {n_ok}, fallback: {n_fallback}, skip: {n_skip}")
    return n_ok, n_fallback, n_skip


def main():
    print("=" * 70)
    print("Generacion de dataset YOLO con bboxes auto-anotados")
    print("=" * 70)

    # 1. Recolectar
    lsm_imgs = recolectar_imagenes_lsm()
    scraped_imgs = recolectar_imagenes_scraped()
    print(f"\nLSM original: {len(lsm_imgs)} imagenes")
    print(f"Scraped:      {len(scraped_imgs)} imagenes")

    # Distribucion
    dist_lsm = Counter(c for _, c in lsm_imgs)
    dist_scr = Counter(c for _, c in scraped_imgs)
    print("\nDistribucion LSM por clase:", dict(dist_lsm))
    print("Distribucion Scraped por clase:", dict(dist_scr))

    todos = lsm_imgs + scraped_imgs
    random.shuffle(todos)

    # 2. Split estratificado 70/15/15
    X = todos
    y = [c for _, c in todos]

    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_trainval, y_trainval,
        test_size=0.176,  # 0.15/0.85 -> 0.176
        random_state=42, stratify=y_trainval
    )

    print(f"\nSplits: train={len(X_train)}, valid={len(X_valid)}, test={len(X_test)}")

    # 3. Procesar
    ya_existen = set()
    procesar(X_train, "train", ya_existen)
    procesar(X_valid, "valid", ya_existen)
    procesar(X_test, "test", ya_existen)

    # 4. Generar data.yaml
    yaml_path = OUT / "data.yaml"
    yaml_content = f"""# Dataset YOLO para deteccion de vocales LSM
# Generado por Daniel Jimenez Vallejo - Proyecto Final Vision por Computadora

path: {str(OUT).replace(chr(92), '/')}
train: train/images
val: valid/images
test: test/images

nc: 5
names: ['A', 'E', 'I', 'O', 'U']
"""
    yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"\ndata.yaml creado: {yaml_path}")

    # 5. Estadisticas finales
    print("\n=== ESTADISTICAS FINALES ===")
    for split in ["train", "valid", "test"]:
        lbls = list((OUT / split / "labels").glob("*.txt"))
        clase_count = Counter()
        for lbl in lbls:
            with open(lbl) as f:
                line = f.read().strip().split()
                if line:
                    clase_count[CLASES[int(line[0])]] += 1
        print(f"  {split}: {len(lbls)} total -> {dict(clase_count)}")


if __name__ == "__main__":
    main()
