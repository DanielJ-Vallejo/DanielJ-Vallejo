"""Generate all simulation figures.

Usage::

    python scripts/run_all.py [--quick]

Runs the 2D/3D Ising temperature scans, the Langevin ensemble and the
random walks, writing figures to ``reports/figures/``.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from simulaciones import ising2d, ising3d, langevin, random_walk  # noqa: E402
from simulaciones.stats import blocked_jackknife  # noqa: E402

FIG = PROJECT_ROOT / "reports" / "figures"


def run_ising2d(quick: bool) -> None:
    sizes = [8, 16, 32] if not quick else [8]
    n_eq, n_meas = (400, 600) if not quick else (100, 150)
    temperatures = np.linspace(1.5, 3.5, 21 if not quick else 9)

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for L in sizes:
        scan = ising2d.temperature_scan(L, temperatures, n_eq=n_eq, n_meas=n_meas)
        axs[0, 0].plot(scan["T"], scan["m_abs"], "o-", ms=3, label=f"L={L}")
        axs[0, 1].plot(scan["T"], scan["e_mean"], "o-", ms=3, label=f"L={L}")
        axs[1, 0].plot(scan["T"], scan["chi"], "o-", ms=3, label=f"L={L}")
        axs[1, 1].plot(scan["T"], scan["cv"], "o-", ms=3, label=f"L={L}")
    titles = ["⟨|m|⟩", "⟨E⟩/N", "χ", "C_V/N"]
    for ax, t in zip(axs.flat, titles):
        ax.axvline(ising2d.TC_EXACT, color="gray", ls="--", alpha=0.7)
        ax.set_xlabel("T")
        ax.set_ylabel(t)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(
        f"2D Ising (Metropolis) — dashed line: Onsager Tc = {ising2d.TC_EXACT:.4f}"
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "ising2d_observables.png", dpi=130)
    plt.close(fig)

    # Magnetization with jackknife error bars at three temperatures
    fig, ax = plt.subplots(figsize=(7, 4.5))
    Ts = [1.8, ising2d.TC_EXACT, 3.0]
    labels = ["T < Tc (ordered)", "T ≈ Tc (critical)", "T > Tc (disordered)"]
    for T, lab in zip(Ts, labels):
        res = ising2d.simulate(16, float(T), n_eq=n_eq, n_meas=max(n_meas, 200))
        mean, var = blocked_jackknife(np.abs(res["magnetization"]), n_blocks=10)
        ax.errorbar([T], [mean], yerr=[np.sqrt(var)], fmt="o", capsize=4, label=lab)
    ax.set_xlabel("T")
    ax.set_ylabel("⟨|m|⟩ ± jackknife error")
    ax.set_title("2D Ising: magnetization with blocked-jackknife errors (L=16)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "ising2d_jackknife.png", dpi=130)
    plt.close(fig)
    print("OK ising2d figures")


def run_ising3d(quick: bool) -> None:
    L = 10 if not quick else 6
    n_eq, n_meas = (200, 200) if not quick else (60, 60)
    temperatures = np.linspace(3.0, 6.0, 13 if not quick else 7)

    obs = {k: [] for k in ("m_abs", "e_mean", "chi", "cv")}
    for i, T in enumerate(temperatures):
        res = ising3d.simulate(L, float(T), n_eq=n_eq, n_meas=n_meas, seed=42 + i)
        for k in obs:
            obs[k].append(res[k])

    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for ax, (k, ylab) in zip(
        axs.flat,
        [("m_abs", "⟨|m|⟩"), ("e_mean", "⟨E⟩/N"), ("chi", "χ"), ("cv", "C_V/N")],
    ):
        ax.plot(temperatures, obs[k], "o-", ms=4)
        ax.axvline(ising3d.TC_3D, color="gray", ls="--", alpha=0.7)
        ax.set_xlabel("T")
        ax.set_ylabel(ylab)
        ax.grid(alpha=0.3)
    fig.suptitle(f"3D Ising (L={L}) — dashed line: Tc ≈ {ising3d.TC_3D}")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "ising3d_observables.png", dpi=130)
    plt.close(fig)

    # Middle slice of the equilibrium configuration below/at/above Tc
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, T, tit in zip(
        axes, [3.0, ising3d.TC_3D, 6.0], ["T < Tc", "T ≈ Tc", "T > Tc"]
    ):
        res = ising3d.simulate(20 if not quick else 10, float(T), n_eq=n_eq, n_meas=1)
        spins = res["spins"]
        ax.imshow(spins[spins.shape[0] // 2], cmap="binary", interpolation="nearest")
        ax.set_title(f"{tit} (T={T:.2f})")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("3D Ising: central slice of equilibrium configurations")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(FIG / "ising3d_configs.png", dpi=130)
    plt.close(fig)
    print("OK ising3d figures")


def run_langevin(quick: bool) -> None:
    res = langevin.simulate_ensemble(
        n_particles=20000 if not quick else 2000,
        n_steps=2000 if not quick else 500,
        snapshot_times=(1.0, 5.0, 10.0, 20.0) if not quick else (1.0, 5.0),
    )
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for t, data in res["snapshots"].items():
        ax.hist(data, bins=60, density=True, alpha=0.45, label=f"t={t:g}")
        xx = np.linspace(data.min(), data.max(), 300)
        ax.plot(xx, langevin.gaussian_pdf(xx, t, res["D"]), "k", lw=1)
    ax.set_xlabel("x")
    ax.set_ylabel("probability density")
    ax.set_title("Overdamped Langevin: histograms vs exact Gaussian propagator")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "langevin_histograms.png", dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(res["tgrid"], res["var_t"], ".", ms=2, label="empirical Var[x(t)]")
    ax.plot(res["tgrid"], 2 * res["D"] * res["tgrid"], "r-", lw=2, label="theory 2Dt")
    coef = np.polyfit(res["tgrid"], res["var_t"], 1)
    ax.set_xlabel("t")
    ax.set_ylabel("Var[x(t)]")
    ax.set_title(f"Linear variance growth — fitted slope {coef[0]:.3f} (2D = {2*res['D']:.1f})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "langevin_variance.png", dpi=130)
    plt.close(fig)
    print(f"OK langevin figures (slope {coef[0]:.4f})")


def run_random_walk(quick: bool) -> None:
    n_walkers = 5000 if not quick else 500
    n_steps = 1000 if not quick else 200

    paths1d = random_walk.walk_1d(n_steps, n_walkers)
    msd = random_walk.mean_square_displacement(paths1d)
    steps = np.arange(n_steps + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    for i in range(min(30, n_walkers)):
        ax1.plot(steps, paths1d[i], lw=0.6, alpha=0.6)
    ax1.set_xlabel("step N")
    ax1.set_ylabel("x")
    ax1.set_title("1D random walk: sample trajectories")
    ax2.plot(steps, msd, label="empirical ⟨x²⟩")
    ax2.plot(steps, steps, "r--", label="theory ⟨x²⟩ = N")
    ax2.set_xlabel("step N")
    ax2.set_ylabel("⟨x²⟩")
    ax2.set_title("Diffusive scaling")
    ax2.legend()
    fig.tight_layout()
    fig.savefig(FIG / "random_walk_1d.png", dpi=130)
    plt.close(fig)

    paths2d = random_walk.walk_2d(n_steps, 3)
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    for i in range(3):
        ax.plot(paths2d[i, :, 0], paths2d[i, :, 1], lw=0.8)
    ax.plot(0, 0, "ko", label="origin")
    ax.set_title("2D random walk: three sample paths")
    ax.set_aspect("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "random_walk_2d.png", dpi=130)
    plt.close(fig)
    print("OK random walk figures")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="fast smoke run")
    args = parser.parse_args()

    FIG.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    run_random_walk(args.quick)
    run_langevin(args.quick)
    run_ising2d(args.quick)
    run_ising3d(args.quick)
    print(f"All figures written to {FIG} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
