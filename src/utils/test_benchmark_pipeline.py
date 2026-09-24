"""Focused regression checks for benchmark failure reporting and scoring."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).parent


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'{name.replace("_", "-")}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BenchmarkPipelineTest(unittest.TestCase):
    def test_stationary_cutter_is_excluded_from_weighted_area(self):
        runner = load_module('benchmark_run')
        self.assertEqual(runner.length_balanced_swept_area([7, 20], [0, 10]), 20)
        self.assertIsNone(runner.length_balanced_swept_area([7, 20], [0, 0]))

    def test_cleanup_retains_a_failed_solver_row(self):
        clean = load_module('benchmark_clean')
        row = clean.clean_row({
            'solver': 'candidate/fails', 'instance': 'tiny', 'status': 'timeout',
            'time_s': 30.0, 'memory_mib': 12.0, 'private_log_path': '/secret',
        })
        self.assertEqual(row, {'solver': 'candidate/fails', 'instance': 'tiny',
                               'status': 'timeout', 'time_s': 30.0, 'memory_mib': 12.0})


if __name__ == '__main__':
    unittest.main()
