"""Titanic survival prediction — end-to-end run.

Usage::

    python scripts/run_pipeline.py

Loads the data (downloads on first run), compares three models with
stratified 5-fold cross-validation, evaluates the best one on a holdout
set and writes metrics + figures to ``reports/``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_validate, train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from titanic_ml.data import TARGET, engineer_features, load_titanic  # noqa: E402
from titanic_ml.pipeline import make_models  # noqa: E402

DATA_PATH = PROJECT_ROOT.parent / "data" / "raw" / "titanic" / "titanic.csv"
RANDOM_STATE = 42


def main() -> None:
    reports = PROJECT_ROOT / "reports"
    figures = reports / "figures"
    models_dir = PROJECT_ROOT / "models"
    figures.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    print("[1/4] Loading data ...")
    df = engineer_features(load_titanic(DATA_PATH))
    X, y = df.drop(columns=[TARGET]), df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    print(f"      {len(df)} passengers | survival rate {y.mean():.1%}")

    print("[2/4] Cross-validating models (5-fold) ...")
    models = make_models(RANDOM_STATE)
    cv_rows = []
    for name, model in models.items():
        cv = cross_validate(
            model,
            X_train,
            y_train,
            cv=5,
            scoring=["accuracy", "roc_auc", "f1"],
            n_jobs=-1,
        )
        cv_rows.append(
            {
                "model": name,
                "cv_accuracy": cv["test_accuracy"].mean(),
                "cv_accuracy_std": cv["test_accuracy"].std(),
                "cv_roc_auc": cv["test_roc_auc"].mean(),
                "cv_f1": cv["test_f1"].mean(),
            }
        )
    cv_results = pd.DataFrame(cv_rows).set_index("model").round(4)
    print(cv_results.to_string())

    best_name = cv_results["cv_roc_auc"].idxmax()
    print(f"[3/4] Fitting best model on full training set: {best_name}")
    best = models[best_name].fit(X_train, y_train)
    y_pred = best.predict(X_test)
    y_score = best.predict_proba(X_test)[:, 1]
    holdout = {
        "model": best_name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_score), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
    }
    print(f"      holdout: {holdout}")

    print("[4/4] Writing reports ...")
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, display_labels=["Died", "Survived"], ax=ax, colorbar=False
    )
    ax.set_title(f"Confusion matrix — {best_name} (holdout)")
    fig.tight_layout()
    fig.savefig(figures / "confusion_matrix.png", dpi=130)
    plt.close(fig)

    # Permutation-free importance proxy: one-hot feature coefficients/importances
    prep = best.named_steps["prep"]
    clf = best.named_steps["clf"]
    feat_names = prep.get_feature_names_out()
    importances = getattr(clf, "feature_importances_", None)
    if importances is None and hasattr(clf, "coef_"):
        importances = np.abs(clf.coef_[0])
    if importances is not None:
        order = np.argsort(importances)[-12:]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh([feat_names[i] for i in order], importances[order], color="#4c72b0")
        ax.set_title(f"Top features — {best_name}")
        fig.tight_layout()
        fig.savefig(figures / "feature_importance.png", dpi=130)
        plt.close(fig)

    # Survival-by-group EDA figure
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, col in zip(axes, ["Sex", "Pclass", "Title"]):
        rate = df.groupby(col, observed=True)[TARGET].mean().sort_values()
        ax.bar(rate.index.astype(str), rate.to_numpy(), color="#4c72b0")
        ax.set_title(f"Survival rate by {col}")
        ax.set_ylim(0, 1)
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(figures / "survival_by_group.png", dpi=130)
    plt.close(fig)

    summary = {
        "n_passengers": int(len(df)),
        "survival_rate": round(float(y.mean()), 4),
        "cross_validation": json.loads(cv_results.reset_index().to_json(orient="records")),
        "best_model": best_name,
        "holdout": holdout,
    }
    (reports / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    joblib.dump(best, models_dir / f"{best_name}.joblib")
    print("Done. See reports/ and models/.")


if __name__ == "__main__":
    main()
