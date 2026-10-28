import random
import unittest

from fpr_branching import SimulationConfig, simulate_population_trajectory
from make_example_figure import build_trajectory_svg


class ExampleFigureTests(unittest.TestCase):
    def test_trajectory_has_expected_lengths(self) -> None:
        config = SimulationConfig(total_time=1.0, dt=0.1, diffusion=0.4, branching_rate=0.2)
        trajectory = simulate_population_trajectory(config, random.Random(3))
        self.assertEqual(len(trajectory["times"]), 11)
        self.assertEqual(len(trajectory["population"]), 11)

    def test_svg_contains_expected_elements(self) -> None:
        svg = build_trajectory_svg([0.0, 0.5, 1.0], [1, 2, 1], [0.5])
        self.assertIn("<svg", svg)
        self.assertIn("<polyline", svg)
        self.assertIn("reset events", svg)


if __name__ == "__main__":
    unittest.main()
