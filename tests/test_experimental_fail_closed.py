"""Offline regression checks; no live network or cryptographic certification."""
import importlib.util
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'aee/v4-commercial-suite/04_SOVEREIGN_AIR_GAPPED_PROTOCOL/ed25519_receipt_verifier.py'
B_DIR = ROOT / 'aee/bittensor-experimental'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

receipt = load('receipt_fail_closed', RECEIPT)
sys.path.insert(0, str(B_DIR))
automator = load('automator_fail_closed', B_DIR / 'bittensor_subnet_automator.py')

class FailClosedTests(unittest.TestCase):
    def test_receipt_signing_is_unavailable(self):
        with self.assertRaises(NotImplementedError):
            receipt.Ed25519ReceiptVerifier.generate_signed_receipt({'x': 1})

    def test_all_receipts_fail_closed(self):
        for item in ({}, {'payload': {}, 'payload_sha256': 'x'},
                     {'payload': {'changed': True}, 'payload_sha256': 'x', 'signature_proof': 'bad'}, None):
            with self.subTest(item=item), self.assertRaises(NotImplementedError):
                receipt.Ed25519ReceiptVerifier.verify_receipt(item)

    def test_cli_fails_nonzero(self):
        for path in (RECEIPT, B_DIR / 'bittensor_subnet_automator.py'):
            result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('not implemented', result.stderr.lower())

    def test_missing_package_is_not_connection(self):
        a = automator.BittensorSubnetAutomator()
        a.subtensor = object()
        with patch.dict(sys.modules, {'bittensor': None}):
            self.assertFalse(a.connect_network())
        self.assertIsNone(a.subtensor)
        with self.assertRaises(RuntimeError): a.sync_metagraph()

    def test_connection_exception_does_not_leave_stale_connection(self):
        a = automator.BittensorSubnetAutomator()
        a.subtensor = object()
        fake = types.SimpleNamespace(subtensor=lambda **kw: (_ for _ in ()).throw(RuntimeError('offline')))
        with patch.dict(sys.modules, {'bittensor': fake}):
            self.assertFalse(a.connect_network())
        self.assertIsNone(a.subtensor)

    def test_block_failure_not_connection(self):
        a = automator.BittensorSubnetAutomator()
        c = types.SimpleNamespace(get_current_block=lambda: (_ for _ in ()).throw(RuntimeError('offline')))
        with patch.dict(sys.modules, {'bittensor': types.SimpleNamespace(subtensor=lambda **kw: c)}):
            self.assertFalse(a.connect_network())
        self.assertIsNone(a.subtensor)

    def test_invalid_block_not_connection(self):
        a = automator.BittensorSubnetAutomator()
        for block in (None, False, -1):
            c = types.SimpleNamespace(get_current_block=lambda: block)
            with self.subTest(block=block), patch.dict(sys.modules, {'bittensor': types.SimpleNamespace(subtensor=lambda **kw: c)}):
                self.assertFalse(a.connect_network())
                self.assertIsNone(a.subtensor)

    def test_sync_failure_raises_and_clears_stale_graph(self):
        a = automator.BittensorSubnetAutomator()
        a.metagraph = object()
        a.subtensor = types.SimpleNamespace(metagraph=lambda **kw: (_ for _ in ()).throw(RuntimeError('no graph')))
        with self.assertRaises(RuntimeError): a.sync_metagraph()
        self.assertIsNone(a.metagraph)

    def test_mock_connection_and_sync_success(self):
        a = automator.BittensorSubnetAutomator()
        graph = types.SimpleNamespace(uids=types.SimpleNamespace(tolist=lambda: [4]), hotkeys=['key'], S=[1], I=[2], E=[3], sync=lambda: None)
        conn = types.SimpleNamespace(get_current_block=lambda: 99, metagraph=lambda **kw: graph)
        with patch.dict(sys.modules, {'bittensor': types.SimpleNamespace(subtensor=lambda **kw: conn)}):
            self.assertTrue(a.connect_network())
            self.assertEqual(a.sync_metagraph(), [{'uid': 4, 'hotkey': 'key', 'stake': 1., 'incentive': 2., 'emission': 3.}])

    def test_fabricated_payload_loop_unavailable(self):
        a = automator.BittensorSubnetAutomator()
        with self.assertRaises(NotImplementedError): a.run_automated_validation_loop()

if __name__ == '__main__': unittest.main()
