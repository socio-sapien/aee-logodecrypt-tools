#!/usr/bin/env python3
"""Run the supplied Chassis CLI against task and provider text, storing a local report."""
import sys as _prime_sys
from pathlib import Path as _PrimePath
_prime_sys.path.insert(0, str(_PrimePath(__file__).resolve().parents[3]))
from prime_audit.timing import monitored as _prime_monitored
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "chassis_cli_v7.py"


@_prime_monitored("chassis_audit")
def cli_audit(text: str, db: str) -> dict:
    env = os.environ.copy()
    env["THAUMATURGICON_DB"] = db
    result = subprocess.run(
        [sys.executable, str(CLI), "--db", db, "--json", "audit", text],
        cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError("Chassis CLI failed with exit status %d." % result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError("Chassis CLI returned invalid JSON.") from None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--request", required=True)
    p.add_argument("--vibe-output", required=True)
    p.add_argument("--chaingpt-output", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--db", required=True)
    args = p.parse_args()
    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    chain_text = Path(args.chaingpt_output).read_text(encoding="utf-8")[:12000]
    specimens = {
        "owner_request": req["request"][:12000],
        "mistral_vibe_draft": Path(args.vibe_output).read_text(encoding="utf-8")[:12000],
    }
    results = {label: cli_audit(text, args.db) for label, text in specimens.items()}
    if chain_text.startswith("CHAIN_GPT_SKIPPED:"):
        results["chaingpt_review"] = {"status": "not_run", "reason": chain_text.strip()}
    else:
        results["chaingpt_review"] = cli_audit(chain_text, args.db)
    report = {
        "schema": "chassis-v7-text-audit-report-v1",
        "repo": req.get("repo_full_name"),
        "issue_number": req.get("issue_number"),
        "scope": "surface/lexicon heuristic audit of supplied text only",
        "warning": "Chassis heuristic fields are not factual verification, model quality, security, semantic correctness, or a chain-state finding.",
        "results": results,
    }
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Chassis audits saved; interpret all scores as heuristics, not truth labels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
