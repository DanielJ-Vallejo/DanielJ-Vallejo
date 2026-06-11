"""Synthetic credit card transaction generator with fraud injection.

Original re-implementation inspired by the methodology of the
*Reproducible Machine Learning for Credit Card Fraud Detection — Practical
Handbook* (Le Borgne et al., ULB, 2022). See ``references/README.md``.

Three fraud scenarios are injected on top of legitimate traffic:

1. **Amount anomaly** — any transaction above a fixed amount is fraudulent
   (sanity-check scenario, trivially detectable from ``TX_AMOUNT``).
2. **Compromised terminals** — every day a few terminals are compromised;
   all their transactions during the following weeks are fraudulent
   (detectable through terminal risk aggregates).
3. **Compromised customers** — every day a few customers have their card
   details leaked; for two weeks a third of their transactions show
   inflated amounts (detectable through customer spending aggregates).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import SimulationConfig


def generate_customer_profiles(cfg: SimulationConfig) -> pd.DataFrame:
    """Create customer profiles with location and spending behaviour."""
    rng = np.random.default_rng(cfg.random_state)
    n = cfg.n_customers
    mean_amount = rng.uniform(5.0, 100.0, n)
    return pd.DataFrame(
        {
            "CUSTOMER_ID": np.arange(n),
            "x_customer": rng.uniform(0, 100, n),
            "y_customer": rng.uniform(0, 100, n),
            "mean_amount": mean_amount,
            "std_amount": mean_amount / 2.0,
            "mean_nb_tx_per_day": rng.uniform(0.0, 4.0, n),
        }
    )


def generate_terminal_profiles(cfg: SimulationConfig) -> pd.DataFrame:
    """Create payment terminal profiles with a 2D location."""
    rng = np.random.default_rng(cfg.random_state + 1)
    n = cfg.n_terminals
    return pd.DataFrame(
        {
            "TERMINAL_ID": np.arange(n),
            "x_terminal": rng.uniform(0, 100, n),
            "y_terminal": rng.uniform(0, 100, n),
        }
    )


def assign_terminals_to_customers(
    customers: pd.DataFrame, terminals: pd.DataFrame, radius: float
) -> pd.Series:
    """For each customer, list the terminal ids within ``radius``."""
    term_xy = terminals[["x_terminal", "y_terminal"]].to_numpy()

    def nearby(row: pd.Series) -> list[int]:
        d = np.sqrt(
            (term_xy[:, 0] - row["x_customer"]) ** 2
            + (term_xy[:, 1] - row["y_customer"]) ** 2
        )
        return list(np.flatnonzero(d < radius))

    return customers.apply(nearby, axis=1)


def generate_transactions(cfg: SimulationConfig) -> pd.DataFrame:
    """Generate legitimate transactions for all customers over ``n_days``."""
    rng = np.random.default_rng(cfg.random_state + 2)
    customers = generate_customer_profiles(cfg)
    terminals = generate_terminal_profiles(cfg)
    customers["available_terminals"] = assign_terminals_to_customers(
        customers, terminals, cfg.radius
    )

    rows: list[tuple] = []
    seconds_in_day = 86400
    for cust in customers.itertuples(index=False):
        if len(cust.available_terminals) == 0:
            continue
        avail = np.asarray(cust.available_terminals)
        for day in range(cfg.n_days):
            n_tx = rng.poisson(cust.mean_nb_tx_per_day)
            if n_tx == 0:
                continue
            # time of day centred at noon, clipped to the day
            times = np.clip(
                rng.normal(seconds_in_day / 2, 20000, n_tx), 0, seconds_in_day - 1
            ).astype(int)
            amounts = np.maximum(
                np.round(rng.normal(cust.mean_amount, cust.std_amount, n_tx), 2),
                0.01,
            )
            term_ids = rng.choice(avail, n_tx)
            for t, amount, term in zip(times, amounts, term_ids):
                rows.append(
                    (day * seconds_in_day + t, day, cust.CUSTOMER_ID, term, amount)
                )

    tx = pd.DataFrame(
        rows,
        columns=["TX_TIME_SECONDS", "TX_TIME_DAYS", "CUSTOMER_ID", "TERMINAL_ID", "TX_AMOUNT"],
    ).sort_values("TX_TIME_SECONDS", ignore_index=True)
    tx["TX_DATETIME"] = pd.to_datetime(
        tx["TX_TIME_SECONDS"], unit="s", origin=pd.Timestamp(cfg.start_date)
    )
    tx.insert(0, "TRANSACTION_ID", np.arange(len(tx)))
    return tx


def add_fraud_scenarios(tx: pd.DataFrame, cfg: SimulationConfig) -> pd.DataFrame:
    """Flag transactions as fraudulent according to the three scenarios."""
    rng = np.random.default_rng(cfg.random_state + 3)
    tx = tx.copy()
    tx["TX_FRAUD"] = 0
    tx["TX_FRAUD_SCENARIO"] = 0

    # Scenario 1: amount anomaly
    mask1 = tx["TX_AMOUNT"] > cfg.amount_fraud_threshold
    tx.loc[mask1, ["TX_FRAUD", "TX_FRAUD_SCENARIO"]] = [1, 1]

    n_terminals = int(tx["TERMINAL_ID"].max()) + 1
    n_customers = int(tx["CUSTOMER_ID"].max()) + 1

    # Scenario 2: compromised terminals
    n_days = int(tx["TX_TIME_DAYS"].max()) + 1
    for day in range(n_days):
        n_comp = rng.poisson(cfg.terminal_compromise_rate * n_terminals)
        if n_comp == 0:
            continue
        compromised = rng.choice(n_terminals, min(n_comp, n_terminals), replace=False)
        mask2 = (
            tx["TERMINAL_ID"].isin(compromised)
            & (tx["TX_TIME_DAYS"] >= day)
            & (tx["TX_TIME_DAYS"] < day + cfg.terminal_compromise_duration)
        )
        tx.loc[mask2, ["TX_FRAUD", "TX_FRAUD_SCENARIO"]] = [1, 2]

    # Scenario 3: compromised customers (card-not-present leak)
    for day in range(n_days):
        n_comp = rng.poisson(cfg.customer_compromise_rate * n_customers)
        if n_comp == 0:
            continue
        compromised = rng.choice(n_customers, min(n_comp, n_customers), replace=False)
        window = (
            tx["CUSTOMER_ID"].isin(compromised)
            & (tx["TX_TIME_DAYS"] >= day)
            & (tx["TX_TIME_DAYS"] < day + cfg.customer_compromise_duration)
        )
        idx = tx.index[window]
        if len(idx) == 0:
            continue
        hit = rng.random(len(idx)) < 1 / 3
        chosen = idx[hit]
        tx.loc[chosen, "TX_AMOUNT"] = tx.loc[chosen, "TX_AMOUNT"] * cfg.customer_fraud_amount_factor
        tx.loc[chosen, ["TX_FRAUD", "TX_FRAUD_SCENARIO"]] = [1, 3]

    return tx


def simulate_dataset(cfg: SimulationConfig | None = None) -> pd.DataFrame:
    """Full simulation: legitimate traffic plus injected fraud."""
    cfg = cfg or SimulationConfig()
    return add_fraud_scenarios(generate_transactions(cfg), cfg)
