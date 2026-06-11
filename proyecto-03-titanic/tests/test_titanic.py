"""Tests for the Titanic feature engineering and pipeline construction."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from titanic_ml.data import engineer_features
from titanic_ml.pipeline import make_models


def _sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Survived": [1, 0, 1, 0],
            "Pclass": [1, 3, 2, 3],
            "Name": [
                "Cumings, Mrs. John Bradley (Florence Briggs Thayer)",
                "Braund, Mr. Owen Harris",
                "Heikkinen, Miss. Laina",
                "Palsson, Master. Gosta Leonard",
            ],
            "Sex": ["female", "male", "female", "male"],
            "Age": [38.0, 22.0, np.nan, 2.0],
            "SibSp": [1, 1, 0, 3],
            "Parch": [0, 0, 0, 1],
            "Fare": [71.28, 7.25, 7.92, 21.07],
            "Cabin": ["C85", None, None, None],
            "Embarked": ["C", "S", "S", "S"],
        }
    )


def test_title_extraction_and_grouping():
    df = engineer_features(_sample())
    assert df["Title"].tolist() == ["Mrs", "Mr", "Miss", "Master"]


def test_family_features():
    df = engineer_features(_sample())
    assert df["FamilySize"].tolist() == [2, 2, 1, 5]
    assert df["IsAlone"].tolist() == [0, 0, 1, 0]


def test_deck_from_cabin_with_unknowns():
    df = engineer_features(_sample())
    assert df["Deck"].tolist() == ["C", "U", "U", "U"]


def test_pipelines_fit_and_predict_with_missing_values():
    df = engineer_features(_sample())
    X, y = df.drop(columns=["Survived"]), df["Survived"]
    for name, model in make_models().items():
        model.fit(X, y)
        proba = model.predict_proba(X)[:, 1]
        assert proba.shape == (4,), name
        assert np.isfinite(proba).all(), name


def test_unseen_categories_do_not_crash():
    df = engineer_features(_sample())
    X, y = df.drop(columns=["Survived"]), df["Survived"]
    model = make_models()["logistic_regression"].fit(X, y)
    X_new = X.copy()
    X_new.loc[:, "Embarked"] = "Z"  # category never seen in training
    assert model.predict(X_new).shape == (4,)
