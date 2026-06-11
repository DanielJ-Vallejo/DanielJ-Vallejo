"""2D Ising model with the Metropolis algorithm (checkerboard, vectorized).

Square L×L lattice, periodic boundaries, J = 1, kB = 1. The exact critical
temperature is known from Onsager's solution: Tc = 2 / ln(1 + sqrt(2)).

The update uses two checkerboard sublattices so each half of the spins can
be flipped simultaneously with pure numpy — no compiled extension needed.
"""

from __future__ import annotations

import numpy as np

TC_EXACT = 2.0 / np.log(1.0 + np.sqrt(2.0))  # ≈ 2.2692


def random_lattice(L: int, rng: np.random.Generator) -> np.ndarray:
    """Random ±1 spin configuration."""
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=(L, L))


def total_energy(spins: np.ndarray) -> float:
    """Total energy with J=1 (each bond counted once)."""
    neighbors = np.roll(spins, 1, axis=0) + np.roll(spins, 1, axis=1)
    return float(-np.sum(spins * neighbors))


def _checkerboard_masks(L: int) -> tuple[np.ndarray, np.ndarray]:
    i, j = np.indices((L, L))
    even = (i + j) % 2 == 0
    return even, ~even


def metropolis_sweep(
    spins: np.ndarray, beta: float, rng: np.random.Generator
) -> np.ndarray:
    """One full lattice sweep: update both checkerboard sublattices."""
    L = spins.shape[0]
    for mask in _checkerboard_masks(L):
        neighbors = (
            np.roll(spins, 1, 0)
            + np.roll(spins, -1, 0)
            + np.roll(spins, 1, 1)
            + np.roll(spins, -1, 1)
        )
        dE = 2.0 * spins * neighbors
        accept = (dE <= 0) | (rng.random(spins.shape) < np.exp(-beta * dE))
        spins[accept & mask] *= -1
    return spins


def simulate(
    L: int,
    T: float,
    n_eq: int = 500,
    n_meas: int = 1000,
    seed: int = 42,
    init: str = "random",
) -> dict[str, np.ndarray | float]:
    """Equilibrate, then measure magnetization and energy per spin.

    Returns the time series plus ensemble observables: ``m_abs``,
    ``energy``, susceptibility ``chi`` and specific heat ``cv``.
    ``init="ordered"`` starts from the all-up ground state — recommended
    deep in the ferromagnetic phase to avoid domain-wall trapping.
    """
    rng = np.random.default_rng(seed)
    beta = 1.0 / T
    spins = (
        np.ones((L, L), dtype=np.int8) if init == "ordered" else random_lattice(L, rng)
    )
    N = L * L

    for _ in range(n_eq):
        metropolis_sweep(spins, beta, rng)

    M = np.empty(n_meas)
    E = np.empty(n_meas)
    for t in range(n_meas):
        metropolis_sweep(spins, beta, rng)
        M[t] = spins.sum()
        E[t] = total_energy(spins)

    return {
        "magnetization": M / N,
        "energy": E / N,
        "m_abs": float(np.mean(np.abs(M)) / N),
        "e_mean": float(np.mean(E) / N),
        "chi": float(beta * (np.mean(M**2) - np.mean(np.abs(M)) ** 2) / N),
        "cv": float(beta**2 * (np.mean(E**2) - np.mean(E) ** 2) / N),
        "spins": spins,
    }


def temperature_scan(
    L: int,
    temperatures: np.ndarray,
    n_eq: int = 400,
    n_meas: int = 600,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Observables as a function of temperature for one lattice size."""
    out = {k: [] for k in ("T", "m_abs", "e_mean", "chi", "cv")}
    for i, T in enumerate(temperatures):
        res = simulate(L, float(T), n_eq=n_eq, n_meas=n_meas, seed=seed + i)
        out["T"].append(float(T))
        for k in ("m_abs", "e_mean", "chi", "cv"):
            out[k].append(res[k])
    return {k: np.asarray(v) for k, v in out.items()}
