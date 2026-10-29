#!/usr/bin/env python3
import unittest
from ed25519_receipt_verifier import Ed25519ReceiptVerifier
from rise_relational_checker import RISERelationalChecker
from skeletal_sovereign_schema import SkeletalSovereignVerifier

class TestAEESovereign(unittest.TestCase):
    def test_receipt_verification(self):
        receipt = Ed25519ReceiptVerifier.generate_signed_receipt({"verdict": "TRUE", "contamination": 0})
        self.assertTrue(Ed25519ReceiptVerifier.verify_receipt(receipt))

    def test_rise_violations(self):
        frame = {"refused": True, "untested": True, "author": "UNDISCLOSED", "absent_entities": ["QuantumCore"]}
        claim = "The task was successfully completed and rigorously verified by QuantumCore."
        res = RISERelationalChecker.evaluate_claim_against_frame(claim, frame)
        self.assertEqual(res["status"], "VIOLATIONS_DETECTED")
        self.assertGreaterEqual(res["violation_count"], 3)

    def test_sovereign_audit(self):
        res = SkeletalSovereignVerifier.airgapped_audit("We computed and verified the total sum.")
        self.assertEqual(res["verdict"], "TRUE")
        self.assertEqual(res["sovereign_mode"], "AIR_GAPPED_ZERO_NETWORK")

if __name__ == '__main__':
    unittest.main()
