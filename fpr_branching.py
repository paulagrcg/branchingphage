from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    total_time: float = 10.0
    dt: float = 0.01
    diffusion: float = 1.0
    drift: float = 0.0
    branching_rate: float = 0.25
    x0: float = 1.0
    boundary: float = 0.0

    def validate(self) -> None:
        if self.total_time <= 0:
            raise ValueError("total_time must be positive")
        if self.dt <= 0:
            raise ValueError("dt must be positive")
        if self.diffusion < 0:
            raise ValueError("diffusion must be non-negative")
        if self.branching_rate < 0:
            raise ValueError("branching_rate must be non-negative")
        if self.x0 <= self.boundary:
            raise ValueError("x0 must start above boundary")


def simulate_single_run(config: SimulationConfig, rng: random.Random) -> dict[str, float | int]:
    config.validate()
    positions = [config.x0]
    sqrt_step = math.sqrt(2.0 * config.diffusion * config.dt)
    branch_prob = min(1.0, config.branching_rate * config.dt)

    resets = 0
    max_population = 1
    steps = int(config.total_time / config.dt)

    for _ in range(steps):
        next_positions: list[float] = []
        reset_triggered = False

        for x in positions:
            x_next = x + config.drift * config.dt + sqrt_step * rng.gauss(0.0, 1.0)

            if x_next <= config.boundary:
                reset_triggered = True
                break

            next_positions.append(x_next)
            if rng.random() < branch_prob:
                next_positions.append(x_next)

        if reset_triggered:
            resets += 1
            positions = [config.x0]
            continue

        positions = next_positions or [config.x0]
        if len(positions) > max_population:
            max_population = len(positions)

    return {
        "final_population": len(positions),
        "resets": resets,
        "max_population": max_population,
    }


def simulate_ensemble(config: SimulationConfig, runs: int, seed: int = 0) -> dict[str, float]:
    if runs <= 0:
        raise ValueError("runs must be positive")

    rng = random.Random(seed)
    totals = {"final_population": 0.0, "resets": 0.0, "max_population": 0.0}

    for _ in range(runs):
        stats = simulate_single_run(config, rng)
        for key in totals:
            totals[key] += float(stats[key])

    return {
        "runs": float(runs),
        "mean_final_population": totals["final_population"] / runs,
        "mean_resets": totals["resets"] / runs,
        "mean_max_population": totals["max_population"] / runs,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate branching diffusion under first-passage resetting"
    )
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--total-time", type=float, default=10.0)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--diffusion", type=float, default=1.0)
    parser.add_argument("--drift", type=float, default=0.0)
    parser.add_argument("--branching-rate", type=float, default=0.25)
    parser.add_argument("--x0", type=float, default=1.0)
    parser.add_argument("--boundary", type=float, default=0.0)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    config = SimulationConfig(
        total_time=args.total_time,
        dt=args.dt,
        diffusion=args.diffusion,
        drift=args.drift,
        branching_rate=args.branching_rate,
        x0=args.x0,
        boundary=args.boundary,
    )
    results = simulate_ensemble(config=config, runs=args.runs, seed=args.seed)
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
