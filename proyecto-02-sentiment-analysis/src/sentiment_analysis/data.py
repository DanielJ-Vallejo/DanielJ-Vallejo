"""Data loading and text preparation for the MeIA 2025 review dataset.

Each review comes with metadata (region, town, service type). Prepending it
as pseudo-tokens lets the transformer condition on context — reviews about
hotels and restaurants express polarity differently.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["Review", "Region", "Town", "Type"]


def enrich_text(row: pd.Series) -> str:
    """Prepend metadata pseudo-tokens to the raw review text."""
    return (
        f"[REGION: {row['Region']}] [TOWN: {row['Town']}] "
        f"[SERVICE: {row['Type']}] {row['Review']}"
    )


def load_reviews(path: Path | str, with_labels: bool = True) -> pd.DataFrame:
    """Load a MeIA xlsx file and add the enriched ``text`` column.

    With ``with_labels=True`` a 0-based ``label`` column is derived from the
    1-5 ``Polarity`` rating.
    """
    df = pd.read_excel(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path}: missing expected columns {missing}")
    df["text"] = df.apply(enrich_text, axis=1)
    if with_labels:
        if "Polarity" not in df.columns:
            raise ValueError(f"{path}: no 'Polarity' column in labelled data")
        df["label"] = df["Polarity"].astype(int) - 1
        if not df["label"].between(0, 4).all():
            raise ValueError("Polarity ratings must be in 1..5")
    return df


def oversample_minority(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    """Random-oversample the smallest class up to the second-smallest size.

    Lightweight replacement for imblearn's ``RandomOverSampler`` with
    ``sampling_strategy='minority'`` so the package is not a hard dependency.
    """
    counts = df["label"].value_counts()
    minority = counts.idxmin()
    target = int(counts.drop(index=minority).min())
    extra = target - int(counts[minority])
    if extra <= 0:
        return df.reset_index(drop=True)
    sampled = df[df["label"] == minority].sample(
        n=extra, replace=True, random_state=random_state
    )
    return (
        pd.concat([df, sampled], ignore_index=True)
        .sample(frac=1.0, random_state=random_state)
        .reset_index(drop=True)
    )


def format_predictions(predictions: list[int], prefix: str = "MeIA") -> str:
    """Serialize predictions in the official run-file format ``MeIA <i> <label>``."""
    return "\n".join(f"{prefix} {i} {p}" for i, p in enumerate(predictions)) + "\n"
