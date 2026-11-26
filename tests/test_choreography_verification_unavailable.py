"""Offline regression of disabled verification paths, not a security audit.

The package has separate import defects. A temporary copy is patched solely to
run the exact verification methods from this checkout; the public import is not fixed.
"""
import importlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class VerificationUnavailable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copytree(ROOT / 'aee' / 'choreography', root / 'aee' / 'choreography')
        init = root / 'aee' / 'choreography' / '__init__.py'
        text = init.read_text()
        assert '    TaskSequencer,\n' in text and "    'TaskSequencer',\n" in text
        init.write_text(text.replace('    TaskSequencer,\n', '').replace("    'TaskSequencer',\n", ''))
        prime = root / 'aee' / 'choreography' / 'prime_integration.py'
        text = prime.read_text()
        assert '    AuditSeverity,\n    ComplianceLevel' in text
        prime.write_text(text.replace('    AuditSeverity,\n    ComplianceLevel', '    AuditSeverity,\n    AuditStatus,\n    ComplianceLevel'))
        sys.path.insert(0, str(root))
        cls.math = importlib.import_module('aee.choreography.mathematical_certainty')
        cls.orch = importlib.import_module('aee.choreography.orchestration_engine')
        assert str(root) in cls.math.__file__ and str(root) in cls.orch.__file__

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(cls.tmp.name)
        for name in list(sys.modules):
            if name == 'aee' or name.startswith('aee.choreography'):
                del sys.modules[name]
        cls.tmp.cleanup()

    def test_chain_rejects_fabricated_and_empty(self):
        m = self.math
        import hashlib
        h = hashlib.sha256(b'arbitrary').hexdigest()
        for chain in ([], ['arbitrary']):
            with self.assertRaises(NotImplementedError):
                m.CryptographicProof('fake', h, h, 0, 'fake', chain).verify_chain()

    def test_determinism_does_not_accept_changed_output(self):
        m = self.math
        result = m.DeterministicExecutor().execute('custom', {'x': 1})
        result.output_data = {'tampered': True}
        with self.assertRaises(NotImplementedError): result.verify_determinism({'x': 1})

    def test_engine_never_certifies_result(self):
        m = self.math
        engine = m.MathematicalCertaintyEngine()
        result = engine.execute_with_certainty('identity', {'x': 1})
        for data in ({'x': 1}, {'x': 2}):
            with self.assertRaises(NotImplementedError): engine.verify_execution(result, data)

    def test_absolute_assertion_refuses_before_executing(self):
        engine = self.math.MathematicalCertaintyEngine()
        engine.execute_with_certainty = lambda *args, **kwargs: self.fail('must not execute')
        with self.assertRaises(NotImplementedError): engine.assert_absolute_certainty('identity', {})

    def test_orchestration_absent_and_fabricated_evidence(self):
        m = self.orch
        class Fake:
            def verify_chain(self): return True
            def verify(self): return True
        for proof, audit in ((None, None), (Fake(), Fake())):
            r = m.OrchestratedResult('r', 'i', m.InitiativeType.TASK, 'completed', {'x': 1}, 0,
                                     cryptographic_proof=proof, audit_result=audit)
            with self.assertRaises(NotImplementedError): r.verify()

    def test_manager_empty_and_nonempty_cannot_claim_certainty(self):
        manager = self.orch.InitiativeManager.__new__(self.orch.InitiativeManager)
        for results in ({}, {'fake': object()}):
            manager.results = results
            with self.assertRaises(NotImplementedError): manager.verify_all_results()

    def test_mathematical_optimization_refuses_without_mutating_result(self):
        m = self.orch
        controller = m.AutomationController.__new__(m.AutomationController)
        class FakeProof:
            def verify(self): return True
        for proof in (None, FakeProof()):
            output = {'value': 'sample'}
            result = m.OrchestratedResult('r', 'i', m.InitiativeType.TASK,
                                          'completed', output, 0, mathematical_proof=proof)
            with self.assertRaises(NotImplementedError):
                controller._mathematical_optimization(result)
            self.assertEqual(output, {'value': 'sample'})

    def test_controller_refuses_before_invoking_manager(self):
        m = self.orch
        controller = m.AutomationController.__new__(m.AutomationController)
        class Manager:
            def execute_initiative(self, *args):
                raise AssertionError('manager must not be invoked')
        controller.initiative_manager = Manager()
        for strategy in m.OptimizationStrategy:
            controller.optimization_strategy = strategy
            with self.assertRaises(NotImplementedError):
                controller.execute_initiative('example', {})

    def test_literal_truth_verifier_stays_bounded(self):
        m = self.math
        v = m.AbsoluteTruthVerifier()
        self.assertIs(v.verify('2+2=4'), m.TruthValue.TRUE)
        self.assertIs(v.verify('1+1=2'), m.TruthValue.UNDEFINED)

if __name__ == '__main__': unittest.main()
