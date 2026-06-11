"""CFDI 3.3 / 4.0 XML parsing with the standard library only.

A CFDI (Comprobante Fiscal Digital por Internet) is the official Mexican
electronic invoice issued by the SAT. The XML is the legal document — parsing
it directly is exact, unlike OCR on the PDF representation.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path

NAMESPACES = {
    "4.0": {"cfdi": "http://www.sat.gob.mx/cfd/4"},
    "3.3": {"cfdi": "http://www.sat.gob.mx/cfd/3"},
}
TFD_NS = {"tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"}


@dataclass
class Invoice:
    """Flat record of the fields accountants ask for."""

    uuid: str
    version: str
    fecha: str
    rfc_emisor: str
    nombre_emisor: str
    rfc_receptor: str
    nombre_receptor: str
    subtotal: float
    total: float
    moneda: str
    archivo: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class CfdiError(ValueError):
    """Raised when a file is not a parseable CFDI."""


def parse_cfdi(path: Path | str) -> Invoice:
    """Parse one CFDI XML file (versions 3.3 and 4.0)."""
    path = Path(path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise CfdiError(f"{path.name}: not valid XML ({exc})") from exc

    version = root.get("Version") or root.get("version") or ""
    ns = NAMESPACES.get(version)
    if ns is None or not root.tag.endswith("Comprobante"):
        raise CfdiError(
            f"{path.name}: not a CFDI 3.3/4.0 Comprobante (version={version!r})"
        )

    emisor = root.find("cfdi:Emisor", ns)
    receptor = root.find("cfdi:Receptor", ns)
    if emisor is None or receptor is None:
        raise CfdiError(f"{path.name}: missing Emisor/Receptor nodes")

    timbre = root.find(".//tfd:TimbreFiscalDigital", TFD_NS)
    uuid = timbre.get("UUID", "") if timbre is not None else ""

    try:
        subtotal = float(root.get("SubTotal", "0"))
        total = float(root.get("Total", "0"))
    except ValueError as exc:
        raise CfdiError(f"{path.name}: non-numeric SubTotal/Total") from exc

    return Invoice(
        uuid=uuid,
        version=version,
        fecha=root.get("Fecha", ""),
        rfc_emisor=emisor.get("Rfc", ""),
        nombre_emisor=emisor.get("Nombre", ""),
        rfc_receptor=receptor.get("Rfc", ""),
        nombre_receptor=receptor.get("Nombre", ""),
        subtotal=subtotal,
        total=total,
        moneda=root.get("Moneda", "MXN"),
        archivo=path.name,
    )
