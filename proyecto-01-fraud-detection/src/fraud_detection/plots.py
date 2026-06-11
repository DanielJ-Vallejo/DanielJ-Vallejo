"""Diagnostic plots for the fraud detection pipeline."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve


def plot_class_balance(tx: pd.DataFrame, out: Path) -> None:
    counts = tx["TX_FRAUD"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["Legitimate", "Fraud"], counts.to_numpy(), color=["#4c72b0", "#c44e52"])
    pct = 100 * counts.get(1, 0) / counts.sum()
    ax.set_ylabel("Transactions")
    ax.set_title(f"Class balance — fraud = {pct:.2f}% of transactions")
    ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_amount_distribution(tx: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for label, color, name in [(0, "#4c72b0", "Legitimate"), (1, "#c44e52", "Fraud")]:
        ax.hist(
            tx.loc[tx["TX_FRAUD"] == label, "TX_AMOUNT"],
            bins=60,
            alpha=0.6,
            density=True,
            color=color,
            label=name,
        )
    ax.set_xlabel("Transaction amount")
    ax.set_ylabel("Density")
    ax.set_title("Amount distribution by class")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_daily_fraud(tx: pd.DataFrame, out: Path) -> None:
    daily = tx.groupby("TX_TIME_DAYS").agg(
        n_tx=("TRANSACTION_ID", "count"), n_fraud=("TX_FRAUD", "sum")
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(daily.index, daily["n_tx"], label="All transactions", color="#4c72b0")
    ax.plot(daily.index, daily["n_fraud"], label="Fraudulent", color="#c44e52")
    ax.set_xlabel("Day")
    ax.set_ylabel("Transactions per day")
    ax.set_title("Daily transaction and fraud volume")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_curves(scored: pd.DataFrame, model_names: list[str], out_dir: Path) -> None:
    """ROC and precision-recall curves for every model on the test period."""
    y = scored["TX_FRAUD"]

    fig, ax = plt.subplots(figsize=(6, 5))
    for name in model_names:
        fpr, tpr, _ = roc_curve(y, scored[f"SCORE_{name}"])
        ax.plot(fpr, tpr, label=name)
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("ROC curves (test period)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "roc_curves.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    for name in model_names:
        prec, rec, _ = precision_recall_curve(y, scored[f"SCORE_{name}"])
        ax.plot(rec, prec, label=name)
    baseline = y.mean()
    ax.axhline(baseline, color="k", ls="--", lw=1, label=f"chance ({baseline:.3f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall curves (test period)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "pr_curves.png", dpi=130)
    plt.close(fig)
