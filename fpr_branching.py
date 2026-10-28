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
    lattice_step: float = 0.1
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
        if self.lattice_step <= 0:
            raise ValueError("lattice_step must be positive")
        if self.diffusion < 0:
            raise ValueError("diffusion must be non-negative")
        if self.branching_rate < 0:
            raise ValueError("branching_rate must be non-negative")
        if self.x0 <= self.boundary:
            raise ValueError("x0 must start above boundary")


def _gillespie_rates(config: SimulationConfig) -> tuple[float, float, float]:
    diffusion_rate = config.diffusion / (config.lattice_step**2)
    drift_right = max(0.0, config.drift) / config.lattice_step
    drift_left = max(0.0, -config.drift) / config.lattice_step
    left_rate = diffusion_rate + drift_left
    right_rate = diffusion_rate + drift_right
    return left_rate, right_rate, config.branching_rate


def _start_site(config: SimulationConfig) -> int:
    return max(1, int(math.ceil((config.x0 - config.boundary) / config.lattice_step)))


def _run_gillespie(
    config: SimulationConfig,
    rng: random.Random,
    *,
    sample_times: list[float] | None = None,
) -> dict[str, float | int | list[int] | list[float]]:
    config.validate()
    left_rate, right_rate, branch_rate = _gillespie_rates(config)
    total_particle_rate = left_rate + right_rate + branch_rate
    particles = [_start_site(config)]
    resets = 0
    max_population = 1
    t = 0.0
    reset_times: list[float] = []

    sampled_population: list[int] = []
    sample_index = 0
    if sample_times is not None:
        sampled_population.append(len(particles))
        sample_index = 1

    while t < config.total_time:
        n = len(particles)
        if n > max_population:
            max_population = n

        if total_particle_rate <= 0 or n <= 0:
            t = config.total_time
            break

        tau = rng.expovariate(n * total_particle_rate)
        event_time = t + tau

        if sample_times is not None:
            while (
                sample_index < len(sample_times)
                and sample_times[sample_index] < event_time
            ):
                sampled_population.append(n)
                sample_index += 1

        if event_time > config.total_time:
            t = config.total_time
            break

        t = event_time
        i = rng.randrange(n)
        u = rng.random() * total_particle_rate

        if u < left_rate:
            if particles[i] <= 1:
                particles = [_start_site(config)]
                resets += 1
                reset_times.append(t)
            else:
                particles[i] -= 1
        elif u < left_rate + right_rate:
            particles[i] += 1
        else:
            particles.append(particles[i])

        if sample_times is not None:
            while (
                sample_index < len(sample_times)
                and sample_times[sample_index] <= t
            ):
                sampled_population.append(len(particles))
                sample_index += 1

    if sample_times is not None:
        while sample_index < len(sample_times):
            sampled_population.append(len(particles))
            sample_index += 1

    return {
        "final_population": len(particles),
        "resets": resets,
        "max_population": max_population,
        "reset_times": reset_times,
        "population_samples": sampled_population,
    }


def simulate_single_run(config: SimulationConfig, rng: random.Random) -> dict[str, float | int]:
    stats = _run_gillespie(config, rng)
    return {
        "final_population": int(stats["final_population"]),
        "resets": int(stats["resets"]),
        "max_population": int(stats["max_population"]),
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


def simulate_population_trajectory(
    config: SimulationConfig, rng: random.Random
) -> dict[str, list[float] | list[int]]:
    steps = int(config.total_time / config.dt)
    times = [i * config.dt for i in range(steps + 1)]
    stats = _run_gillespie(config, rng, sample_times=times)
    return {
        "times": times,
        "population": list(stats["population_samples"]),
        "reset_times": list(stats["reset_times"]),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simulate branching diffusion under first-passage resetting"
    )
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--total-time", type=float, default=10.0)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--lattice-step", type=float, default=0.1)
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
        lattice_step=args.lattice_step,
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
