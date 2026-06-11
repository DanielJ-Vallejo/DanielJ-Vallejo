"""3D Ising model: checkerboard Metropolis on a cubic lattice.

L×L×L lattice with periodic boundaries, J = 1, kB = 1. There is no exact
solution in 3D; the critical temperature is known numerically:
Tc ≈ 4.5115.
"""

from __future__ import annotations

import numpy as np

TC_3D = 4.5115


def _masks(L: int) -> tuple[np.ndarray, np.ndarray]:
    i, j, k = np.indices((L, L, L))
    even = (i + j + k) % 2 == 0
    return even, ~even


def total_energy(spins: np.ndarray) -> float:
    neighbors = (
        np.roll(spins, 1, 0) + np.roll(spins, 1, 1) + np.roll(spins, 1, 2)
    )
    return float(-np.sum(spins * neighbors))


def metropolis_sweep(
    spins: np.ndarray, beta: float, rng: np.random.Generator
) -> np.ndarray:
    """One full sweep over both 3D checkerboard sublattices."""
    for mask in _masks(spins.shape[0]):
        neighbors = (
            np.roll(spins, 1, 0)
            + np.roll(spins, -1, 0)
            + np.roll(spins, 1, 1)
            + np.roll(spins, -1, 1)
            + np.roll(spins, 1, 2)
            + np.roll(spins, -1, 2)
        )
        dE = 2.0 * spins * neighbors
        accept = (dE <= 0) | (rng.random(spins.shape) < np.exp(-beta * dE))
        spins[accept & mask] *= -1
    return spins


def simulate(
    L: int,
    T: float,
    n_eq: int = 300,
    n_meas: int = 300,
    seed: int = 42,
    init: str = "random",
) -> dict[str, float | np.ndarray]:
    """Measure <|m|>, energy, susceptibility and specific heat per spin.

    ``init="ordered"`` starts from the all-up ground state — standard
    practice deep in the ferromagnetic phase, where a random start can get
    trapped in long-lived domain-wall states.
    """
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    if init == "ordered":
        spins = np.ones((L, L, L), dtype=np.int8)
    else:
        spins = rng.choice(np.array([-1, 1], dtype=np.int8), size=(L, L, L))
    N = L**3

    for _ in range(n_eq):
        metropolis_sweep(spins, beta, rng)

    M = np.empty(n_meas)
    E = np.empty(n_meas)
    for t in range(n_meas):
        metropolis_sweep(spins, beta, rng)
        M[t] = spins.sum()
        E[t] = total_energy(spins)

    return {
        "m_abs": float(np.mean(np.abs(M)) / N),
        "e_mean": float(np.mean(E) / N),
        "chi": float(beta * (np.mean(M**2) - np.mean(np.abs(M)) ** 2) / N),
        "cv": float(beta**2 * (np.mean(E**2) - np.mean(E) ** 2) / N),
        "spins": spins,
    }
