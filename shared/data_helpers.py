"""Reusable data preprocessing helpers shared across portfolio projects.

Cleaned-up evolution of the preprocessing utilities from the UNAM data
preprocessing course: each function does one thing, operates on copies and
is safe for mixed-dtype dataframes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_csv(filepath: str | Path, **kwargs) -> pd.DataFrame:
    """Read a CSV with a clear error if the file is missing."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Dataset not found: {filepath}")
    return pd.read_csv(filepath, **kwargs)


def fill_missing_numeric(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame:
    """Impute numeric columns with their mean or median; leave others intact."""
    if strategy not in {"mean", "median"}:
        raise ValueError("strategy must be 'mean' or 'median'")
    df = df.copy()
    numeric = df.select_dtypes(include=np.number).columns
    fill = df[numeric].mean() if strategy == "mean" else df[numeric].median()
    df[numeric] = df[numeric].fillna(fill)
    return df


def remove_outliers_zscore(
    df: pd.DataFrame, columns: list[str] | None = None, threshold: float = 3.0
) -> pd.DataFrame:
    """Drop rows where any selected numeric column exceeds ``threshold`` z-scores.

    Note: this learns statistics from the data — in a modelling context apply
    it to the training partition only.
    """
    df = df.copy()
    columns = columns or list(df.select_dtypes(include=np.number).columns)
    sub = df[columns]
    std = sub.std(ddof=0).replace(0, np.nan)
    z = ((sub - sub.mean()) / std).abs()
    mask = (z < threshold).fillna(True).all(axis=1)
    return df[mask].reset_index(drop=True)


def standardize(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Z-score scale the selected numeric columns (population std)."""
    df = df.copy()
    columns = columns or list(df.select_dtypes(include=np.number).columns)
    std = df[columns].std(ddof=0).replace(0, 1.0)
    df[columns] = (df[columns] - df[columns].mean()) / std
    return df


def one_hot(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """One-hot encode the given categorical columns (ints, not bools)."""
    return pd.get_dummies(df, columns=columns, dtype=int)


def summarize_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Per-column missing-value count and percentage, sorted descending."""
    n = df.isna().sum()
    out = pd.DataFrame({"n_missing": n, "pct_missing": (100 * n / len(df)).round(2)})
    return out[out["n_missing"] > 0].sort_values("n_missing", ascending=False)
