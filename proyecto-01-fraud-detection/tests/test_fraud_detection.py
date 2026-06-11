"""Unit tests for the fraud detection package."""

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fraud_detection.config import FeatureConfig, SimulationConfig, TrainConfig
from fraud_detection.evaluation import card_precision_top_k
from fraud_detection.features import add_datetime_features, build_features
from fraud_detection.modeling import time_split
from fraud_detection.simulation import simulate_dataset

# Compromise rates raised so all three fraud scenarios appear even in a
# small 30-day network (production defaults would yield ~0 events here).
QUICK_CFG = SimulationConfig(
    n_customers=80,
    n_terminals=30,
    n_days=30,
    amount_fraud_threshold=120.0,
    terminal_compromise_rate=0.01,
    customer_compromise_rate=0.01,
)


@pytest.fixture(scope="module")
def dataset() -> pd.DataFrame:
    return simulate_dataset(QUICK_CFG)


def test_simulation_is_reproducible(dataset):
    again = simulate_dataset(QUICK_CFG)
    pd.testing.assert_frame_equal(dataset, again)


def test_simulation_has_both_classes_and_scenarios(dataset):
    assert set(dataset["TX_FRAUD"].unique()) == {0, 1}
    assert dataset["TX_FRAUD"].mean() < 0.25  # fraud is the minority class
    assert {1, 2, 3} <= set(dataset["TX_FRAUD_SCENARIO"].unique())


def test_amounts_and_times_are_valid(dataset):
    assert (dataset["TX_AMOUNT"] > 0).all()
    assert dataset["TX_TIME_DAYS"].between(0, QUICK_CFG.n_days - 1).all()
    assert dataset["TX_TIME_SECONDS"].is_monotonic_increasing


def test_datetime_features():
    tx = pd.DataFrame(
        {
            # Sat 2025-04-05 (weekend) at 03:00, Mon 2025-04-07 at 12:00
            "TX_DATETIME": pd.to_datetime(["2025-04-05 03:00", "2025-04-07 12:00"])
        }
    )
    out = add_datetime_features(tx)
    assert out["TX_DURING_WEEKEND"].tolist() == [1, 0]
    assert out["TX_DURING_NIGHT"].tolist() == [1, 0]


def test_customer_window_counts_include_current_tx(dataset):
    feats = build_features(dataset, FeatureConfig())
    # every transaction counts itself, so windows are >= 1
    assert (feats["CUSTOMER_ID_NB_TX_1DAY_WINDOW"] >= 1).all()
    # larger windows can only contain more (or equal) transactions
    assert (
        feats["CUSTOMER_ID_NB_TX_30DAY_WINDOW"]
        >= feats["CUSTOMER_ID_NB_TX_7DAY_WINDOW"]
    ).all()
    assert feats[
        [c for c in feats.columns if "WINDOW" in c]
    ].notna().all().all()


def test_terminal_risk_is_a_rate(dataset):
    feats = build_features(dataset, FeatureConfig())
    for w in (1, 7, 30):
        risk = feats[f"TERMINAL_ID_RISK_{w}DAY_WINDOW"]
        assert risk.between(0, 1).all()


def test_time_split_leaves_delay_gap(dataset):
    cfg = TrainConfig(train_duration=15, delay_duration=5, test_duration=10)
    train, test = time_split(dataset, cfg)
    assert train["TX_TIME_DAYS"].max() < 15
    assert test["TX_TIME_DAYS"].min() >= 20
    assert len(train) > 0 and len(test) > 0


def test_card_precision_top_k_perfect_score():
    scored = pd.DataFrame(
        {
            "TX_TIME_DAYS": [0] * 4,
            "CUSTOMER_ID": [1, 2, 3, 4],
            "TX_FRAUD": [1, 1, 0, 0],
            "SCORE_m": [0.9, 0.8, 0.2, 0.1],
        }
    )
    assert card_precision_top_k(scored, "SCORE_m", k=2) == 1.0
    # bottom-2 ranking would be 0
    scored["SCORE_m"] = [0.1, 0.2, 0.8, 0.9]
    assert card_precision_top_k(scored, "SCORE_m", k=2) == 0.0


def test_card_precision_handles_k_larger_than_cards():
    scored = pd.DataFrame(
        {
            "TX_TIME_DAYS": [0, 0],
            "CUSTOMER_ID": [1, 2],
            "TX_FRAUD": [1, 0],
            "SCORE_m": [0.9, 0.1],
        }
    )
    assert 0.0 <= card_precision_top_k(scored, "SCORE_m", k=10) <= 1.0


def test_fraud_scenario_amounts_are_inflated(dataset):
    s3 = dataset[dataset["TX_FRAUD_SCENARIO"] == 3]
    legit = dataset[dataset["TX_FRAUD"] == 0]
    if len(s3) > 0:
        assert s3["TX_AMOUNT"].mean() > legit["TX_AMOUNT"].mean()


def test_no_nan_anywhere_in_model_inputs(dataset):
    from fraud_detection.config import INPUT_FEATURES

    feats = build_features(dataset, FeatureConfig())
    assert not feats[INPUT_FEATURES].isna().any().any()
    assert np.isfinite(feats[INPUT_FEATURES].to_numpy(dtype=float)).all()
