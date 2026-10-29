#!/usr/bin/env python3
import unittest
from aee_master_engine import AEEMasterEngine
from skeletal_enterprise_schema import SkeletalLogoDecrypt
from forensic_autopsy_29device import ForensicAutopsy29Device

class TestAEEEnterprise(unittest.TestCase):
    def test_master_engine_full(self):
        engine = AEEMasterEngine()
        specimen = "We computed the total sum and verified the result. However, the system potentially evolves synergies."
        res = engine.process_full_diagnostic(specimen)
        self.assertIn("audit_record", res)
        self.assertIn("decryption_payload", res)
        self.assertIn("metadata_forensics", res)
        self.assertEqual(res["audit_record"]["VERDICT"], "OBJECTIVE")

    def test_logodecrypt_transforms(self):
        res = SkeletalLogoDecrypt.audit_enterprise_record("There is no hidden motive in this protocol.")
        self.assertIn("ASSERTION: [HIDDEN MOTIVE IN THIS PROTOCOL]", res["apophasis_payloads"][0])
        self.assertGreater(res["shannon_entropy"], 0.0)

    def test_29device_autopsy(self):
        autopsy = ForensicAutopsy29Device()
        sweep = autopsy.run_full_sweep()
        self.assertEqual(sweep["devices_audited"], 29)
        self.assertEqual(sweep["system_verdict"], "VERIFIED_ACTIVE")

if __name__ == '__main__':
    unittest.main()
