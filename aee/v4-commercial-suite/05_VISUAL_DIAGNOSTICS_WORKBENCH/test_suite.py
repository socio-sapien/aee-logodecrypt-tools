#!/usr/bin/env python3
import os
import unittest

class TestAEEVisual(unittest.TestCase):
    def test_html_files_exist(self):
        for name in ['oracle_app_ui.html', 'oraclepal_standalone.html', 'skeletal_web_schema.html']:
            path = os.path.join(os.path.dirname(__file__), name)
            self.assertTrue(os.path.exists(path), f"Missing {name}")
            self.assertGreater(os.path.getsize(path), 100)

    def test_cli_ui_exists(self):
        path = os.path.join(os.path.dirname(__file__), 'aee_fidelity_cli_ui.py')
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 5000)

if __name__ == '__main__':
    unittest.main()
