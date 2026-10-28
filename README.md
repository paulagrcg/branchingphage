# branchingphage

Simulation of Branching under First-Passage Resetting.

## Model implemented

This repository includes a minimal Monte Carlo simulator for a one-dimensional branching diffusion process with first-passage resetting:

- Particles start at `x0 > boundary`.
- Each time step applies drift-diffusion dynamics.
- Surviving particles branch with probability `branching_rate * dt` (binary branching).
- If any particle reaches the boundary (`x <= boundary`), a global first-passage reset is triggered and the system restarts from a single particle at `x0`.

## Run

```bash
python /home/runner/work/branchingphage/branchingphage/fpr_branching.py --runs 1000 --seed 0
```

The CLI prints JSON with ensemble averages.

## Test

```bash
python -m unittest /home/runner/work/branchingphage/branchingphage/test_fpr_branching.py
```
