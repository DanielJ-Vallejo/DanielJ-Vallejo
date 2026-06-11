# 🤟 Mexican Sign Language Vowel Detection / Detección de Vocales de LSM

> **EN** — Object detection of the five vowels of **Mexican Sign Language (LSM)** with
> YOLO under a **few-shot learning** regime: 9 trainings (3 architectures × 3 dataset
> sizes) quantifying exactly how much data a low-resource sign language task needs.
> Final project for the Computer Vision course (UNAM).
>
> **ES** — Detección de objetos de las cinco vocales de la **Lengua de Señas Mexicana
> (LSM)** con YOLO bajo régimen de **few-shot learning**: 9 entrenamientos (3
> arquitecturas × 3 tamaños de dataset) que cuantifican cuántos datos necesita una tarea
> de lengua de señas con pocos recursos. Proyecto final del curso de Visión por
> Computadora (UNAM).

![YOLO](https://img.shields.io/badge/YOLO-v5%2Fv8%2Fv11-purple) ![Few-shot](https://img.shields.io/badge/regime-few--shot-yellow) ![mAP@0.5](https://img.shields.io/badge/best%20mAP%4050-0.853-brightgreen)

---

## 🇬🇧 English

### Motivation

Around **2.4 million people in Mexico** have hearing disabilities and use LSM. Unlike
American Sign Language, LSM datasets are scarce — a realistic system must learn from
very few examples. This project measures the data/performance trade-off directly.

### Experimental design

- **Dataset**: ~500 images of LSM vowel signs (A, E, I, O, U) — Roboflow LSM data plus
  self-collected images, annotated in YOLO format.
- **Grid**: {YOLOv5n, YOLOv8n, YOLOv11n} × {100, 200, 300 training images},
  identical hyperparameters, fixed validation split → **9 runs**.
- **Class rebalancing (reweighting)** to compensate uneven vowel frequency.

### Results (held-out test set)

| Model | Images | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|---|---|---|---|---|---|
| YOLOv5n | 300 | 0.838 | 0.655 | 0.805 | 0.624 |
| **YOLOv8n** | **300** | 0.669 | **0.762** | **0.853** | **0.686** |
| YOLOv11n | 300 | 0.822 | 0.751 | 0.810 | 0.623 |

Key findings:
- Tripling the data (100 → 300 images) lifts mAP@0.5 by **+0.26 on average** — in this
  regime data beats architecture: the gap between the worst and best *architecture* at
  300 images (0.05) is five times smaller than the gap from *data* size.
- YOLOv8n offers the best recall/mAP balance — preferable when missing a sign is more
  costly than a false positive (assistive-technology setting).

### Repository contents

```
proyecto-05-lsm-vision/
├── notebooks/proyecto_final_LSM.ipynb  # full report: EDA, training, evaluation
├── scripts/                            # data collection → bboxes → 9 trainings → figures
├── reports/figures/                    # mAP vs dataset size, confusion matrix, ...
└── reports/tables/                     # per-run metrics (9 models)
```

> Dataset images are not redistributed (Roboflow license + personal images).

---

## 🇪🇸 Español

### Motivación

Cerca de **2.4 millones de personas en México** tienen discapacidad auditiva y usan LSM.
A diferencia del lenguaje de señas americano, los datasets de LSM son escasos — un
sistema realista debe aprender con muy pocos ejemplos. Este proyecto mide directamente el
compromiso datos/desempeño.

### Diseño experimental

- **Dataset**: ~500 imágenes de vocales de LSM (A, E, I, O, U) — datos de Roboflow LSM
  más imágenes propias, anotadas en formato YOLO.
- **Malla**: {YOLOv5n, YOLOv8n, YOLOv11n} × {100, 200, 300 imágenes de entrenamiento},
  hiperparámetros idénticos, validación fija → **9 corridas**.
- **Rebalanceo de clases (reweighting)** para compensar la frecuencia desigual de vocales.

### Hallazgos clave

- Triplicar los datos (100 → 300 imágenes) sube el mAP@0.5 **+0.26 en promedio** — en
  este régimen los datos le ganan a la arquitectura: la brecha entre la peor y la mejor
  *arquitectura* con 300 imágenes (0.05) es cinco veces menor que la brecha por *cantidad
  de datos*.
- YOLOv8n logra el mejor balance recall/mAP (mAP@0.5 = **0.853**) — preferible cuando
  perder una seña cuesta más que un falso positivo (contexto de tecnología asistiva).
