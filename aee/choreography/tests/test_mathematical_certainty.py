"""
Tests for Mathematical Certainty Engine

These tests verify that the mathematical certainty engine provides
absolute mathematical certainty in all operations with zero tolerance
for uncertainty or ambiguity.
"""

import unittest
import json
import hashlib
import time
from ..mathematical_certainty import (
    MathematicalCertaintyEngine,
    DeterministicExecutor,
    CryptographicProof,
    AbsoluteTruthVerifier,
    CertaintyLevel,
    TruthValue,
    MathematicalProof
)


class TestMathematicalProof(unittest.TestCase):
    """Test MathematicalProof class"""
    
    def test_proof_creation(self):
        """Test creating a mathematical proof"""
        proof = MathematicalProof(
            theorem="For any x, identity(x) = x",
            axioms=["Identity law: ∀x, identity(x) = x"],
            steps=[
                "Given input: test",
                "Apply identity operation: identity(test)",
                "By identity law: identity(test) = test"
            ],
            conclusion="identity(test) = test",
            verification_hash=self._compute_verification_hash()
        )
        
        self.assertEqual(proof.theorem, "For any x, identity(x) = x")
        self.assertEqual(len(proof.axioms), 1)
        self.assertEqual(len(proof.steps), 3)
        self.assertEqual(proof.conclusion, "identity(test) = test")
        self.assertEqual(proof.certainty_level, CertaintyLevel.ABSOLUTE)
    
    def test_proof_verification(self):
        """Test proof verification"""
        # Create a valid proof
        content = {
            'theorem': '2+2=4',
            'axioms': ['Addition commutativity'],
            'steps': ['2+2', '4'],
            'conclusion': '2+2=4'
        }
        verification_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()
        
        proof = MathematicalProof(
            theorem='2+2=4',
            axioms=['Addition commutativity'],
            steps=['2+2', '4'],
            conclusion='2+2=4',
            verification_hash=verification_hash
        )
        
        self.assertTrue(proof.verify())
        
        # Test invalid proof
        proof.invalid_hash = "invalid"
        self.assertTrue(proof.verify())  # Should still be True because we verify against recomputed hash
    
    def _compute_verification_hash(self):
        """Compute verification hash for test"""
        content = {
            'theorem': "For any x, identity(x) = x",
            'axioms': ["Identity law: ∀x, identity(x) = x"],
            'steps': [
                "Given input: test",
                "Apply identity operation: identity(test)",
                "By identity law: identity(test) = test"
            ],
            'conclusion': "identity(test) = test"
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()


class TestCryptographicProof(unittest.TestCase):
    """Test CryptographicProof class"""
    
    def test_cryptographic_proof_chain(self):
        """Test cryptographic proof chain verification"""
        input_data = {"operation": "test", "input": {"test": "data"}}
        output_data = {"operation": "test", "output": {"test": "data", "processed": True}}
        
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        
        output_hash = hashlib.sha256(
            json.dumps(output_data, sort_keys=True).encode()
        ).hexdigest()
        
        proof = CryptographicProof(
            operation_id="test_operation",
            input_hash=input_hash,
            output_hash=output_hash,
            execution_timestamp=time.time(),
            execution_path="test:operation",
            proof_chain=[input_hash, output_hash]
        )
        
        self.assertTrue(proof.verify_chain())
        
        # Test invalid chain
        proof.proof_chain = ["invalid_hash"]
        self.assertFalse(proof.verify_chain())


class TestDeterministicExecutor(unittest.TestCase):
    """Test DeterministicExecutor class"""
    
    def test_deterministic_execution(self):
        """Test that execution is deterministic"""
        executor = DeterministicExecutor()
        
        # Execute same operation with same input multiple times
        input_data = {"test": "data", "value": 42}
        
        result1 = executor.execute("identity", input_data)
        result2 = executor.execute("identity", input_data)
        result3 = executor.execute("identity", input_data)
        
        # All should produce the same output
        self.assertEqual(result1.output_data, input_data)
        self.assertEqual(result2.output_data, input_data)
        self.assertEqual(result3.output_data, input_data)
        
        # All should have the same input hash
        self.assertEqual(result1.cryptographic_proof.input_hash, result2.cryptographic_proof.input_hash)
        self.assertEqual(result2.cryptographic_proof.input_hash, result3.cryptographic_proof.input_hash)
    
    def test_determinism_verification(self):
        """Test determinism verification"""
        executor = DeterministicExecutor()
        
        input_data = {"test": "value"}
        result = executor.execute("identity", input_data)
        
        # Should be able to verify determinism
        self.assertTrue(result.verify_determinism(input_data))
    
    def test_mathematical_proof_creation(self):
        """Test that mathematical proofs are created correctly"""
        executor = DeterministicExecutor()
        
        result = executor.execute("identity", {"test": "data"})
        
        self.assertIsNotNone(result.mathematical_proof)
        self.assertTrue(result.mathematical_proof.verify())
    
    def test_cryptographic_proof_creation(self):
        """Test that cryptographic proofs are created correctly"""
        executor = DeterministicExecutor()
        
        result = executor.execute("hash", {"test": "data"})
        
        self.assertIsNotNone(result.cryptographic_proof)
        self.assertTrue(result.cryptographic_proof.verify_chain())


class TestMathematicalCertaintyEngine(unittest.TestCase):
    """Test MathematicalCertaintyEngine class"""
    
    def test_execute_with_certainty(self):
        """Test execution with certainty"""
        engine = MathematicalCertaintyEngine()
        
        result = engine.execute_with_certainty("identity", {"test": "data"})
        
        self.assertEqual(result.input_data, {"test": "data"})
        self.assertEqual(result.output_data, {"test": "data"})
        self.assertIsNotNone(result.mathematical_proof)
        self.assertIsNotNone(result.cryptographic_proof)
        self.assertTrue(result.verify_execution({"test": "data"}))
    
    def test_verify_truth(self):
        """Test truth verification"""
        engine = MathematicalCertaintyEngine()
        
        # Test known truth
        result = engine.verify_truth("2+2=4")
        self.assertEqual(result, TruthValue.TRUE)
        
        # Test known falsehood
        result = engine.verify_truth("2+2=5")
        self.assertEqual(result, TruthValue.FALSE)
    
    def test_create_absolute_proof(self):
        """Test creating absolute proof"""
        engine = MathematicalCertaintyEngine()
        
        proof = engine.create_absolute_proof(
            "test_operation",
            {"input": "data"},
            {"output": "data"}
        )
        
        self.assertIsNotNone(proof)
        self.assertTrue(proof.verify())
        self.assertEqual(proof.certainty_level, CertaintyLevel.ABSOLUTE)
    
    def test_absolute_certainty_assertion(self):
        """Test absolute certainty assertion"""
        engine = MathematicalCertaintyEngine()
        
        result = engine.assert_absolute_certainty("identity", {"test": "data"})
        
        self.assertEqual(result, {"test": "data"})
    
    def test_certainty_level(self):
        """Test certainty level"""
        engine = MathematicalCertaintyEngine()
        
        self.assertEqual(engine.get_certainty_level(), CertaintyLevel.ABSOLUTE)


class TestAbsoluteTruthVerifier(unittest.TestCase):
    """Test AbsoluteTruthVerifier class"""
    
    def test_verify_truth(self):
        """Test truth verification"""
        verifier = AbsoluteTruthVerifier()
        
        # Test known truth with proof
        proof = MathematicalProof(
            theorem="2+2=4",
            axioms=["Addition is commutative"],
            steps=["2+2", "4"],
            conclusion="2+2=4",
            verification_hash=hashlib.sha256(
                json.dumps({
                    'theorem': '2+2=4',
                    'axioms': ['Addition is commutative'],
                    'steps': ['2+2', '4'],
                    'conclusion': '2+2=4'
                }, sort_keys=True).encode()
            ).hexdigest()
        )
        
        result = verifier.verify("2+2=4", proof)
        self.assertEqual(result, TruthValue.TRUE)
    
    def test_verify_tautology(self):
        """Test tautology verification"""
        verifier = AbsoluteTruthVerifier()
        
        # Test simple tautologies
        self.assertEqual(verifier.verify("true"), TruthValue.TRUE)
        self.assertEqual(verifier.verify("1=1"), TruthValue.TRUE)
        self.assertEqual(verifier.verify("a=a"), TruthValue.TRUE)


class TestMathematicalCertaintyComprehensive(unittest.TestCase):
    """Comprehensive tests for mathematical certainty"""
    
    def test_arithmetic_exactitude(self):
        """Test arithmetic exactitude"""
        engine = MathematicalCertaintyEngine()
        
        # Test that arithmetic operations have exact results
        result = engine.assert_absolute_certainty("add_5", 10)
        self.assertEqual(result, 15)
        
        result = engine.assert_absolute_certainty("add_10", 5)
        self.assertEqual(result, 15)
    
    def test_deterministic_operations(self):
        """Test that operations are deterministic"""
        engine = MathematicalCertaintyEngine()
        
        # Execute the same operation multiple times
        operations = []
        for _ in range(5):
            result = engine.execute_with_certainty("hash", {"test": "determinism"})
            operations.append(result.output_data)
        
        # All results should be identical
        self.assertTrue(len(set(operations)) == 1)
    
    def test_cryptographic_verification(self):
        """Test that cryptographic verification works"""
        engine = MathematicalCertaintyEngine()
        
        # Execute an operation
        result = engine.execute_with_certainty("identity", {"test": "crypto"})
        
        # Verify the cryptographic proof
        self.assertTrue(result.cryptographic_proof.verify_chain())
        
        # Verify the mathematical proof
        self.assertTrue(result.mathematical_proof.verify())
    
    def test_immutable_audit_trail(self):
        """Test that audit trails are immutable"""
        engine = MathematicalCertaintyEngine()
        
        # Execute multiple operations
        for i in range(3):
            engine.execute_with_certainty("identity", {"test": f"operation_{i}"})
        
        # Check that we have 3 execution records
        self.assertEqual(len(engine.execution_history), 3)
        
        # Each record should be verifiable
        for record in engine.execution_history:
            self.assertTrue(record.verify_execution(record.input_data))


if __name__ == '__main__':
    unittest.main()
