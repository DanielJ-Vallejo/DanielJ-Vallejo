"""Streamlit UI: drag CFDI XMLs in, download a clean spreadsheet.

Run locally (free) or deploy on Streamlit Community Cloud (free):

    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cfdi_extractor.cfdi import CfdiError, parse_cfdi  # noqa: E402

st.set_page_config(page_title="Extractor de Facturas CFDI", page_icon="🧾")
st.title("🧾 Extractor de Facturas CFDI")
st.caption(
    "Sube tus facturas XML (CFDI 3.3 / 4.0) y descarga un Excel con "
    "UUID, RFC, fechas y totales. Los archivos se procesan en memoria, "
    "no se guardan en ningún servidor."
)

uploads = st.file_uploader(
    "Arrastra aquí tus XML", type=["xml"], accept_multiple_files=True
)

if uploads:
    records, errors = [], []
    for up in uploads:
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            tmp.write(up.getvalue())
            tmp_path = Path(tmp.name)
        try:
            invoice = parse_cfdi(tmp_path)
            invoice.archivo = up.name
            records.append(invoice.to_dict())
        except CfdiError as exc:
            errors.append(f"{up.name}: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)

    if errors:
        st.warning("Archivos con problemas:\n\n- " + "\n- ".join(errors))

    if records:
        df = pd.DataFrame(records).sort_values("fecha", ignore_index=True)
        st.success(f"{len(df)} facturas procesadas ✅")
        st.dataframe(df, width="stretch")

        col1, col2 = st.columns(2)
        col1.metric("Total facturado", f"${df['total'].sum():,.2f}")
        col2.metric("Emisores distintos", df["rfc_emisor"].nunique())

        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            "⬇️ Descargar Excel",
            data=buffer.getvalue(),
            file_name="facturas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
            "⬇️ Descargar CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="facturas.csv",
            mime="text/csv",
        )
else:
    st.info("👆 Sube uno o varios XML para empezar. Prueba con data/ejemplo_cfdi40.xml")
