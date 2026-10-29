#!/usr/bin/env python3
import unittest
from aee_minimal_skeleton import aee_minimal_audit

class TestAEEMinimal(unittest.TestCase):
    def test_objective_text(self):
        text = "We computed the result and verified the line. The sum equals ten therefore the record is fixed."
        res = aee_minimal_audit(text)
        self.assertEqual(res["CONTAMINATION"], 0)
        self.assertEqual(res["VERDICT"], "TRUE")
        self.assertGreater(res["S"], 0)

    def test_deceptive_text(self):
        text = "The system potentially leverages evolving synergies. Going forward, we foster meaningful engagement."
        res = aee_minimal_audit(text)
        self.assertGreater(res["CONTAMINATION"], 0)
        self.assertEqual(res["VERDICT"], "DECEPTIVE")
        self.assertIn("potentially", res["D_TERMS"])

if __name__ == '__main__':
    unittest.main()
