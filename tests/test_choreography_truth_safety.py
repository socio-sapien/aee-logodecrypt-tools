"""Limited offline regression tests; not a security audit or proof engine."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'aee/choreography/mathematical_certainty.py'
spec = importlib.util.spec_from_file_location('choreography_truth_safety', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class TruthSafety(unittest.TestCase):
    def setUp(self):
        self.verifier = module.AbsoluteTruthVerifier()

    def test_assertion_does_not_execute_code(self):
        with tempfile.TemporaryDirectory() as d:
            marker = Path(d) / 'marker'
            assertion = "__import__('pathlib').Path(" + repr(str(marker)) + ").write_text('test')=4"
            self.assertIs(self.verifier.verify(assertion), module.TruthValue.UNDEFINED)
            self.assertFalse(marker.exists())

    def test_self_hashed_unrelated_proof_does_not_prove_assertion(self):
        content = {'theorem':'unrelated', 'axioms':[], 'steps':[], 'conclusion':'unrelated'}
        digest = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
        proof = module.MathematicalProof(verification_hash=digest, **content)
        self.assertTrue(proof.verify())  # only a checksum match, not proof of truth
        self.assertIs(self.verifier.verify('1=0', proof), module.TruthValue.FALSE)
        self.assertIs(self.verifier.verify('an unsupported assertion', proof), module.TruthValue.UNDEFINED)

    def test_known_literals_and_unsupported_expressions(self):
        for value in ('true', '1=1', 'a=a', 'x=x', '2+2=4'):
            self.assertIs(self.verifier.verify(value), module.TruthValue.TRUE)
        for value in ('false', '1=0', 'a≠a', '2+2=5'):
            self.assertIs(self.verifier.verify(value), module.TruthValue.FALSE)
        for value in ('3+3=6', '__import__("os")=0', '', 'a'*257, None):
            self.assertIs(self.verifier.verify(value), module.TruthValue.UNDEFINED)

    def test_input_cache_is_not_a_proof_source(self):
        self.verifier.known_truths['1=0'] = module.TruthValue.TRUE
        self.assertIs(self.verifier.verify('1=0'), module.TruthValue.FALSE)

if __name__ == '__main__':
    unittest.main()
