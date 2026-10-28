from __future__ import annotations

import argparse
import random
from pathlib import Path

from fpr_branching import SimulationConfig, simulate_population_trajectory


def build_trajectory_svg(
    times: list[float],
    population: list[int],
    reset_times: list[float],
    *,
    width: int = 900,
    height: int = 360,
) -> str:
    if not times or not population or len(times) != len(population):
        raise ValueError("times and population must be non-empty and same length")

    max_time = max(times)
    max_pop = max(population)
    min_x, min_y = 70, 40
    max_x, max_y = width - 30, height - 50

    def sx(t: float) -> float:
        if max_time == 0:
            return float(min_x)
        return min_x + (max_x - min_x) * (t / max_time)

    def sy(p: int) -> float:
        if max_pop <= 1:
            return float(max_y)
        return max_y - (max_y - min_y) * ((p - 1) / (max_pop - 1))

    line_points = " ".join(f"{sx(t):.2f},{sy(p):.2f}" for t, p in zip(times, population))
    reset_lines = "\n".join(
        f'<line x1="{sx(t):.2f}" y1="{min_y}" x2="{sx(t):.2f}" y2="{max_y}" stroke="#ef4444" stroke-dasharray="5,5" stroke-width="1.5" />'
        for t in reset_times
    )

    tick_values = [1, max(1, max_pop // 2), max_pop]
    tick_values = sorted(set(tick_values))
    y_ticks = "\n".join(
        f'<text x="18" y="{sy(v) + 5:.2f}" font-size="12" fill="#374151">{v}</text>'
        for v in tick_values
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white" />
  <text x="{width/2:.1f}" y="24" text-anchor="middle" font-size="18" fill="#111827">Example: Branching under First-Passage Resetting</text>

  <line x1="{min_x}" y1="{min_y}" x2="{min_x}" y2="{max_y}" stroke="#111827" stroke-width="2" />
  <line x1="{min_x}" y1="{max_y}" x2="{max_x}" y2="{max_y}" stroke="#111827" stroke-width="2" />

  <text x="{width/2:.1f}" y="{height-12}" text-anchor="middle" font-size="13" fill="#111827">time</text>
  <text x="24" y="{height/2:.1f}" text-anchor="middle" font-size="13" fill="#111827" transform="rotate(-90 24 {height/2:.1f})">population size</text>

  {y_ticks}

  {reset_lines}
  <polyline points="{line_points}" fill="none" stroke="#2563eb" stroke-width="2.2" />
  <circle cx="{sx(times[0]):.2f}" cy="{sy(population[0]):.2f}" r="3" fill="#2563eb" />

  <rect x="{width-260}" y="40" width="220" height="58" fill="#f9fafb" stroke="#d1d5db" />
  <line x1="{width-246}" y1="58" x2="{width-206}" y2="58" stroke="#2563eb" stroke-width="2.2" />
  <text x="{width-196}" y="62" font-size="12" fill="#111827">population</text>
  <line x1="{width-246}" y1="82" x2="{width-206}" y2="82" stroke="#ef4444" stroke-dasharray="5,5" stroke-width="1.5" />
  <text x="{width-196}" y="86" font-size="12" fill="#111827">reset events</text>
</svg>
'''


def generate_example_figure(output: Path, seed: int = 11) -> Path:
    config = SimulationConfig(total_time=8.0, dt=0.05, diffusion=0.8, drift=0.02, branching_rate=0.8)
    trajectory = simulate_population_trajectory(config, random.Random(seed))
    svg = build_trajectory_svg(
        times=trajectory["times"],
        population=trajectory["population"],
        reset_times=trajectory["reset_times"],
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an example first-passage-resetting figure")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/home/runner/work/branchingphage/branchingphage/figures/example_trajectory.svg"),
    )
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()

    path = generate_example_figure(args.output, seed=args.seed)
    print(path)


if __name__ == "__main__":
    main()
