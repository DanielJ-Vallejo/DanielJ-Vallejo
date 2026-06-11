"""End-to-end fraud detection pipeline.

Usage::

    python scripts/run_pipeline.py [--quick]

Simulates transactions, engineers features, trains three classifiers with a
time-aware split, evaluates them with fraud-specific metrics and writes
figures, metrics and the fitted models to ``reports/`` and ``models/``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fraud_detection.config import INPUT_FEATURES, PipelineConfig  # noqa: E402
from fraud_detection.evaluation import evaluate_models  # noqa: E402
from fraud_detection.features import build_features  # noqa: E402
from fraud_detection.modeling import fit_and_score, make_models, time_split  # noqa: E402
from fraud_detection.plots import (  # noqa: E402
    plot_amount_distribution,
    plot_class_balance,
    plot_curves,
    plot_daily_fraud,
)
from fraud_detection.simulation import simulate_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="small simulation for smoke testing (200 customers, 40 days)",
    )
    args = parser.parse_args()

    cfg = PipelineConfig()
    if args.quick:
        cfg.simulation = replace(
            cfg.simulation, n_customers=200, n_terminals=80, n_days=40
        )
        cfg.training = replace(
            cfg.training, train_duration=20, delay_duration=3, test_duration=10
        )

    figures_dir = PROJECT_ROOT / "reports" / "figures"
    models_dir = PROJECT_ROOT / "models"
    figures_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    print("[1/5] Simulating transactions ...")
    tx = simulate_dataset(cfg.simulation)
    fraud_pct = 100 * tx["TX_FRAUD"].mean()
    print(f"      {len(tx):,} transactions, {fraud_pct:.2f}% fraudulent")

    print("[2/5] Engineering features ...")
    tx = build_features(tx, cfg.features)

    print("[3/5] Training models on time-aware split ...")
    train, test = time_split(tx, cfg.training)
    print(f"      train: {len(train):,} tx | test: {len(test):,} tx")
    models = make_models(cfg.training)
    scored = fit_and_score(models, train, test)

    print("[4/5] Evaluating ...")
    metrics = evaluate_models(scored, list(models), cfg.training.top_k)
    print(metrics.to_string())

    print("[5/5] Writing reports and models ...")
    plot_class_balance(tx, figures_dir / "class_balance.png")
    plot_amount_distribution(tx, figures_dir / "amount_distribution.png")
    plot_daily_fraud(tx, figures_dir / "daily_volume.png")
    plot_curves(scored, list(models), figures_dir)

    summary = {
        "n_transactions": int(len(tx)),
        "fraud_rate_pct": round(fraud_pct, 3),
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "input_features": INPUT_FEATURES,
        "metrics": json.loads(metrics.reset_index().to_json(orient="records")),
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (PROJECT_ROOT / "reports" / "metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    for name, model in models.items():
        joblib.dump(model, models_dir / f"{name}.joblib")

    print(f"Done in {summary['runtime_seconds']}s. See reports/ and models/.")


if __name__ == "__main__":
    main()
