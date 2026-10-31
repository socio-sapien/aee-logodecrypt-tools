import tempfile
import unittest
from pathlib import Path
from prime_audit.role_index_repair import reconcile, canonical_index

class RoleIndexRepairTest(unittest.TestCase):
    def test_real_repair_and_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root/'.prime').mkdir()
            f = root/'.prime/role-index.json'; f.write_text('{"outdated": true}\n')
            self.assertEqual(reconcile(root)['status'], 'verified')
            self.assertEqual(f.read_text(), canonical_index())
            self.assertEqual(reconcile(root)['status'], 'already_current')
    def test_missing_refused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): reconcile(d)
