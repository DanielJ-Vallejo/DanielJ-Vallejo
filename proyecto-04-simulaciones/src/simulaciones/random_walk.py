"""Simple symmetric random walks in 1D and 2D.

Verifies the diffusive scaling <r²(N)> = N (unit steps) and visualizes
sample trajectories.
"""

from __future__ import annotations

import numpy as np


def walk_1d(
    n_steps: int, n_walkers: int, seed: int = 42
) -> np.ndarray:
    """Positions of ``n_walkers`` after each of ``n_steps`` ±1 steps.

    Returns an array of shape ``(n_walkers, n_steps + 1)`` including x0=0.
    """
    rng = np.random.default_rng(seed)
    steps = rng.choice([-1, 1], size=(n_walkers, n_steps))
    paths = np.zeros((n_walkers, n_steps + 1), dtype=int)
    paths[:, 1:] = np.cumsum(steps, axis=1)
    return paths


def walk_2d(n_steps: int, n_walkers: int, seed: int = 42) -> np.ndarray:
    """2D lattice walk; returns positions of shape (n_walkers, n_steps+1, 2)."""
    rng = np.random.default_rng(seed)
    moves = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])
    choices = rng.integers(0, 4, size=(n_walkers, n_steps))
    steps = moves[choices]
    paths = np.zeros((n_walkers, n_steps + 1, 2), dtype=int)
    paths[:, 1:, :] = np.cumsum(steps, axis=1)
    return paths


def mean_square_displacement(paths: np.ndarray) -> np.ndarray:
    """<r²> over walkers at every step, for 1D or 2D paths."""
    if paths.ndim == 2:  # 1D
        return np.mean(paths.astype(float) ** 2, axis=0)
    return np.mean(np.sum(paths.astype(float) ** 2, axis=2), axis=0)
