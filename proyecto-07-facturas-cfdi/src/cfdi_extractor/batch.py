"""Batch processing: a folder of CFDIs in, one spreadsheet out."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .cfdi import CfdiError, parse_cfdi


def process_folder(folder: Path | str) -> tuple[pd.DataFrame, list[str]]:
    """Parse every ``*.xml`` in a folder.

    Returns the invoice table and a list of per-file error messages for
    files that could not be parsed (the batch never dies on one bad file).
    """
    folder = Path(folder)
    records, errors = [], []
    for xml_file in sorted(folder.glob("*.xml")):
        try:
            records.append(parse_cfdi(xml_file).to_dict())
        except CfdiError as exc:
            errors.append(str(exc))
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("fecha", ignore_index=True)
    return df, errors


def export(df: pd.DataFrame, out_path: Path | str) -> Path:
    """Write the invoice table to .xlsx or .csv based on the extension."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix == ".xlsx":
        df.to_excel(out_path, index=False)
    elif out_path.suffix == ".csv":
        df.to_csv(out_path, index=False)
    else:
        raise ValueError("output must end in .xlsx or .csv")
    return out_path
