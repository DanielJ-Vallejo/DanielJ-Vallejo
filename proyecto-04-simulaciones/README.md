# ⚛️ Statistical Physics Simulations / Simulaciones de Física Estadística

> **EN** — Monte Carlo and stochastic dynamics from my Physics degree at UNAM, packaged
> as a tested Python library: 2D/3D Ising models (vectorized checkerboard Metropolis),
> overdamped Langevin dynamics and random walks — each validated against exact
> theoretical results.
>
> **ES** — Monte Carlo y dinámica estocástica de mi carrera de Física en la UNAM,
> empaquetados como librería Python con tests: modelos de Ising 2D/3D (Metropolis
> checkerboard vectorizado), dinámica de Langevin sobreamortiguada y caminatas
> aleatorias — cada uno validado contra resultados teóricos exactos.

![Python](https://img.shields.io/badge/python-3.11-blue) ![NumPy](https://img.shields.io/badge/numpy-vectorized-green) ![tests](https://img.shields.io/badge/tests-9%20passing-brightgreen)

---

## 🇬🇧 English

### What's inside

| Module | Physics | Validation |
|---|---|---|
| `ising2d.py` | Phase transition on the square lattice, Metropolis with simultaneous checkerboard sublattice updates | Onsager's exact Tc = 2/ln(1+√2) ≈ 2.269 visible in χ and C_V peaks |
| `ising3d.py` | Cubic lattice, no exact solution | Numerical Tc ≈ 4.5115 reproduced by susceptibility peak |
| `langevin.py` | Euler-Maruyama integration of overdamped Brownian motion | Var[x(t)] = 2Dt — fitted slope 2.014 vs exact 2.0 |
| `random_walk.py` | 1D/2D lattice walks | Diffusive scaling ⟨x²⟩ = N |
| `stats.py` | Jackknife + blocked jackknife error estimation | Matches σ²/n on i.i.d. data to 1e-6 |

### Highlights

- **Pure NumPy checkerboard updates**: both Ising models update half the lattice per
  vectorized operation — no compiled extensions needed, full 2D scan (3 sizes × 21
  temperatures) in seconds.
- **Honest error bars**: Monte Carlo samples are autocorrelated, so naive standard
  errors are biased; the blocked jackknife handles this correctly.
- **Physics-based tests**: ferromagnetic ordering at low T, paramagnetic disorder at
  high T, exact diffusion law, energy bounds — 9 assertions a wrong implementation
  cannot pass.

```bash
pip install -r requirements.txt
python scripts/run_all.py          # all figures (~30 s)
pytest tests/ -q
```

---

## 🇪🇸 Español

### Contenido

| Módulo | Física | Validación |
|---|---|---|
| `ising2d.py` | Transición de fase en red cuadrada, Metropolis con actualización simultánea por subredes de ajedrez | Tc exacta de Onsager = 2/ln(1+√2) ≈ 2.269 visible en los picos de χ y C_V |
| `ising3d.py` | Red cúbica, sin solución exacta | Tc numérica ≈ 4.5115 reproducida por el pico de susceptibilidad |
| `langevin.py` | Integración Euler-Maruyama del movimiento browniano sobreamortiguado | Var[x(t)] = 2Dt — pendiente ajustada 2.014 vs 2.0 exacto |
| `random_walk.py` | Caminatas en red 1D/2D | Escalamiento difusivo ⟨x²⟩ = N |
| `stats.py` | Estimación de errores jackknife y jackknife por bloques | Coincide con σ²/n en datos i.i.d. a 1e-6 |

### Puntos destacados

- **Actualización checkerboard en NumPy puro**: ambos modelos de Ising actualizan media
  red por operación vectorizada — sin extensiones compiladas, el barrido 2D completo
  (3 tamaños × 21 temperaturas) corre en segundos.
- **Barras de error honestas**: las muestras de Monte Carlo están autocorrelacionadas;
  el jackknife por bloques lo maneja correctamente.
- **Tests basados en física**: orden ferromagnético a T baja, desorden paramagnético a
  T alta, ley de difusión exacta, cotas de energía — 9 aserciones que una
  implementación incorrecta no puede pasar.

### Figuras generadas (`reports/figures/`)

`ising2d_observables.png` · `ising2d_jackknife.png` · `ising3d_observables.png` ·
`ising3d_configs.png` · `langevin_histograms.png` · `langevin_variance.png` ·
`random_walk_1d.png` · `random_walk_2d.png`
