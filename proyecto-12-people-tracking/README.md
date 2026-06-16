# 🚶 Seguimiento de Personas / People Tracking (YOLO + IoU + apariencia)

> **ES** — Sistema de **tracking multi-objeto** que detecta personas con YOLO y les
> asigna un **ID estable** entre frames, combinando solapamiento espacial (IoU) y
> similitud de apariencia (histograma HSV), con asignación óptima por **algoritmo
> Húngaro**. La lógica de tracking está desacoplada de la cámara para poder probarla.
>
> **EN** — A **multi-object tracking** system that detects people with YOLO and assigns
> a **stable ID** across frames, combining spatial overlap (IoU) and appearance
> similarity (HSV histogram), with optimal assignment via the **Hungarian algorithm**.
> Tracking logic is decoupled from the camera so it can be unit-tested.

![Python](https://img.shields.io/badge/python-3.11-blue) ![YOLO](https://img.shields.io/badge/detección-YOLOv8-00FFFF) ![SciPy](https://img.shields.io/badge/asignación-Húngaro%20(SciPy)-8CAAE6) ![tests](https://img.shields.io/badge/tests-6%20passing-brightgreen)

---

## 🇪🇸 Español

### Cómo funciona
1. **Detección:** YOLO encuentra a las personas en cada frame (caja + confianza).
2. **Apariencia:** de cada caja se saca un histograma de color **HSV** del torso.
3. **Asociación:** se calcula un score `max(blend, similitud)` donde
   `blend = w·IoU + (1−w)·coseno`, y el **algoritmo Húngaro** empareja detecciones
   con tracks de forma óptima. (El `max(…)` mantiene el ID aun en cortes de escena,
   donde el IoU cae a 0 pero la apariencia sigue.)
4. **Ciclo de vida:** un track sin actualizarse `max_age` frames se elimina; uno nuevo
   nace cuando aparece una persona sin match.

### Arquitectura (clave del diseño)
La **lógica** (`src/tracking/`) recibe detecciones y descriptores **ya calculados** →
no depende de OpenCV ni YOLO → se prueba con datos sintéticos. La **app**
(`scripts/seguir.py`) hace la parte pesada (YOLO + OpenCV + video).

```
proyecto-12-people-tracking/
├── src/tracking/   # geometria (IoU), descriptor (coseno), tracker (Húngaro + ciclo de vida)
├── scripts/        # seguir.py: YOLO + cámara/video + dibujo (deps en requirements-app.txt)
└── tests/          # 6 pruebas: IoU, similitud, IDs estables, objeto nuevo, muerte de track
```

### Cómo correrlo
```bash
# Pruebas (ligero):
pip install -r requirements.txt && pytest tests -q

# App en vivo (pesado):
pip install -r requirements-app.txt
python scripts/seguir.py --fuente 0            # webcam
python scripts/seguir.py --fuente video.mp4    # archivo
```

---

## 🇬🇧 English

Multi-object people tracker: YOLO detection + HSV-appearance + IoU, associated optimally
with the **Hungarian algorithm**, giving each person a **stable ID**. A `max(blend, sim)`
score keeps IDs through scene cuts (IoU drops to 0 but appearance persists). The tracking
**logic** (`src/tracking/`) is decoupled from OpenCV/YOLO and unit-tested with synthetic
detections (6 tests); the heavy camera/YOLO pipeline lives in `scripts/seguir.py`. Run
`pytest tests -q` for the logic, or `python scripts/seguir.py --fuente 0` for the live demo.
