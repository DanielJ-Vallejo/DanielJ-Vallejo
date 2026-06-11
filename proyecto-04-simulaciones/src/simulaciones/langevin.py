"""Overdamped Langevin dynamics (free Brownian motion).

    gamma * dx/dt = eta(t),    <eta(t) eta(t')> = 2 gamma kB T delta(t-t')

reduces to a Wiener process with diffusion constant D = kB T / gamma.
Integrated with Euler-Maruyama:

    x_{n+1} = x_n + sqrt(2 D dt) * xi,    xi ~ N(0, 1)

The analytic checks are Var[x(t)] = 2 D t and a Gaussian position
distribution at every time.
"""

from __future__ import annotations

import numpy as np


def simulate_ensemble(
    D: float = 1.0,
    dt: float = 0.01,
    n_steps: int = 2000,
    n_particles: int = 20000,
    snapshot_times: tuple = (1.0, 5.0, 10.0, 20.0),
    seed: int = 2026,
) -> dict:
    """Evolve an ensemble of independent particles from x=0.

    Returns the variance time series, time grid and position snapshots.
    """
    rng = np.random.default_rng(seed)
    x = np.zeros(n_particles)
    var_t = np.zeros(n_steps + 1)
    tgrid = np.arange(n_steps + 1) * dt
    snapshots: dict[float, np.ndarray] = {}

    for n in range(1, n_steps + 1):
        x += np.sqrt(2.0 * D * dt) * rng.standard_normal(n_particles)
        var_t[n] = x.var()
        t = n * dt
        for ts in snapshot_times:
            if abs(t - ts) < dt / 2:
                snapshots[ts] = x.copy()

    return {"tgrid": tgrid, "var_t": var_t, "snapshots": snapshots, "D": D}


def gaussian_pdf(x: np.ndarray, t: float, D: float) -> np.ndarray:
    """Exact free-diffusion propagator from a point source at the origin."""
    sigma2 = 2.0 * D * t
    return np.exp(-(x**2) / (2.0 * sigma2)) / np.sqrt(2.0 * np.pi * sigma2)
