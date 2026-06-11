"""Fraud-specific evaluation metrics.

Besides threshold-free metrics (ROC-AUC, Average Precision), the key
operational metric is **Card Precision@k**: a fraud team can only review
``k`` cards per day, so we measure the fraction of truly compromised cards
among the ``k`` highest-scored cards of each test day.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score


def card_precision_top_k(
    scored: pd.DataFrame, score_col: str, k: int
) -> float:
    """Mean daily precision of the top-``k`` most suspicious cards.

    For every day in ``scored``, cards are ranked by their maximum
    transaction score; precision is the fraction of the ``k`` selected
    cards that had at least one fraudulent transaction that day.
    """
    precisions = []
    for _, day_tx in scored.groupby("TX_TIME_DAYS"):
        per_card = day_tx.groupby("CUSTOMER_ID").agg(
            score=(score_col, "max"), fraud=("TX_FRAUD", "max")
        )
        top = per_card.nlargest(k, "score")
        precisions.append(top["fraud"].mean())
    return float(np.mean(precisions))


def evaluate_models(
    scored: pd.DataFrame, model_names: list[str], top_k: int
) -> pd.DataFrame:
    """Compute ROC-AUC, Average Precision and Card Precision@k per model."""
    y_true = scored["TX_FRAUD"]
    rows = []
    for name in model_names:
        score = scored[f"SCORE_{name}"]
        rows.append(
            {
                "model": name,
                "roc_auc": roc_auc_score(y_true, score),
                "average_precision": average_precision_score(y_true, score),
                f"card_precision_top_{top_k}": card_precision_top_k(
                    scored, f"SCORE_{name}", top_k
                ),
            }
        )
    return pd.DataFrame(rows).set_index("model").round(4)
