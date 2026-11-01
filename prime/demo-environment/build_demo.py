#!/usr/bin/env python3
"""Rebuild or verify the self-contained PRIME customer demo from its actual local core."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE = ROOT / "prime" / "aee_logodecrypt_prime.py"
SCENARIOS = HERE / "scenarios.json"
TEMPLATE = HERE / "index.template.html"
HTML_OUT = HERE / "index.html"
RESULTS_OUT = HERE / "scenario-results.json"
EXPECTED_IDS = {
    "refund-flips", "release-gate", "market-simulation", "privacy-disclosure",
    "unicode-boundary", "license-terms", "generated-alternative", "contract-audit-mismatch", "role-swap-blind-spot",
    "agent-execution-claim", "oracle-freshness-shift",
}
IMPACT_FIELDS = {"person", "workflow", "industry", "market", "long_tail"}

spec = importlib.util.spec_from_file_location("prime_demo_core", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load core module: {CORE}")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def build() -> tuple[str, str, dict]:
    cases = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)) or any(not isinstance(item, str) for item in ids):
        raise ValueError("Scenario ids must be non-empty and unique")
    records = []
    for case in cases:
        if case.get("frame") not in core.FRAMES:
            raise ValueError(f"Unsupported frame in {case['id']}")
        if not isinstance(case.get("candidate"), str) or not isinstance(case.get("impact"), dict):
            raise ValueError(f"Scenario is incomplete: {case['id']}")
        result = core.analyze(case["candidate"], case.get("source"), case["frame"])
        if not core.verify(result):
            raise AssertionError(f"Core receipt verification failed: {case['id']}")
        if result["source_verbatim"] != case["candidate"]:
            raise AssertionError(f"Candidate was not preserved: {case['id']}")
        impact = case["impact"]
        if set(impact) != IMPACT_FIELDS or any(not isinstance(impact[key], str) or not impact[key].strip() for key in IMPACT_FIELDS):
            raise ValueError(f"Each scenario must explain all five conditional impact horizons: {case['id']}")
        records.append({
            "scenario": case,
            "analysis_target": "candidate",
            "analysis_target_note": "The core's source_verbatim field preserves the candidate under analysis; scenario.source is separate context.",
            "result": result,
        })
    if set(ids) != EXPECTED_IDS:
        raise ValueError(f"Expected the curated eleven-scene demonstration; got {sorted(ids)}")
    by_id = {record["scenario"]["id"]: record for record in records}
    # Keep the honest, high-stakes examples and the intentional blind spot from silently regressing.
    refund = by_id["refund-flips"]["result"]["context_fidelity"]
    if [(x["source_pole"], x["candidate_pole"]) for x in refund["curated_polarity_changes"]] != [("approved", "denied")]:
        raise AssertionError("Refund fixture must surface the approved → denied cue")
    release = by_id["release-gate"]["result"]["context_fidelity"]
    if not any((x["source_pole"], x["candidate_pole"]) == ("failed", "passed") for x in release["curated_polarity_changes"]):
        raise AssertionError("Release fixture must surface the failed → passed cue")
    market = by_id["market-simulation"]["result"]["context_fidelity"]
    if market["candidate_numbers_not_in_source_multiset"] != ["6"] or market["source_numbers_not_in_candidate_multiset"] != ["18"]:
        raise AssertionError("Market fixture must surface the changed counts")
    unicode_result = by_id["unicode-boundary"]["result"]["scripts"]
    if "CYRILLIC" not in unicode_result["letters_by_script"] or not any(x["codepoint"] == "U+200B" for x in unicode_result["format_controls"]):
        raise AssertionError("Unicode fixture must expose the staged mixed-script and format-control cues")
    contract = by_id["contract-audit-mismatch"]["result"]["context_fidelity"]
    if contract["candidate_numbers_not_in_source_multiset"] != ["0"] or contract["source_numbers_not_in_candidate_multiset"] != ["1"]:
        raise AssertionError("Contract fixture must surface the changed finding count")
    if not any((x["source_pole"], x["candidate_pole"]) == ("failed", "passed") for x in contract["curated_polarity_changes"]):
        raise AssertionError("Contract fixture must surface the changed test status")
    contract_case = by_id["contract-audit-mismatch"]["scenario"]
    if "Release status: blocked" not in contract_case["source"] or "Release status: approved" not in contract_case["candidate"]:
        raise AssertionError("Contract fixture must preserve its synthetic release-state contrast")
    settlement = by_id["agent-execution-claim"]["result"]["context_fidelity"]
    if settlement["candidate_numbers_not_in_source_multiset"] != ["1"] or settlement["source_numbers_not_in_candidate_multiset"] != ["0"]:
        raise AssertionError("Agent fixture must surface the synthetic 0 → 1 broadcast-count change")
    if not any((x["source_pole"], x["candidate_pole"]) == ("failed", "passed") for x in settlement["curated_polarity_changes"]):
        raise AssertionError("Agent fixture must surface the authorization test status change")
    oracle = by_id["oracle-freshness-shift"]["result"]["context_fidelity"]
    if oracle["candidate_numbers_not_in_source_multiset"] or oracle["source_numbers_not_in_candidate_multiset"]:
        raise AssertionError("Oracle fixture must keep its synthetic block reference unchanged")
    if not any((x["source_pole"], x["candidate_pole"]) == ("failed", "passed") for x in oracle["curated_polarity_changes"]):
        raise AssertionError("Oracle fixture must surface the freshness-test status change")
    blind = by_id["role-swap-blind-spot"]["result"]["context_fidelity"]
    if blind["status"] != "NO-SELECTED-CUE-DIFFERENCE" or blind["curated_polarity_changes"] or blind["candidate_numbers_not_in_source_multiset"] or blind["source_numbers_not_in_candidate_multiset"]:
        raise AssertionError("Role-swap fixture must remain an explicit known miss, not a pass")
    generated = by_id["generated-alternative"]["result"]["transformations"]
    if "GENERATED" not in generated["counterfactual_lexical_flip"]["label"] or "NOT" not in generated["counterfactual_lexical_flip"]["label"]:
        raise AssertionError("Generated alternative must remain explicitly labelled as generated")
    results = {
        "title": "PRIME Demonstration Environment",
        "engine": "prime/aee_logodecrypt_prime.py",
        "engine_version": core.VERSION,
        "provenance": "Generated locally by this repository's deterministic analyzer; all cases are synthetic.",
        "cases": records,
    }
    results_text = json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    template = TEMPLATE.read_text(encoding="utf-8")
    marker = "/*__PRIME_DEMO_DATA__*/"
    if template.count(marker) != 1:
        raise ValueError(f"Expected exactly one {marker} marker in template")
    # Prevent scenario text from closing the inline script element.
    payload = json.dumps(results, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = template.replace(marker, "const DEMO = " + payload + ";")
    return html, results_text, results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify committed outputs match a fresh run; do not write")
    args = parser.parse_args()
    html, results_text, results = build()
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in ((HTML_OUT, html), (RESULTS_OUT, results_text))
                 if not path.exists() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing generated demo artifact(s): " + ", ".join(stale), file=sys.stderr)
            print("Run: python3 prime/demo-environment/build_demo.py", file=sys.stderr)
            return 1
        print(f"Verified {len(results['cases'])} synthetic scenarios against PRIME {core.VERSION}; embedded receipts verify.")
        return 0
    HTML_OUT.write_text(html, encoding="utf-8")
    RESULTS_OUT.write_text(results_text, encoding="utf-8")
    print(f"Built {len(results['cases'])} synthetic scenarios for PRIME {core.VERSION}.")
    print(f"Wrote {HTML_OUT.relative_to(ROOT)} and {RESULTS_OUT.relative_to(ROOT)}")
    print("No external model or network service was called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
