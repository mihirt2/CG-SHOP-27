"""Focused regression checks for benchmark failure reporting and scoring."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parent


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'{name.replace("_", "-")}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BenchmarkReportTest(unittest.TestCase):
    def test_stationary_cutter_is_excluded_from_weighted_area(self):
        runner = load_module('benchmark_run')
        self.assertEqual(runner.length_balanced_swept_area([7, 20], [0, 10]), 20)
        self.assertIsNone(runner.length_balanced_swept_area([7, 20], [0, 0]))

    def test_report_retains_a_failed_solver_row(self):
        report = load_module('benchmark_report')
        row = report.public_row({
            'solver': 'candidate/fails', 'instance': 'tiny', 'status': 'timeout',
            'time_s': 30.0, 'memory_mib': 12.0, 'private_log_path': '/secret',
        })
        self.assertEqual(row, {'solver': 'candidate/fails', 'instance': 'tiny',
                               'status': 'timeout', 'time_s': 30.0, 'memory_mib': 12.0})

    def test_failed_solver_run_produces_a_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            instances, solver, dumps, report = (root / name for name in ('instances', 'solver', 'dumps', 'report'))
            instances.mkdir()
            solver.mkdir()
            (instances / 'tiny.instance.json').write_text(json.dumps({
                'instance_uid': 'tiny', 'number_of_cutters': 1,
                'region_to_cover': {
                    'outer_boundary': {'x': [0, 1, 1, 0], 'y': [0, 0, 1, 1]},
                    'inner_boundaries': [],
                },
            }))
            (solver / 'main.py').write_text('raise SystemExit(2)\n')
            (solver / 'pyproject.toml').write_text(
                '[project]\nname = "fails"\nversion = "0"\nrequires-python = ">=3.14"\n')
            failed = subprocess.run([
                sys.executable, ROOT / 'benchmark-run.py', instances,
                '--solver-root', f'candidate={root}', '--solver', 'solver',
                '--timeout', '1', '--output', dumps,
            ])
            self.assertNotEqual(failed.returncode, 0)
            manifest = root / 'manifest.json'
            manifest.write_text('[]\n')
            subprocess.run([sys.executable, ROOT / 'benchmark-report.py', '--dumps', dumps,
                            '--manifest', manifest, '--output', report], check=True)
            rows = json.loads((report / 'results.json').read_text())
            self.assertEqual(len(rows), 1)
            self.assertNotEqual(rows[0]['status'], 'valid')
            self.assertTrue((report / 'report.md').is_file())


if __name__ == '__main__':
    unittest.main()
