# 🗣️ Spanish Sentiment Analysis — MeIA 2025 / Análisis de Sentimientos en Español

> **EN** — Fine-tuning of **BETO** (Spanish BERT) for 5-class polarity prediction of
> Mexican tourism reviews. Built for the **MeIA 2025 challenge** (Macroentrenamiento en
> Inteligencia Artificial, UNAM), where this configuration scored **0.5889** on the
> leaderboard as team *Moodhacker4Neurona*.
>
> **ES** — Fine-tuning de **BETO** (BERT en español) para predicción de polaridad en 5
> clases sobre reseñas turísticas mexicanas. Construido para el **reto MeIA 2025**
> (Macroentrenamiento en Inteligencia Artificial, UNAM), donde esta configuración obtuvo
> **0.5889** en el leaderboard como equipo *Moodhacker4Neurona*.

![Python](https://img.shields.io/badge/python-3.11-blue) ![transformers](https://img.shields.io/badge/🤗-transformers-yellow) ![BETO](https://img.shields.io/badge/model-BETO-red)

---

## 🇪🇸 Español

### Tarea

Dadas ~5,000 reseñas tipo TripAdvisor de destinos mexicanos (texto + región, ciudad y
tipo de servicio), predecir una calificación de polaridad 1–5. La polaridad fina en
español es difícil: la frontera entre 3 y 4 estrellas es subjetiva, las clases están
desbalanceadas y las reseñas mezclan dialectos.

### Enfoque

| Componente | Decisión | Por qué |
|---|---|---|
| Modelo base | `dccuchile/bert-base-spanish-wwm-uncased` (BETO) | Mejor modelo monolingüe en español disponible para el reto |
| Entrada de texto | `[REGION: x] [TOWN: y] [SERVICE: z] <reseña>` | La atención condiciona la polaridad al contexto (hotel ≠ restaurante) |
| Desbalance | Sobremuestreo aleatorio de la clase minoritaria | Recupera macro-F1 en reseñas raras de 1–2 estrellas |
| Regularización | Dropout 0.4/0.3 + weight decay 0.1 + **primeras 6 capas congeladas** | Con ~5k muestras, el fine-tuning completo sobreajusta en 2 épocas |
| Calendario | Decaimiento coseno, 10% warmup, early stopping sobre macro-F1 | Estabilidad con learning rate 2e-5 |

### Resultado

**Score 0.5889** en el leaderboard del reto MeIA 2025 (equipo *Moodhacker4Neurona*).
El archivo de predicciones oficial está en `reports/runs/`.

### Estructura

```
proyecto-02-sentiment-analysis/
├── src/sentiment_analysis/   # config, data (enriquecimiento, oversampling), train
├── scripts/train_meia.py     # entrenamiento end-to-end + run file oficial
├── notebooks/                # notebook original del reto (Colab)
├── reports/runs/             # predicciones enviadas al leaderboard
└── tests/                    # tests de preparación de datos (sin GPU)
```

---

## 🇬🇧 English

### Task

Given ~5,000 TripAdvisor-style reviews of Mexican destinations (text + region, town and
service type), predict a 1–5 polarity rating. Fine-grained polarity in Spanish is hard:
the boundary between 3 and 4 stars is subjective, class distribution is skewed, and
reviews mix dialects and code-switching.

### Approach

| Component | Decision | Why |
|---|---|---|
| Backbone | `dccuchile/bert-base-spanish-wwm-uncased` (BETO) | Best Spanish monolingual model available for the challenge |
| Text input | `[REGION: x] [TOWN: y] [SERVICE: z] <review>` | Lets attention condition polarity on context (hotels ≠ restaurants) |
| Imbalance | Random oversampling of the minority class | Recovers macro-F1 on rare 1–2 star reviews |
| Regularization | Dropout 0.4/0.3 + weight decay 0.1 + **first 6 encoder layers frozen** | ~5k training samples: full fine-tuning overfits in 2 epochs |
| Schedule | Cosine decay, 10% warmup, early stopping on macro-F1 | Stability at 2e-5 learning rate |

### Reproduce

```bash
pip install -r requirements.txt
# place MeIA_2025_train.xlsx / MeIA_2025_test_wo_labels.xlsx in ../data/raw/sentiment-analysis/
python scripts/train_meia.py        # needs GPU (or run the notebook in Colab)
pytest tests/ -q                    # data-prep tests, no GPU needed
```

The official run file submitted to the challenge is preserved in
`reports/runs/MeIA-Moodhacker4neurona.Run.txt`.

> **Note** — the MeIA 2025 dataset belongs to the challenge organizers and is **not
> redistributed** in this repository.
