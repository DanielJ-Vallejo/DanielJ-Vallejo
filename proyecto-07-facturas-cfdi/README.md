# 🧾 CFDI Invoice Extractor / Extractor de Facturas CFDI

> **EN** — Turn a folder of Mexican electronic invoices (CFDI 3.3/4.0 XML) into a clean
> Excel in seconds: UUID, RFCs, dates, totals. Stdlib XML parsing (exact, not OCR
> guessing), drag-and-drop web UI with Streamlit, optional Tesseract OCR for scanned
> invoices. Fully local and offline — your fiscal data never leaves your machine.
>
> **ES** — Convierte una carpeta de facturas electrónicas mexicanas (CFDI 3.3/4.0 XML)
> en un Excel limpio en segundos: UUID, RFCs, fechas, totales. Parsing exacto del XML
> con la librería estándar (no adivina con OCR), interfaz web de arrastrar y soltar con
> Streamlit y OCR opcional con Tesseract para facturas escaneadas. Totalmente local
> y offline — tus datos fiscales nunca salen de tu máquina.

![Python](https://img.shields.io/badge/python-3.11-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B) ![tests](https://img.shields.io/badge/tests-8%20passing-brightgreen)

---

## 🇪🇸 Español

### El problema

Contadores y pequeños negocios capturan facturas **a mano** en Excel cada mes. El XML
del CFDI ya contiene todos los datos de forma legal y exacta — solo hay que extraerlos.

### Uso

**Interfaz web** (arrastrar y soltar):

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

**Por código** (carpetas completas):

```python
from cfdi_extractor.batch import process_folder, export

df, errores = process_folder("mis_facturas/")   # nunca muere por un XML malo
export(df, "facturas_mayo.xlsx")
```

### Qué extrae

| Campo | Fuente en el XML |
|---|---|
| UUID (folio fiscal) | `TimbreFiscalDigital@UUID` |
| RFC y nombre de emisor/receptor | `Emisor@Rfc`, `Receptor@Rfc`, ... |
| Fecha, SubTotal, Total, Moneda | atributos de `Comprobante` |

Soporta **CFDI 3.3 y 4.0**. Para facturas escaneadas (imagen), `ocr.py` añade
extracción por OCR + expresiones regulares (RFC, total, fecha, UUID) usando el
binario gratuito de Tesseract — completamente opcional.

### Privacidad

Todo corre local. La app de Streamlit procesa en memoria y no persiste archivos.
El XML de `data/` es **sintético** (RFC de pruebas del SAT).

---

## 🇬🇧 English

Accountants and small businesses re-type invoice data into Excel every month, even
though the CFDI XML *is* the legal invoice and already contains every field. This tool
parses CFDI 3.3/4.0 with `xml.etree` (exact — no OCR guessing), batch-processes folders
without dying on malformed files, and exports to Excel/CSV. A Streamlit drag-and-drop
UI makes it usable by non-programmers; optional Tesseract OCR covers scanned invoices.

```
proyecto-07-facturas-cfdi/
├── src/cfdi_extractor/   # cfdi (XML parsing), ocr (regex layer), batch (folder→Excel)
├── app/streamlit_app.py  # drag & drop web UI
├── data/ejemplo_cfdi40.xml  # synthetic sample (SAT test RFCs)
└── tests/                # 8 tests: both CFDI versions, bad files, OCR regexes
```
