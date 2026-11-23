"""Offline demonstration smoke test; output must not overwrite existing files."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'demonstrations/synthetic-prime-battery/run_battery.py'

class SyntheticBatteryDemoTest(unittest.TestCase):
    def test_run_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / 'result.json'
            env = dict(os.environ, PYTHONPATH=str(ROOT))
            command = [sys.executable, str(SCRIPT), '--output', str(output)]
            first = subprocess.run(command, cwd=d, env=env, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            data = json.loads(output.read_text(encoding='utf-8'))
            self.assertTrue(data['receipt_verified'])
            self.assertFalse(data['local_preflight']['executed'])
            roles = data['seven_offline_fixture_scenarios']['roles']
            self.assertEqual(len(roles), 7)
            self.assertTrue(all(x['passed'] for x in roles))
            original = output.read_bytes()
            second = subprocess.run(command, cwd=d, env=env, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), original)
