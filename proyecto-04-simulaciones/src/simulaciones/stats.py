"""Resampling-based error estimation for correlated Monte Carlo data."""

from __future__ import annotations

import numpy as np


def jackknife(values: np.ndarray) -> tuple[float, float]:
    """Jackknife estimate of the mean and its variance.

    Returns ``(mean, variance_of_mean)``. The jackknife removes one sample
    at a time, recomputes the estimator and uses the spread of the
    leave-one-out estimates — robust for the correlated samples produced
    by Markov chain Monte Carlo.
    """
    values = np.asarray(values, dtype=float)
    n = values.size
    if n < 2:
        raise ValueError("jackknife requires at least 2 samples")
    total = values.sum()
    loo_means = (total - values) / (n - 1)
    theta = loo_means.mean()
    var = (n - 1) / n * np.sum((loo_means - theta) ** 2)
    return float(theta), float(var)


def blocked_jackknife(values: np.ndarray, n_blocks: int = 20) -> tuple[float, float]:
    """Jackknife over time-series blocks to handle autocorrelation."""
    values = np.asarray(values, dtype=float)
    if n_blocks < 2 or values.size < 2 * n_blocks:
        raise ValueError("need at least 2 blocks with 2+ samples each")
    usable = values[: values.size - values.size % n_blocks]
    blocks = usable.reshape(n_blocks, -1).mean(axis=1)
    return jackknife(blocks)
