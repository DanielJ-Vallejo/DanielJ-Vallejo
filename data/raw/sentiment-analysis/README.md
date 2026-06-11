# MeIA 2025 dataset

**EN** — `MeIA_2025_train.xlsx` and `MeIA_2025_test_wo_labels.xlsx` belong to the MeIA
2025 challenge organizers (Macroentrenamiento en Inteligencia Artificial, UNAM/RedMacro)
and are **not redistributed** in this repository. Participants can place their local
copies in this folder; the pipeline in `proyecto-02-sentiment-analysis` will pick them
up automatically.

**ES** — `MeIA_2025_train.xlsx` y `MeIA_2025_test_wo_labels.xlsx` pertenecen a los
organizadores del reto MeIA 2025 (Macroentrenamiento en Inteligencia Artificial,
UNAM/RedMacro) y **no se redistribuyen** en este repositorio. Los participantes pueden
colocar sus copias locales en esta carpeta; el pipeline de
`proyecto-02-sentiment-analysis` las detecta automáticamente.

Expected schema / Esquema esperado:

| Column | Type | Description |
|---|---|---|
| `Review` | str | Review text (Spanish) |
| `Region` | str | Mexican region |
| `Town` | str | Town / magical village |
| `Type` | str | Hotel · Restaurant · Attractive |
| `Polarity` | int 1-5 | Rating (train only) |
