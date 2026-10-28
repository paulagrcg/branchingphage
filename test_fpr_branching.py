import random
import unittest

from fpr_branching import SimulationConfig, simulate_ensemble, simulate_single_run


class FPRBranchingSimulationTests(unittest.TestCase):
    def test_reproducible_single_run_with_seed(self) -> None:
        config = SimulationConfig(total_time=1.0, dt=0.05, diffusion=0.5, branching_rate=0.4)
        first = simulate_single_run(config, random.Random(42))
        second = simulate_single_run(config, random.Random(42))
        self.assertEqual(first, second)

    def test_no_branching_keeps_population_bounded(self) -> None:
        config = SimulationConfig(total_time=0.5, dt=0.01, diffusion=0.2, branching_rate=0.0)
        stats = simulate_single_run(config, random.Random(1))
        self.assertEqual(stats["max_population"], 1)

    def test_ensemble_reproducibility(self) -> None:
        config = SimulationConfig(total_time=1.0, dt=0.02, diffusion=0.5, branching_rate=0.25)
        a = simulate_ensemble(config, runs=50, seed=3)
        b = simulate_ensemble(config, runs=50, seed=3)
        self.assertEqual(a, b)

    def test_negative_drift_produces_resets(self) -> None:
        config = SimulationConfig(
            total_time=0.5,
            dt=0.01,
            lattice_step=0.1,
            diffusion=0.0,
            drift=-2.0,
            branching_rate=0.0,
            x0=0.2,
            boundary=0.0,
        )
        stats = simulate_single_run(config, random.Random(4))
        self.assertGreater(stats["resets"], 0)
        self.assertEqual(stats["final_population"], 1)


if __name__ == "__main__":
    unittest.main()
