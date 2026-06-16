# 🚢 Titanic Survival Prediction / Predicción de Supervivencia del Titanic

> **EN** — The classic benchmark, done the way it should be done: domain feature
> engineering, **leakage-free** preprocessing inside cross-validated pipelines and honest
> holdout evaluation.
>
> **ES** — El benchmark clásico, hecho como se debe: ingeniería de características con
> conocimiento de dominio, preprocesamiento **sin fuga de datos** dentro de pipelines con
> validación cruzada y evaluación honesta en conjunto de retención.

![Python](https://img.shields.io/badge/python-3.11-blue) ![scikit-learn](https://img.shields.io/badge/scikit--learn-pipeline-orange) ![tests](https://img.shields.io/badge/tests-5%20passing-brightgreen)

---

## 🇪🇸 Español

### ¿Por qué otro proyecto del Titanic?

Porque la mayoría filtra información. El punto aquí es la disciplina de ingeniería:

- **Toda estadística aprendida vive dentro del pipeline.** Medianas de imputación,
  parámetros de escalado y categorías one-hot se ajustan por fold de validación cruzada
  con `ColumnTransformer` — el fold de prueba nunca influye en el preprocesamiento.
- **Ingeniería de características por fila** (`Title` extraído del nombre y agrupado en 6
  categorías sociales, `FamilySize`, `IsAlone`, `Deck` de la cabina) se aplica antes de la
  partición porque no aprende nada de los datos — y esa distinción está documentada.
- **Las categorías nunca vistas no rompen producción**: `handle_unknown="ignore"`,
  cubierto por un test unitario.

### Resultados (891 pasajeros, 38.4% supervivencia)

Validación cruzada de 5 folds sobre el 80% de entrenamiento:

| Modelo | Accuracy CV | ROC-AUC CV | F1 CV |
|---|---|---|---|
| Regresión logística | 0.819 ± 0.024 | 0.866 | 0.761 |
| Random forest | 0.823 ± 0.030 | 0.871 | 0.750 |
| **Gradient boosting** | 0.822 ± 0.035 | **0.876** | 0.755 |

Retención (20%, jamás tocado durante la selección): **accuracy 0.804, ROC-AUC 0.839,
F1 0.733** — consistente con CV, sin sesgo optimista.

### Estructura

```
proyecto-03-titanic/
├── src/titanic_ml/        # data (features de dominio), pipeline (ColumnTransformer)
├── scripts/run_pipeline.py
├── tests/                 # 5 tests (títulos, familia, NaNs, categorías nuevas)
└── reports/               # metrics.json + matriz de confusión + importancias
```

---

## 🇬🇧 English

### Why another Titanic project?

Because most of them leak data. The point here is engineering discipline:

- **Every learned statistic lives inside the pipeline.** Imputation medians, scaler
  parameters and one-hot categories are fit per CV fold via `ColumnTransformer` —
  the test fold never influences preprocessing.
- **Row-wise feature engineering** (`Title` extracted from names and grouped into 6
  social categories, `FamilySize`, `IsAlone`, `Deck` from cabin codes) is applied before
  the split because it learns nothing from data — and that distinction is documented.
- **Unseen categories don't crash production**: `OneHotEncoder(handle_unknown="ignore")`,
  covered by a unit test.

### Results (891 passengers, 38.4% survival)

5-fold cross-validation on the 80% training partition:

| Model | CV Accuracy | CV ROC-AUC | CV F1 |
|---|---|---|---|
| Logistic regression | 0.819 ± 0.024 | 0.866 | 0.761 |
| Random forest | 0.823 ± 0.030 | 0.871 | 0.750 |
| **Gradient boosting** | 0.822 ± 0.035 | **0.876** | 0.755 |

Holdout (20%, never touched during model selection): **accuracy 0.804, ROC-AUC 0.839,
F1 0.733** — consistent with CV, i.e. no optimistic bias.

### Quickstart

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py   # downloads data on first run
pytest tests/ -q
```
