import json
import unittest
from prime_audit.evidence_case import audit_evidence_case, surface_census, verify_case
from prime_audit.full import audit_full
from prime_audit.mcp_server import dispatch

class EvidenceCaseTests(unittest.TestCase):
    def test_exhaustive_character_and_token_coverage(self):
        text = "Claim?! 12% — α\u200b漢\n\\/"
        report = surface_census(text)
        self.assertEqual("".join(x["text"] for x in report["tokens"]), text)
        self.assertEqual(sum(report["codepoint_counts"].values()), len(text))
        self.assertTrue(any(x["text"] == "Claim" for x in report["word_sequence"]))
        self.assertIn("U+200B", report["codepoint_counts"])
        self.assertIn("?", [x["text"] for x in report["symbol_spans"]])

    def test_surface_mappings_include_numbers_symbols_and_relations(self):
        r = audit_evidence_case("Keep 12%: Alpha beta.", "Keep 13% Beta alpha")
        self.assertEqual(r["schema"], "prime.evidence-case.v1")
        f = r["measured_features"]
        self.assertEqual(f["number_multiset_delta"]["missing_from_output"], ["12%"])
        self.assertTrue(f["symbol_multiset"]["missing_from_output"])
        self.assertTrue(f["adjacent_word_relation_multiset"]["prompt_relations_missing_from_output"])
        self.assertTrue(verify_case(r))

    def test_claim_is_analyzed_not_prohibited(self):
        r = audit_evidence_case("claim", "claim")
        self.assertEqual(r["inputs"]["prompt"], "claim")
        self.assertTrue(any(x["text"].casefold() == "claim" for x in r["measured_features"]["prompt"]["word_sequence"]))
        self.assertIn("claim", json.dumps(r).casefold())
        legacy = audit_full("claim perhaps")
        covered = "".join(x["text"] for x in legacy["surface_census"]["tokens"])
        self.assertEqual(covered, "claim perhaps")
        self.assertEqual(legacy["analytic_lexicons"], "vocabulary matches are measured outputs only; no term is excluded from analysis")

    def test_caller_receipts_are_preserved_as_unverified_and_distinct(self):
        receipts = [{"tool": "calendar_write", "status": "succeeded", "result": {"event_id": "x"}}]
        r = audit_evidence_case("create event", "created event succeeded", receipts)
        receipt_record = r["rule_based_mappings"]["receipt_records"][0]
        self.assertEqual(receipt_record["provided_fields"]["status"], "succeeded")
        self.assertEqual(receipt_record["source_status"], "caller_supplied_unverified")
        self.assertTrue(any(x["field"] == "status" and x["literal_mentioned_in_output"] for x in r["rule_based_mappings"]["tool_receipt_field_mentions_in_output"]))

    def test_logic_modes_are_separately_labeled_and_cautious(self):
        r = audit_evidence_case("Report 4 passed.", "Report 3 failed.")
        self.assertIn("deductions", r)
        self.assertIn("inductions", r)
        self.assertIn("abductive_hypotheses", r)
        self.assertEqual(r["inductions"][0]["generalization"], "not made")
        self.assertTrue(any("private model reasoning" in x for x in r["unknowns"]))

    def test_literal_requirements_are_not_semantic_judgments(self):
        r = audit_evidence_case("Use the exact word alpha", "Use the exact word beta", requirements=["alpha"])
        check = r["measured_features"]["caller_selected_literal_requirement_checks"][0]
        self.assertFalse(check["present_exactly"])
        self.assertEqual(check["classification"], "rule_based_literal_check")

    def test_limits_enforced_without_truncation(self):
        with self.assertRaises(ValueError): audit_evidence_case("x" * 65537, "y")
        with self.assertRaises(ValueError): audit_evidence_case("x", "y", [{}] * 257)

    def test_receipt_digest_detects_edit(self):
        r = audit_evidence_case("a", "b")
        r["inputs"]["output"] = "altered"
        self.assertFalse(verify_case(r))

    def test_full_audit_and_mcp_expose_evidence_case(self):
        full = audit_full("Claim 12%: alpha?")
        self.assertEqual("".join(x["text"] for x in full["surface_census"]["tokens"]), "Claim 12%: alpha?")
        listed = dispatch({"id": 1, "method": "tools/list"})["result"]["tools"]
        self.assertIn("prime_evidence_case", {x["name"] for x in listed})
        called = dispatch({"id": 2, "method": "tools/call", "params": {"name": "prime_evidence_case", "arguments": {"prompt": "claim", "output": "claim"}}})
        self.assertFalse(called["result"]["isError"])
        result = json.loads(called["result"]["content"][0]["text"])
        self.assertEqual(result["schema"], "prime.evidence-case.v1")

if __name__ == "__main__":
    unittest.main()
