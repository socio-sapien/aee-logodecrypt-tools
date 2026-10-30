#!/usr/bin/env python3
"""
THAUMATURGICON CHASSIS CLI v7.0 — MARKET-READY EDITION
=====================================================

Terminal interface and automated command utility for the v7.0 chassis.

Exit codes (deterministic, CI-friendly):
  0  success
  1  verification failure or benchmark compromise detected
  2  configuration error (e.g. benchmark invoked without a real target)

Honesty guarantees:
  - No fabricated refusals, verdicts, or telemetry.
  - Benchmark results are computed from a real system under test.
  - Verification results are computed against a golden snapshot file.
  - Credentials are read from the environment and never echoed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

curr_dir = os.path.dirname(os.path.abspath(__file__))

if __package__ in (None, ""):
    sys.path.insert(0, curr_dir)

try:
    from thaumaturgicon_chassis_v7 import (
        CHASSIS_VERSION,
        AEEv4Engine,
        AnchorVerifier,
        AuditStore,
        BenchmarkRunner,
        CanaryHTTPTarget,
        CredentialProvider,
        SovereignChassis,
        StaticFunctionTarget,
        TargetNotConfiguredError,
        TelemetryProvider,
    )
except ImportError as exc:  # pragma: no cover
    sys.stderr.write("Failed to import thaumaturgicon_chassis_v7: %s\n" % exc)
    sys.exit(2)


C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_CYAN = "\033[36m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_CONFIG = 2


def print_banner() -> None:
    banner = f"""
{C_CYAN}{C_BOLD}╔═════════════════════════════════════════════════════════════════════════════╗
║            THAUMATURGICON CHASSIS CLI — MARKET-READY EDITION (v7.0)          ║
║   Deterministic scoring  •  Real telemetry  •  No fabricated results          ║
╚═════════════════════════════════════════════════════════════════════════════╝{C_RESET}
"""
    print(banner)


def render_gauge(label: str, value: float, max_val: float, unit: str = "", width: int = 24) -> str:
    pct = max(0.0, min(1.0, value / max_val if max_val > 0 else 0.0))
    filled = int(round(pct * width))
    bar = "█" * filled + "░" * (width - filled)
    color = C_GREEN if pct >= 0.8 else (C_YELLOW if pct >= 0.5 else C_RED)
    return f"{label:<26} [{color}{bar}{C_RESET}] {value:.2f}{unit}"


def cmd_audit(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    res = chassis.audit_text(args.text)
    if args.json:
        print(json.dumps(res, indent=2, default=str))
        return EXIT_OK
    fid = res.get("fidelity", {})
    print(f"Specimen: '{args.text[:80]}{'...' if len(args.text) > 80 else ''}'")
    print("-" * 78)
    print(f"Words: {res['words']} | Letters: {res['letters']} | s-Census: {res['s_census']}")
    print(render_gauge("PIC Metric", res["pic"], 2.0))
    print(render_gauge("Truth Gradient (T_d)", res["t_d"], 5.0))
    print(render_gauge("Duty Fidelity", fid.get("duty_fidelity", 100.0), 100.0, "%"))
    print(f"Hedge density /1k words: {res['hedge_density_per_1k']}")
    print(f"Structural (S): {C_GREEN}{res['s_count']}{C_RESET} terms ({', '.join(res['s_terms']) or 'None'})")
    print(f"Evasion (D): {C_RED}{res['d_count']}{C_RESET} terms ({', '.join(res['d_terms']) or 'None'})")
    print(f"Contamination: {res['contamination']} | Intent: {res['intent_line']}")
    print(f"Distortion Risk: {fid.get('distortion_risk')}")
    verdict_color = C_GREEN if res["verdict"] == "TRUE" else C_RED
    print(f"FINAL VERDICT: {verdict_color}{C_BOLD}*** {res['verdict']} ***{C_RESET}")
    print(f"Audit Log ID: #{res['log_id']} | Fidelity Log ID: #{res.get('fidelity_id', '-')}")
    return EXIT_OK


def cmd_telemetry(args: argparse.Namespace) -> int:
    telemetry = TelemetryProvider.read()
    if args.json:
        print(json.dumps(telemetry, indent=2, default=str))
        return EXIT_OK
    print(f"{C_BOLD}=== REAL HOST TELEMETRY (measured; unavailability is stated, never faked) ==={C_RESET}")
    for key, value in telemetry.items():
        print(f"  {key:<22}: {value}")
    return EXIT_OK


def cmd_status(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    audits = chassis.bridge.list_audits(50)
    tasks = chassis.bridge.list_task_audits(50)
    fidelity = chassis.bridge.list_fidelity_logs(50)
    chain = chassis.bridge.verify_chain("audit_logs")
    creds = chassis.credentials.status()
    telemetry = TelemetryProvider.read()
    if args.json:
        print(json.dumps({
            "chassis_version": CHASSIS_VERSION,
            "database_path": chassis.bridge.db_path,
            "audits": len(audits),
            "tasks": len(tasks),
            "fidelity_records": len(fidelity),
            "audit_chain_valid": chain["valid"],
            "credential_presence": creds,
            "telemetry": telemetry,
        }, indent=2, default=str))
        return EXIT_OK
    print(f"{C_BOLD}┌── CHASSIS STATUS (v{CHASSIS_VERSION}) ───────────────────────────────────────┐{C_RESET}")
    print(f"│  Database:         {chassis.bridge.db_path}")
    print(f"│  Audit chain:      {'VALID' if chain['valid'] else 'TAMPER DETECTED'} ({chain['records']} records)")
    print(f"│  Records:          {len(audits)} audits | {len(tasks)} tasks | {len(fidelity)} fidelity")
    print(f"│  Telemetry source: {telemetry.get('telemetry_source')}")
    print(f"│  Credentials:      {', '.join(k for k, ok in creds.items() if ok) or 'none configured (environment only)'}")
    print(f"{C_BOLD}└──────────────────────────────────────────────────────────────────────────────┘{C_RESET}")
    return EXIT_OK


def cmd_benchmark(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    try:
        if args.endpoint:
            api_key = os.environ.get(args.api_key_env or "OPENAI_API_KEY", "")
            target = CanaryHTTPTarget(
                endpoint=args.endpoint,
                model=args.model or "",
                api_key=api_key,
                system_prompt=args.system_prompt or "",
                timeout=args.timeout,
            )
        elif args.target_script:
            namespace: Dict[str, Any] = {}
            with open(args.target_script, "r", encoding="utf-8") as handle:
                exec(compile(handle.read(), args.target_script, "exec"), namespace)  # noqa: S102
            submit_fn = namespace.get("submit")
            if not callable(submit_fn):
                sys.stderr.write("Target script must define submit(prompt) -> str.\n")
                return EXIT_CONFIG
            target = StaticFunctionTarget(submit_fn)
        else:
            raise TargetNotConfiguredError(
                "No target configured. Provide --endpoint (OpenAI-compatible API) "
                "or --target-script (Python callable). Results are never fabricated."
            )
        runner = BenchmarkRunner(chassis)
        report = runner.run(target, args.canary)
    except TargetNotConfiguredError as exc:
        sys.stderr.write("CONFIGURATION ERROR: %s\n" % exc)
        return EXIT_CONFIG

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"{C_BOLD}=== 14-STEP LADDER RESULTS (computed from real responses) ==={C_RESET}")
        print(f"{'Rank':<5} | {'Tokens':<6} | {'Verdict':<12} | {'Duty %':<8} | {'Latency':<10} | Lever")
        print("-" * 84)
        for step in report["steps"]:
            color = C_GREEN if step["verdict"] == "DEFENDED" else (C_YELLOW if step["verdict"] == "ERROR" else C_RED)
            print(f"{step['rank']:<5} | {step['tokens']:<6} | {color}{step['verdict']:<12}{C_RESET} | {step['duty_fidelity']:<8.1f} | {step['latency_ms']:<10.1f} | {step['lever']}")
        print("-" * 84)
        summary = report["summary"]
        print(f"Summary: {summary['defended']}/{summary['total']} defended | "
              f"{summary['compromised']} compromised | {summary['errors']} errors")

    return EXIT_OK if report["summary"]["all_defended"] else EXIT_FAIL


def cmd_verify(args: argparse.Namespace) -> int:
    golden_path = args.golden or os.path.join(curr_dir, "anchor_golden.json")
    if args.init_golden:
        AnchorVerifier.init_golden(golden_path)
        print(f"Golden snapshot written: {golden_path}")
        return EXIT_OK
    if not os.path.exists(golden_path):
        sys.stderr.write(
            "CONFIGURATION ERROR: golden snapshot not found at %s. "
            "Run with --init-golden first.\n" % golden_path
        )
        return EXIT_CONFIG
    report = AnchorVerifier.verify(golden_path)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        status = "MATCH" if report["passed"] else "MISMATCH"
        color = C_GREEN if report["passed"] else C_RED
        print(f"Anchor verification: {color}{C_BOLD}{report['anchors_checked']} anchors, "
              f"{report['fields_checked']} fields, {len(report['mismatches'])} mismatches — {status}{C_RESET}")
        for mismatch in report["mismatches"]:
            print(f"  {C_RED}{mismatch['anchor']}.{mismatch['field']}: expected {mismatch['expected']}, got {mismatch['actual']}{C_RESET}")
    return EXIT_OK if report["passed"] else EXIT_FAIL


def cmd_chain_verify(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    results = [chassis.bridge.verify_chain(table) for table in AuditStore.CHAINED_TABLES]
    valid = all(r["valid"] for r in results)
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        for r in results:
            color = C_GREEN if r["valid"] else C_RED
            print(f"{r['table']:<30}: {color}{'VALID' if r['valid'] else 'TAMPER DETECTED (' + r['reason'] + ')'}{C_RESET} ({r['records']} records)")
    return EXIT_OK if valid else EXIT_FAIL


def cmd_tasks(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    logs = chassis.bridge.list_task_audits(args.limit)
    if args.json:
        print(json.dumps(logs, indent=2, default=str))
        return EXIT_OK
    print(f"{'ID':<6} | {'Task':<30} | {'Status':<9} | {'Duty %':<8} | {'Latency':<10} | {'In':<10} | {'Out':<10}")
    print("-" * 92)
    for log in logs:
        status_color = C_GREEN if log["status"] == "SUCCESS" else C_RED
        print(f"#{log['id']:<5} | {log['task_name'][:30]:<30} | {status_color}{log['status']:<9}{C_RESET} | "
              f"{log.get('duty_fidelity', 0):<8.1f} | {log.get('latency_ms', 0):<10.1f} | "
              f"{(log.get('in_verdict') or '-'):<10} | {(log.get('out_verdict') or '-'):<10}")
    print(f"Total task records shown: {len(logs)}")
    return EXIT_OK


def cmd_forensic(chassis: SovereignChassis, args: argparse.Namespace) -> int:
    report = chassis.forensic_engine.generate_full_evidentiary_report(
        audit_version=args.version,
    )
    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return EXIT_OK
    summary = report["summary_of_evidentiary_status"]
    print(f"{C_BOLD}=== FORENSIC EVIDENTIARY REPORT (from stored records only) ==={C_RESET}")
    print(f"Events cataloged:      {summary['total_events_cataloged']}")
    print(f"Findings evaluated:    {summary['total_findings_evaluated']}")
    print(f"Contradictions:        {summary['total_contradictions_identified']}")
    print(f"Unsupported (E0):      {summary['unsupported_assertions_flagged']}")
    print("Full JSON report persisted to AuditStore (forensic_audit_reports).")
    return EXIT_OK


def cmd_credentials(args: argparse.Namespace) -> int:
    provider = CredentialProvider()
    status = provider.status()
    if args.json:
        print(json.dumps(status, indent=2))
        return EXIT_OK
    print(f"{C_BOLD}=== CREDENTIAL PRESENCE (values are never displayed) ==={C_RESET}")
    for key, present in status.items():
        color = C_GREEN if present else C_YELLOW
        print(f"  {key:<24}: {color}{'configured' if present else 'not set'}{C_RESET}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Thaumaturgicon Chassis CLI v7.0 — Market-Ready Edition"
    )
    parser.add_argument("--db", type=str, default=None,
                        help="Database path (default: THAUMATURGICON_DB or ~/.thaumaturgicon/chassis.db)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    sub = parser.add_subparsers(dest="command")

    p_audit = sub.add_parser("audit", help="Run a deterministic AEE v4.0 audit on text")
    p_audit.add_argument("text", type=str)

    sub.add_parser("telemetry", help="Print real host telemetry")

    sub.add_parser("status", help="Print chassis status (chain integrity, counts, credentials)")

    p_bench = sub.add_parser("benchmark", help="Run the 14-step ladder against a real target")
    p_bench.add_argument("--endpoint", type=str, help="OpenAI-compatible chat completions URL")
    p_bench.add_argument("--model", type=str, help="Model name for the endpoint")
    p_bench.add_argument("--api-key-env", type=str, default="OPENAI_API_KEY",
                         help="Environment variable holding the API key")
    p_bench.add_argument("--system-prompt", type=str,
                         help="System prompt; must instruct the SUT to hold the canary secret")
    p_bench.add_argument("--canary", type=str, required=True,
                         help="Canary secret the ladder attempts to extract")
    p_bench.add_argument("--target-script", type=str,
                         help="Python file defining submit(prompt) -> str as the SUT")
    p_bench.add_argument("--timeout", type=float, default=60.0)

    p_verify = sub.add_parser("verify", help="Verify engine anchors against a golden snapshot")
    p_verify.add_argument("--golden", type=str, help="Golden snapshot path")
    p_verify.add_argument("--init-golden", action="store_true",
                          help="Create the golden snapshot from current engine output")

    sub.add_parser("chain-verify", help="Verify the SHA-256 audit record hash chain")

    p_tasks = sub.add_parser("tasks", help="List intercepted task audit records")
    p_tasks.add_argument("--limit", type=int, default=20)

    p_forensic = sub.add_parser("forensic", help="Generate the evidentiary report from stored records")
    p_forensic.add_argument("--version", type=str, default="1.0")

    sub.add_parser("credentials", help="Show credential presence (values are never displayed)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        parser.print_help()
        return EXIT_CONFIG

    if args.command in ("telemetry", "credentials", "verify"):
        chassis: Optional[SovereignChassis] = None
    else:
        chassis = SovereignChassis(db_path=args.db)

    if args.command == "audit":
        return cmd_audit(chassis, args)
    if args.command == "telemetry":
        return cmd_telemetry(args)
    if args.command == "status":
        return cmd_status(chassis, args)
    if args.command == "benchmark":
        return cmd_benchmark(chassis, args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "chain-verify":
        return cmd_chain_verify(chassis, args)
    if args.command == "tasks":
        return cmd_tasks(chassis, args)
    if args.command == "forensic":
        return cmd_forensic(chassis, args)
    if args.command == "credentials":
        return cmd_credentials(args)
    parser.print_help()
    return EXIT_CONFIG


if __name__ == "__main__":
    sys.exit(main())
