"""Time-aware training and scoring for fraud detection models."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import INPUT_FEATURES, TARGET, TrainConfig


def time_split(
    tx: pd.DataFrame, cfg: TrainConfig
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split transactions chronologically: train, delay gap, test.

    The *delay* gap between train and test mimics production conditions:
    fraud labels need a verification period before they can be used, so a
    model trained today is evaluated on transactions far enough in the
    future that no label leakage occurs.
    """
    start = tx["TX_TIME_DAYS"].min()
    train_end = start + cfg.train_duration
    test_start = train_end + cfg.delay_duration
    test_end = test_start + cfg.test_duration

    train = tx[(tx["TX_TIME_DAYS"] >= start) & (tx["TX_TIME_DAYS"] < train_end)]
    test = tx[(tx["TX_TIME_DAYS"] >= test_start) & (tx["TX_TIME_DAYS"] < test_end)]
    if train.empty or test.empty:
        raise ValueError(
            f"time_split produced an empty partition (train={len(train)}, "
            f"test={len(test)}): the simulated period of "
            f"{tx['TX_TIME_DAYS'].max() - start + 1} days is shorter than "
            f"train+delay+test = "
            f"{cfg.train_duration + cfg.delay_duration + cfg.test_duration} days"
        )
    return train, test


def make_models(cfg: TrainConfig) -> dict[str, object]:
    """Baseline and tree-based classifiers with class imbalance handling."""
    return {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=cfg.random_state,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            n_jobs=-1,
            class_weight="balanced_subsample",
            random_state=cfg.random_state,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=300,
            learning_rate=0.1,
            class_weight="balanced",
            random_state=cfg.random_state,
        ),
    }


def fit_and_score(
    models: dict[str, object], train: pd.DataFrame, test: pd.DataFrame
) -> pd.DataFrame:
    """Fit every model on the train period and score the test period.

    Returns the test dataframe with one ``SCORE_<model>`` column per model.
    """
    X_train, y_train = train[INPUT_FEATURES], train[TARGET]
    X_test = test[INPUT_FEATURES]
    scored = test.copy()
    for name, model in models.items():
        model.fit(X_train, y_train)
        scored[f"SCORE_{name}"] = model.predict_proba(X_test)[:, 1]
    return scored
