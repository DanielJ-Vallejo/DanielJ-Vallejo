# Contributing / Contribuir

## 🇬🇧 English

This is a personal portfolio, but issues and suggestions are welcome.

1. Fork and create a feature branch from `main`.
2. Keep the project layout described in `architecture.md`.
3. Code style: [ruff](https://docs.astral.sh/ruff/) defaults, type hints on public
   functions, English docstrings.
4. Every change to `src/` needs a test in the project's `tests/` folder.
5. Run locally before pushing:

```bash
pip install ruff pytest
ruff check proyecto-*/src proyecto-*/scripts shared
pytest proyecto-01-fraud-detection/tests proyecto-02-sentiment-analysis/tests \
       proyecto-03-titanic/tests proyecto-04-simulaciones/tests -q
```

6. CI (tests + lint + security audit) must be green before merge.

## 🇪🇸 Español

Este es un portafolio personal, pero los issues y sugerencias son bienvenidos.

1. Haz fork y crea una rama desde `main`.
2. Mantén la estructura de proyecto descrita en `architecture.md`.
3. Estilo de código: [ruff](https://docs.astral.sh/ruff/) por defecto, type hints en
   funciones públicas, docstrings en inglés.
4. Todo cambio en `src/` necesita un test en la carpeta `tests/` del proyecto.
5. Ejecuta lint y tests localmente antes de hacer push (comandos arriba).
6. El CI (tests + lint + auditoría de seguridad) debe estar en verde antes del merge.
