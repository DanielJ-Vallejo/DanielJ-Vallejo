"""Feature engineering for transaction-level fraud detection.

Three families of features are produced:

* **Datetime features** — weekend / night indicators.
* **Customer behaviour** — number of transactions and average amount over
  sliding windows (RFM-style aggregates).
* **Terminal risk** — number of transactions and observed fraud rate per
  terminal over sliding windows, shifted by a *delay* period to reflect
  that fraud labels only become available days after the transaction.
"""

from __future__ import annotations

import pandas as pd

from .config import FeatureConfig


def add_datetime_features(tx: pd.DataFrame) -> pd.DataFrame:
    """Add weekend and night indicators derived from ``TX_DATETIME``."""
    tx = tx.copy()
    tx["TX_DURING_WEEKEND"] = (tx["TX_DATETIME"].dt.weekday >= 5).astype(int)
    tx["TX_DURING_NIGHT"] = (tx["TX_DATETIME"].dt.hour <= 6).astype(int)
    return tx


def _customer_aggregates(group: pd.DataFrame, windows: tuple) -> pd.DataFrame:
    g = group.sort_values("TX_DATETIME").set_index("TX_DATETIME")
    out = pd.DataFrame(index=g.index)
    for w in windows:
        rolled = g["TX_AMOUNT"].rolling(f"{w}D")
        out[f"CUSTOMER_ID_NB_TX_{w}DAY_WINDOW"] = rolled.count()
        out[f"CUSTOMER_ID_AVG_AMOUNT_{w}DAY_WINDOW"] = rolled.mean()
    out["TRANSACTION_ID"] = g["TRANSACTION_ID"].to_numpy()
    return out.reset_index(drop=True)


def add_customer_features(tx: pd.DataFrame, cfg: FeatureConfig) -> pd.DataFrame:
    """Sliding-window count and mean amount per customer (includes current tx)."""
    parts = [
        _customer_aggregates(g, cfg.customer_windows)
        for _, g in tx.groupby("CUSTOMER_ID", sort=False)
    ]
    feats = pd.concat(parts, ignore_index=True)
    return tx.merge(feats, on="TRANSACTION_ID", how="left")


def _terminal_aggregates(group: pd.DataFrame, windows: tuple, delay: int) -> pd.DataFrame:
    g = group.sort_values("TX_DATETIME").set_index("TX_DATETIME")
    # Counts over the delay period (labels assumed unknown there)
    nb_delay = g["TX_FRAUD"].rolling(f"{delay}D").count()
    fraud_delay = g["TX_FRAUD"].rolling(f"{delay}D").sum()
    out = pd.DataFrame(index=g.index)
    for w in windows:
        nb_total = g["TX_FRAUD"].rolling(f"{delay + w}D").count()
        fraud_total = g["TX_FRAUD"].rolling(f"{delay + w}D").sum()
        nb_window = nb_total - nb_delay
        fraud_window = fraud_total - fraud_delay
        risk = (fraud_window / nb_window).fillna(0.0)
        out[f"TERMINAL_ID_NB_TX_{w}DAY_WINDOW"] = nb_window
        out[f"TERMINAL_ID_RISK_{w}DAY_WINDOW"] = risk
    out["TRANSACTION_ID"] = g["TRANSACTION_ID"].to_numpy()
    return out.reset_index(drop=True)


def add_terminal_features(tx: pd.DataFrame, cfg: FeatureConfig) -> pd.DataFrame:
    """Delayed sliding-window transaction count and fraud risk per terminal."""
    parts = [
        _terminal_aggregates(g, cfg.terminal_windows, cfg.terminal_delay)
        for _, g in tx.groupby("TERMINAL_ID", sort=False)
    ]
    feats = pd.concat(parts, ignore_index=True)
    return tx.merge(feats, on="TRANSACTION_ID", how="left")


def build_features(tx: pd.DataFrame, cfg: FeatureConfig | None = None) -> pd.DataFrame:
    """Apply the full feature engineering pipeline to raw transactions."""
    cfg = cfg or FeatureConfig()
    tx = add_datetime_features(tx)
    tx = add_customer_features(tx, cfg)
    tx = add_terminal_features(tx, cfg)
    return tx.sort_values("TX_TIME_SECONDS", ignore_index=True)
