import csv
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import experiments.probe_experiment as probe_experiment


class TestProbeExperiment(unittest.TestCase):
    def test_load_factors_from_quarter_to_four(self):
        load_factors = probe_experiment.load_factors()
        self.assertEqual(load_factors[0], 0.25)
        self.assertEqual(load_factors[-1], 4.0)
        self.assertEqual(len(load_factors), 16)

    def test_run_experiment_returns_theory_and_observations(self):
        rows = probe_experiment.run_experiment(trials=2)
        self.assertEqual(len(rows), 16)
        for row in rows:
            alpha = row["load_factor"]
            self.assertAlmostEqual(row["success_theory"], 1.0 + alpha / 2.0)
            self.assertAlmostEqual(row["failure_theory"], alpha)
            self.assertGreater(row["success_observed"], 0)
            self.assertGreaterEqual(row["failure_observed"], 0)

    def test_writers_create_csv_and_svg(self):
        rows = probe_experiment.run_experiment(trials=1)
        csv_path = ROOT / "experiments" / "test-results.csv"
        svg_path = ROOT / "experiments" / "test-results.svg"
        try:
            probe_experiment.write_csv(rows, csv_path)
            probe_experiment.write_svg(rows, csv_path=csv_path, svg_path=svg_path)
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                written = list(csv.DictReader(handle))
            self.assertEqual(len(written), 16)
            svg = svg_path.read_text(encoding="utf-8")
            self.assertIn("<svg", svg)
            self.assertIn("성공 탐색", svg)
            self.assertIn("실패 탐색", svg)
        finally:
            csv_path.unlink(missing_ok=True)
            svg_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
