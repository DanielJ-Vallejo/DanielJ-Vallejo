# Architecture / Arquitectura

## 🇬🇧 Monorepo layout

This repository is a **data science portfolio monorepo**. Every project is
self-contained and follows the same industry-standard layout:

```
proyecto-XX-name/
├── README.md            # bilingual: problem, approach, results, how to run
├── requirements.txt     # minimal pinned dependencies
├── environment.yml      # conda equivalent
├── src/<package>/       # importable python package (no notebooks-as-source)
├── scripts/             # CLI entry points (run_pipeline.py, train.py, ...)
├── notebooks/           # exploration & reports — never the source of truth
├── tests/               # pytest suites run in CI
├── reports/             # generated metrics.json + figures (reproducible)
└── models/              # trained artifacts (.joblib), git-ignored when heavy
```

Shared infrastructure:

- `shared/` — preprocessing and IO helpers reused across projects.
- `data/raw/`, `data/processed/` — central data lake split by project;
  non-redistributable datasets are git-ignored and documented instead.
- `website/` — static portfolio site deployed to GitHub Pages by
  `.github/workflows/deploy-pages.yml`.
- `.github/workflows/ci.yml` — per-project test matrix + ruff lint +
  `pip-audit`/`bandit` security jobs.

### Design rules

1. **Notebooks demonstrate, packages implement.** All logic lives in `src/` with tests;
   notebooks import it or document experiments.
2. **Reproducibility**: every stochastic process takes an explicit seed; pipelines
   regenerate metrics and figures from scratch on each run.
3. **No data leakage**: preprocessing statistics are learned inside CV folds
   (titanic) or restricted to past windows with label delay (fraud detection).

## 🇪🇸 Estructura del monorepo

Este repositorio es un **monorepo de portafolio de ciencia de datos**. Cada proyecto es
autocontenido y sigue la misma estructura estándar de la industria (ver arriba).

Reglas de diseño:

1. **Los notebooks demuestran, los paquetes implementan.** Toda la lógica vive en `src/`
   con tests; los notebooks la importan o documentan experimentos.
2. **Reproducibilidad**: todo proceso estocástico recibe semilla explícita; los
   pipelines regeneran métricas y figuras desde cero en cada ejecución.
3. **Sin fuga de datos**: las estadísticas de preprocesamiento se aprenden dentro de los
   folds de validación cruzada (titanic) o se restringen a ventanas pasadas con retraso
   de etiquetas (detección de fraude).
