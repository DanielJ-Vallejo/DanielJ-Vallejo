"""Physics sanity checks for the simulation package."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from simulaciones import ising2d, ising3d, langevin, random_walk
from simulaciones.stats import blocked_jackknife, jackknife


def test_jackknife_matches_classic_estimators():
    rng = np.random.default_rng(0)
    x = rng.normal(3.0, 1.0, 500)
    mean, var = jackknife(x)
    assert mean == pytest.approx(x.mean(), rel=1e-10)
    assert var == pytest.approx(x.var(ddof=1) / x.size, rel=1e-6)


def test_blocked_jackknife_requires_enough_data():
    with pytest.raises(ValueError):
        blocked_jackknife(np.arange(10), n_blocks=20)


def test_ising2d_energy_bounds():
    rng = np.random.default_rng(1)
    spins = ising2d.random_lattice(16, rng)
    e = ising2d.total_energy(spins) / spins.size
    assert -2.0 <= e <= 2.0  # per-spin energy of the square lattice


def test_ising2d_orders_at_low_T_disorders_at_high_T():
    cold = ising2d.simulate(16, T=1.0, n_eq=200, n_meas=100, seed=3, init="ordered")
    hot = ising2d.simulate(16, T=5.0, n_eq=200, n_meas=100, seed=3)
    assert cold["m_abs"] > 0.9  # ferromagnetic phase
    assert hot["m_abs"] < 0.3  # paramagnetic phase


def test_ising2d_is_reproducible():
    a = ising2d.simulate(8, T=2.0, n_eq=50, n_meas=50, seed=7)
    b = ising2d.simulate(8, T=2.0, n_eq=50, n_meas=50, seed=7)
    assert np.array_equal(a["magnetization"], b["magnetization"])


def test_ising3d_orders_at_low_T():
    # ordered start avoids domain-wall trapping deep in the cold phase
    cold = ising3d.simulate(8, T=2.0, n_eq=150, n_meas=50, seed=5, init="ordered")
    hot = ising3d.simulate(8, T=8.0, n_eq=150, n_meas=50, seed=5)
    assert cold["m_abs"] > 0.9
    assert hot["m_abs"] < 0.3


def test_langevin_variance_grows_linearly():
    res = langevin.simulate_ensemble(
        D=1.0, dt=0.01, n_steps=500, n_particles=5000, snapshot_times=(1.0,)
    )
    slope = np.polyfit(res["tgrid"], res["var_t"], 1)[0]
    assert slope == pytest.approx(2.0, rel=0.1)  # Var[x] = 2 D t


def test_random_walk_msd_scaling():
    paths = random_walk.walk_1d(n_steps=500, n_walkers=4000, seed=11)
    msd = random_walk.mean_square_displacement(paths)
    assert msd[0] == 0.0
    assert msd[-1] == pytest.approx(500, rel=0.1)  # <x²> = N


def test_random_walk_2d_steps_are_unit_moves():
    paths = random_walk.walk_2d(n_steps=100, n_walkers=10, seed=2)
    diffs = np.diff(paths, axis=1)
    assert np.all(np.abs(diffs).sum(axis=2) == 1)
