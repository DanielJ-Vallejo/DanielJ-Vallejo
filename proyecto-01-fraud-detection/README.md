# 💳 Credit Card Fraud Detection / Detección de Fraude con Tarjetas

> **EN** — End-to-end machine learning system for transaction fraud detection: realistic
> data simulation, leakage-free temporal validation and the operational metrics actually
> used by fraud teams in industry.
>
> **ES** — Sistema de machine learning de extremo a extremo para detección de fraude
> transaccional: simulación realista de datos, validación temporal sin fuga de
> información y las métricas operativas que usan los equipos antifraude en la industria.

![Python](https://img.shields.io/badge/python-3.11-blue) ![scikit-learn](https://img.shields.io/badge/scikit--learn-pipeline-orange) ![tests](https://img.shields.io/badge/tests-11%20passing-brightgreen)

---

## 🇪🇸 Español

### Problema

El fraude con tarjetas es un problema de clasificación **extremadamente desbalanceado**
(~1–2% de positivos aquí, a menudo <0.5% en producción) donde las etiquetas llegan **con
días de retraso** (el cliente reclama un cargo una semana después) y donde la restricción
de negocio es un **presupuesto de alertas**: el equipo de investigación solo puede revisar
*k* tarjetas por día. Un modelo que optimiza accuracy simple es inútil — este proyecto
optimiza lo que los equipos antifraude miden de verdad.

### Qué hace este proyecto

1. **Simulador de transacciones** (`src/fraud_detection/simulation.py`) — genera una red de
   clientes y terminales de pago con comportamiento de gasto realista e inyecta tres
   escenarios de fraude: anomalías de monto, terminales comprometidas y filtración de
   datos de tarjeta (fraude sin tarjeta presente). Metodología inspirada en el *Fraud
   Detection Handbook* de la ULB (ver `references/`), reimplementada desde cero.
2. **Ingeniería de características** (`features.py`) — agregados de ventana deslizante tipo
   RFM por cliente (número de transacciones / gasto promedio en 1, 7 y 30 días), score de
   riesgo por terminal **con retraso** (la tasa de fraude observada se desplaza 7 días para
   que ninguna información futura se filtre a las features) y variables de calendario.
3. **Validación temporal** (`modeling.py`) — partición cronológica entrenamiento / **brecha
   de retraso** / prueba, reproduciendo la latencia de verificación de etiquetas.
4. **Evaluación específica de fraude** (`evaluation.py`) — ROC-AUC, Average Precision y
   **Card Precision@k**: de las *k* tarjetas alertadas por día, cuántas estaban
   realmente comprometidas.

### Resultados (período de prueba — 216,878 tx, 1.07% fraude)

| Modelo | ROC-AUC | Average Precision | Card Precision@20 |
|---|---|---|---|
| Regresión logística (línea base) | 0.898 | 0.455 | 0.442 |
| Random forest | 0.851 | 0.437 | 0.390 |
| **Hist. gradient boosting** | **0.901** | **0.607** | **0.517** |

Con 1% de desbalance, el ROC-AUC parece similar entre modelos — el **Average
Precision** revela la brecha real. Las figuras y métricas se regeneran en cada
ejecución dentro de `reports/`.

### Estructura

```
proyecto-01-fraud-detection/
├── src/fraud_detection/   # paquete: simulation, features, modeling, evaluation, plots
├── scripts/run_pipeline.py
├── tests/                  # 11 tests unitarios (reproducibilidad, fuga de datos, métricas)
├── reports/                # metrics.json + figuras generadas
├── models/                 # modelos entrenados (.joblib)
└── references/             # handbook de la ULB (material de terceros, ver su README)
```

### Referencia

Le Borgne, Y-A., Siblini, W., Lebichot, B., Bontempi, G.
*Reproducible Machine Learning for Credit Card Fraud Detection — Practical Handbook*,
Université Libre de Bruxelles, 2022.

---

## 🇬🇧 English

### Problem

Card fraud is an **extremely imbalanced** classification problem (~1–2% positives here,
often <0.5% in production) where labels arrive **days late** (a customer disputes a charge
a week after it happens) and where the business constraint is an **alert budget**: an
investigation team can only check *k* cards per day. A model that optimizes plain accuracy
is useless — this project optimizes what fraud teams actually measure.

### What this project does

1. **Transaction simulator** (`src/fraud_detection/simulation.py`) — generates a network of
   customers and payment terminals with realistic spending behaviour, then injects three
   fraud scenarios: amount anomalies, compromised terminals and leaked card details
   (card-not-present fraud). Methodology inspired by the ULB *Fraud Detection Handbook*
   (see `references/`), re-implemented from scratch.
2. **Feature engineering** (`features.py`) — RFM-style sliding-window aggregates per
   customer (transaction count / average spent over 1, 7, 30 days), **delayed** terminal
   risk scores (fraud rate observed at the terminal, shifted by the 7-day label delay so
   no future information leaks into the features), and calendar features.
3. **Time-aware validation** (`modeling.py`) — chronological train / **delay gap** / test
   split. The gap reproduces the label verification latency of production systems.
4. **Fraud-specific evaluation** (`evaluation.py`) — ROC-AUC, Average Precision and
   **Card Precision@k**: of the *k* cards flagged per day, how many were truly compromised.

### Results (test period, simulated dataset — 216,878 tx, 1.07% fraud)

| Model | ROC-AUC | Average Precision | Card Precision@20 |
|---|---|---|---|
| Logistic regression (baseline) | 0.898 | 0.455 | 0.442 |
| Random forest | 0.851 | 0.437 | 0.390 |
| **Hist. gradient boosting** | **0.901** | **0.607** | **0.517** |

Under 1% class imbalance, ROC-AUC looks deceptively similar across models —
**Average Precision** reveals the real gap: gradient boosting finds twice as much
fraud as chance-adjusted baselines at every recall level. Figures and the full
metric dump are regenerated on every run in `reports/`.

### Quickstart

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py          # full run (~2-4 min)
python scripts/run_pipeline.py --quick  # smoke test
pytest tests/ -q                        # 11 unit tests
```
