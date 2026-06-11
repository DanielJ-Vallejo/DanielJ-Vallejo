"""Tests for data preparation (no transformers/torch required)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sentiment_analysis.data import (
    enrich_text,
    format_predictions,
    load_reviews,
    oversample_minority,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Review": ["Excelente lugar", "Muy malo", "Regular"],
            "Region": ["CDMX", "Yucatán", "Jalisco"],
            "Town": ["Coyoacán", "Mérida", "Tequila"],
            "Type": ["Hotel", "Restaurante", "Atracción"],
            "Polarity": [5, 1, 3],
        }
    )


def test_enrich_text_prepends_metadata():
    row = _sample_df().iloc[0]
    text = enrich_text(row)
    assert text.startswith("[REGION: CDMX] [TOWN: Coyoacán] [SERVICE: Hotel]")
    assert text.endswith("Excelente lugar")


def test_load_reviews_builds_labels(tmp_path):
    f = tmp_path / "train.xlsx"
    _sample_df().to_excel(f, index=False)
    df = load_reviews(f, with_labels=True)
    assert df["label"].tolist() == [4, 0, 2]
    assert "text" in df.columns


def test_load_reviews_rejects_missing_columns(tmp_path):
    f = tmp_path / "bad.xlsx"
    _sample_df().drop(columns=["Region"]).to_excel(f, index=False)
    with pytest.raises(ValueError, match="missing expected columns"):
        load_reviews(f, with_labels=True)


def test_load_reviews_rejects_out_of_range_polarity(tmp_path):
    df = _sample_df()
    df.loc[0, "Polarity"] = 7
    f = tmp_path / "bad.xlsx"
    df.to_excel(f, index=False)
    with pytest.raises(ValueError, match="1..5"):
        load_reviews(f, with_labels=True)


def test_oversample_minority_balances_smallest_class():
    df = pd.DataFrame(
        {"text": ["a"] * 10 + ["b"] * 5 + ["c"] * 2, "label": [0] * 10 + [1] * 5 + [2] * 2}
    )
    out = oversample_minority(df, random_state=0)
    counts = out["label"].value_counts()
    assert counts[2] == 5  # minority raised to second-smallest class size
    assert counts[0] == 10  # majority untouched


def test_format_predictions_official_format():
    text = format_predictions([3, 5, 1])
    assert text == "MeIA 0 3\nMeIA 1 5\nMeIA 2 1\n"
