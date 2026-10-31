import unittest
from unittest.mock import patch
from prime_audit import hook

class HookInlineSimulationTests(unittest.TestCase):
    def event(self):
        return {"toolName": "view", "toolArgs": {"path": "README.md"}}

    def test_allow_has_verified_simulation_receipt(self):
        result = hook.decision(self.event())
        self.assertEqual(result["permissionDecision"], "allow")
        self.assertEqual(len(result["_simulation_receipt"]), 64)

    def test_simulation_exception_fails_closed(self):
        with patch.object(hook, "simulate_operation", side_effect=RuntimeError("offline")):
            self.assertEqual(hook.decision(self.event())["permissionDecision"], "deny")

    def test_bad_simulation_receipt_fails_closed(self):
        bad = {"decision": "READY_FOR_BOUNDED_REVIEW", "executed": False, "receipt": {"sha256": "0" * 64}}
        with patch.object(hook, "simulate_operation", return_value=bad):
            self.assertEqual(hook.decision(self.event())["permissionDecision"], "deny")

    def test_review_required_fails_closed(self):
        from prime_audit.engine import receipt
        with patch.object(hook, "simulate_operation", return_value=receipt({"decision": "REVIEW_REQUIRED", "executed": False})):
            self.assertEqual(hook.decision(self.event())["permissionDecision"], "deny")

if __name__ == "__main__":
    unittest.main()
