"""Model pipelines: preprocessing learned inside cross-validation folds."""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data import CATEGORICAL_FEATURES, NUMERIC_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """Impute + scale numerics, impute + one-hot encode categoricals.

    Lives inside the model pipeline so every statistic (medians, modes,
    scaler parameters, category list) is learned only from training folds.
    """
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )


def make_models(random_state: int = 42) -> dict[str, Pipeline]:
    """Candidate models, all sharing the same preprocessing."""
    return {
        "logistic_regression": Pipeline(
            [
                ("prep", build_preprocessor()),
                ("clf", LogisticRegression(max_iter=2000, random_state=random_state)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("prep", build_preprocessor()),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=300,
                        max_depth=8,
                        min_samples_leaf=2,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "gradient_boosting": Pipeline(
            [
                ("prep", build_preprocessor()),
                (
                    "clf",
                    GradientBoostingClassifier(
                        n_estimators=300,
                        learning_rate=0.05,
                        max_depth=3,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }
