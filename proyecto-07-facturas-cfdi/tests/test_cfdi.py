"""Tests for CFDI parsing, OCR regexes and batch export (no Tesseract needed)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cfdi_extractor.batch import export, process_folder
from cfdi_extractor.cfdi import CfdiError, parse_cfdi
from cfdi_extractor.ocr import extract_fields

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "ejemplo_cfdi40.xml"

CFDI_33 = """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/3"
    Version="3.3" Fecha="2021-01-10T09:00:00" SubTotal="500.00"
    Total="580.00" Moneda="MXN">
  <cfdi:Emisor Rfc="AAA010101AAA" Nombre="EMPRESA DEMO"/>
  <cfdi:Receptor Rfc="BBB020202BB2" Nombre="CLIENTE DEMO"/>
</cfdi:Comprobante>
"""


def test_parse_cfdi_40_sample():
    inv = parse_cfdi(SAMPLE)
    assert inv.version == "4.0"
    assert inv.uuid == "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
    assert inv.rfc_emisor == "EKU9003173C9"
    assert inv.rfc_receptor == "XAXX010101000"
    assert inv.total == 1160.00 and inv.subtotal == 1000.00
    assert inv.moneda == "MXN"


def test_parse_cfdi_33(tmp_path):
    f = tmp_path / "f33.xml"
    f.write_text(CFDI_33, encoding="utf-8")
    inv = parse_cfdi(f)
    assert inv.version == "3.3"
    assert inv.total == 580.00
    assert inv.uuid == ""  # sin timbre en este ejemplo


def test_parse_rejects_non_cfdi(tmp_path):
    f = tmp_path / "otro.xml"
    f.write_text("<factura><total>100</total></factura>", encoding="utf-8")
    with pytest.raises(CfdiError, match="not a CFDI"):
        parse_cfdi(f)


def test_parse_rejects_broken_xml(tmp_path):
    f = tmp_path / "rota.xml"
    f.write_text("<cfdi:Comprobante", encoding="utf-8")
    with pytest.raises(CfdiError, match="not valid XML"):
        parse_cfdi(f)


def test_process_folder_survives_bad_files(tmp_path):
    (tmp_path / "buena.xml").write_text(
        SAMPLE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "mala.xml").write_text("no es xml", encoding="utf-8")
    df, errors = process_folder(tmp_path)
    assert len(df) == 1 and len(errors) == 1
    assert df.loc[0, "total"] == 1160.00


def test_export_xlsx_and_csv(tmp_path):
    df, _ = process_folder(SAMPLE.parent)
    for ext in (".xlsx", ".csv"):
        out = export(df, tmp_path / f"salida{ext}")
        assert out.exists() and out.stat().st_size > 0
    with pytest.raises(ValueError, match="xlsx or .csv"):
        export(df, tmp_path / "salida.txt")


def test_ocr_regexes_on_invoice_text():
    text = """
    FACTURA   Fecha: 2026-05-15
    Emisor: EKU9003173C9   Receptor: XAXX 010101 000
    Folio fiscal: aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    Subtotal: $1,000.00
    TOTAL A PAGAR: $1,160.00
    """
    fields = extract_fields(text)
    assert fields["rfc_emisor"] == "EKU9003173C9"
    assert fields["rfc_receptor"] == "XAXX010101000"
    assert fields["total"] == 1160.00
    assert fields["fecha"] == "2026-05-15"
    assert fields["uuid"] == "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"


def test_ocr_regexes_handle_missing_fields():
    fields = extract_fields("texto sin datos fiscales")
    assert fields["total"] is None and fields["rfc_emisor"] == ""
