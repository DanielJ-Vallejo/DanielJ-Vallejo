"""Best-effort field extraction from scanned invoices (images / text).

OCR needs the free Tesseract binary + ``pytesseract``; both are optional.
The regex layer also works on text extracted by any other means, so it is
unit-testable without Tesseract installed.
"""

from __future__ import annotations

import re
from pathlib import Path

# RFC: 3-4 letters (incl. Ñ/&), 6 digits of date, 3-char homoclave
RFC_RE = re.compile(r"\b([A-ZÑ&]{3,4}\s?-?\d{6}\s?-?[A-Z\d]{2,3})\b")
# (?<!sub) keeps "Subtotal" from matching; invoices repeat the figure, so
# extract_fields() takes the last occurrence (grand total comes last).
TOTAL_RE = re.compile(
    r"(?<!sub)(?:total(?:\s+a\s+pagar)?)\s*[:$]*\s*\$?\s*([\d,]+\.\d{2})",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b"
)
UUID_RE = re.compile(
    r"\b([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\b"
)


def extract_fields(text: str) -> dict:
    """Pull RFCs, total, date and UUID out of free-form invoice text."""
    rfcs = [m.replace(" ", "").replace("-", "") for m in RFC_RE.findall(text.upper())]
    totals = TOTAL_RE.findall(text)
    date_match = DATE_RE.search(text)
    uuid_match = UUID_RE.search(text)
    return {
        "rfc_emisor": rfcs[0] if rfcs else "",
        "rfc_receptor": rfcs[1] if len(rfcs) > 1 else "",
        "total": float(totals[-1].replace(",", "")) if totals else None,
        "fecha": date_match.group(1) if date_match else "",
        "uuid": uuid_match.group(1).upper() if uuid_match else "",
    }


def ocr_image(path: Path | str) -> str:
    """OCR an invoice image to text. Requires Tesseract (free) installed."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "OCR support needs: pip install pytesseract pillow "
            "+ the Tesseract binary (https://github.com/tesseract-ocr/tesseract)"
        ) from exc
    return pytesseract.image_to_string(Image.open(path), lang="spa+eng")


def extract_from_image(path: Path | str) -> dict:
    """OCR + regex extraction for one scanned invoice."""
    fields = extract_fields(ocr_image(path))
    fields["archivo"] = Path(path).name
    return fields
