"""Loading and domain feature engineering for the Titanic dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_URL = (
    "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
)

TITLE_GROUPS = {
    "Mr": "Mr",
    "Miss": "Miss",
    "Mrs": "Mrs",
    "Master": "Master",
    "Dr": "Officer",
    "Rev": "Officer",
    "Col": "Officer",
    "Major": "Officer",
    "Capt": "Officer",
    "Mlle": "Miss",
    "Ms": "Miss",
    "Mme": "Mrs",
    "Lady": "Royalty",
    "Sir": "Royalty",
    "the Countess": "Royalty",
    "Countess": "Royalty",
    "Don": "Royalty",
    "Dona": "Royalty",
    "Jonkheer": "Royalty",
}


def load_titanic(path: Path | str) -> pd.DataFrame:
    """Load the Kaggle Titanic training CSV, downloading it if missing."""
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.read_csv(DATA_URL).to_csv(path, index=False)
    df = pd.read_csv(path)
    expected = {"Survived", "Pclass", "Name", "Sex", "Age", "SibSp", "Parch", "Fare"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing expected columns {sorted(missing)}")
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add domain features derived from name, family and cabin columns.

    These transformations are row-wise (no statistics learned from data),
    so applying them before the train/test split cannot leak information.
    """
    df = df.copy()
    title = df["Name"].str.extract(r",\s*([^.]+)\.", expand=False).str.strip()
    df["Title"] = title.map(TITLE_GROUPS).fillna("Other")
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df["Deck"] = df["Cabin"].str[0].fillna("U") if "Cabin" in df.columns else "U"
    return df


NUMERIC_FEATURES = ["Age", "Fare", "SibSp", "Parch", "FamilySize"]
CATEGORICAL_FEATURES = ["Pclass", "Sex", "Embarked", "Title", "Deck", "IsAlone"]
TARGET = "Survived"
