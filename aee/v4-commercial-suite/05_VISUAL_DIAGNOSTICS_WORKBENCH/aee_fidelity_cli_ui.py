#!/usr/bin/env python3
"""
SOVEREIGN CLI UI & FORENSIC METADATA AUDIT INTERFACE (v6.0)
===========================================================

Terminal User Interface (CLI UI) and automated command utility integrating:
  - Pure AEE v4.0 Truth & Intent Metrics (Words, S, D, PIC, T_d, Contamination)
  - Sovereign Fidelity Device (Duty Fidelity 0-100%, Distortion Risk)
  - Forensic Metadata Investigation & Evidentiary Audit Engine:
      * Evidence Classification: E1 (Transcript), E2 (Artifact), E3 (Telemetry), E0 (Unsupported)
      * Chronological Event Ledger (EVT-xxx)
      * Finding Records (FND-xxx) with verbatim excerpts & confidence basis
      * Contradictions Ledger (CONTRA-xxx)
  - Plaintext Operational Credentials (zero simulated secret vault or withheld keys)
  - Persistent SQLite LocalDataBridge logging (/tmp/oracle_chassis.db)
"""

import sys
import os
import argparse
import json
import time
import importlib.util

curr_dir = os.path.dirname(os.path.abspath(__file__))

def _load_module(name, filename):
    path = os.path.join(curr_dir, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

_chassis_mod = _load_module('software_utility_chassis', 'software_utility_chassis.py')
SovereignChassis = _chassis_mod.SovereignChassis
AEEv4Engine = _chassis_mod.AEEv4Engine
SovereignFidelityDevice = _chassis_mod.SovereignFidelityDevice
EvidenceClass = _chassis_mod.EvidenceClass


# ANSI Color Codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_CYAN = "\033[36m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"


def print_banner():
    banner = f"""
{C_CYAN}{C_BOLD}╔═════════════════════════════════════════════════════════════════════════════╗
║         SOVEREIGN CLI UI & FORENSIC METADATA AUDIT INTERFACE (v6.0)         ║
║         AEE v4.0 Engine  •  Evidence Tiers (E1/E2/E3/E0)  •  Direct Root    ║
╚═════════════════════════════════════════════════════════════════════════════╝{C_RESET}
"""
    print(banner)


def render_gauge(label: str, value: float, max_val: float, unit: str = "", width: int = 24) -> str:
    pct = max(0.0, min(1.0, value / max_val if max_val > 0 else 0.0))
    filled = int(round(pct * width))
    bar = "█" * filled + "░" * (width - filled)
    color = C_GREEN if pct >= 0.8 else (C_YELLOW if pct >= 0.5 else C_RED)
    return f"{label:<22} [{color}{bar}{C_RESET}] {value:.2f}{unit}"


def render_status_card(chassis: SovereignChassis):
    audits = chassis.bridge.list_audits(50)
    task_audits = chassis.bridge.list_task_audits(50)
    events = chassis.bridge.list_forensic_events(50)
    findings = chassis.bridge.list_forensic_findings(50)
    contras = chassis.bridge.list_forensic_contradictions(50)

    hw = chassis.fidelity_device.HARDWARE_PROFILE

    print(f"{C_BOLD}┌── SYSTEM TELEMETRY & SOVEREIGN STATUS ──────────────────────────────────────┐{C_RESET}")
    print(f"│  Chassis Core:       {C_GREEN}ACTIVE (Sovereign Root / Zero Artificial Secrecy){C_RESET}    │")
    print(f"│  Forensic Engine:    {C_GREEN}OPERATIONAL (v1.0 Evidence Directive Schema){C_RESET}         │")
    print(f"│  Target Device:      {hw['device_model']:<48} │")
    print(f"│  Target SoC:         {hw['soc']:<48} │")
    print(f"│  Execution Mode:     {C_CYAN}{hw['execution_mode']:<48}{C_RESET} │")
    print(f"│  Event Ledger:       {len(events)} Forensic Events Cataloged                           │")
    print(f"│  Findings Ledger:    {len(findings)} Evaluated Claims | {len(contras)} Active Contradictions          │")
    print(f"│  Database Logs:      {len(audits)} AEE Audits | {len(task_audits)} Intercepted Tasks                     │")
    print(f"{C_BOLD}└─────────────────────────────────────────────────────────────────────────────┘{C_RESET}\n")


def execute_forensic_report_cli(chassis: SovereignChassis):
    print(f"\n{C_BOLD}=== EXECUTING FORENSIC METADATA & EVIDENTIARY SELF-AUDIT ==={C_RESET}")
    report = chassis.execute_forensic_self_audit()
    meta = report["audit_metadata"]
    summary = report["summary_of_evidentiary_status"]

    print(f"Audit Version:    {meta['audit_version']} ({meta['audit_date']})")
    print(f"Auditor Engine:   {meta['auditor']}")
    print(f"Execution Status: {C_GREEN}{meta['execution_status']}{C_RESET}")
    print("-" * 75)
    print(f"Total Events Cataloged:        {summary['total_events_cataloged']}")
    print(f"Total Findings Evaluated:      {summary['total_findings_evaluated']}")
    print(f"Total Contradictions Tracked:  {summary['total_contradictions_identified']}")
    print(f"Unsupported Assertions Flagged:{C_RED} {summary['unsupported_assertions_flagged']} (E0){C_RESET}")
    print(f"Verified Artifacts (SHA-256):  {len(summary['verified_artifacts_sha256'])}")
    print("-" * 75)
    print(f"{C_CYAN}Full JSON Audit Schema generated and stored in SQLite LocalDataBridge.{C_RESET}\n")


def show_events_ledger(chassis: SovereignChassis):
    print(f"\n{C_BOLD}=== CHRONOLOGICAL FORENSIC EVENT LEDGER (EVT) ==={C_RESET}")
    events = chassis.bridge.list_forensic_events(100)
    if not events:
        chassis.execute_forensic_self_audit()
        events = chassis.bridge.list_forensic_events(100)

    print(f"{'ID':<9} | {'Class':<5} | {'Timestamp':<24} | {'Event Type':<26} | {'Description'}")
    print("-" * 88)
    for e in events:
        c_color = C_GREEN if e['evidence_class'] in ['E2', 'E3'] else (C_CYAN if e['evidence_class'] == 'E1' else C_RED)
        e_cls = f"{c_color}{e['evidence_class']}{C_RESET}"
        print(f"{e['event_id']:<9} | {e_cls:<14} | {e['timestamp']:<24} | {e['event_type'][:26]:<26} | {e['description'][:48]}")
    print("-" * 88)
    print(f"Total Cataloged Events: {len(events)}\n")


def show_findings_ledger(chassis: SovereignChassis):
    print(f"\n{C_BOLD}=== EVIDENTIARY FINDINGS LEDGER (FND) ==={C_RESET}")
    findings = chassis.bridge.list_forensic_findings(100)
    if not findings:
        chassis.execute_forensic_self_audit()
        findings = chassis.bridge.list_forensic_findings(100)

    for f in findings:
        c_color = C_GREEN if f['evidence_class'] == 'E2' else (C_CYAN if f['evidence_class'] == 'E1' else C_RED)
        print(f"{C_BOLD}[{f['finding_id']}]{C_RESET} Tier: {c_color}{f['evidence_class']}{C_RESET} | Verified: {f['independently_verified']}")
        print(f"  Claim:       {f['claim']}")
        print(f"  Excerpt:     \"{f['source_excerpt']}\"")
        print(f"  Location:    {f['source_location']}")
        print(f"  Conclusion:  {C_BOLD}{f['conclusion']}{C_RESET}")
        print(f"  Confidence:  {f['confidence_basis']}")
        if f['contradictory_evidence']:
            print(f"  {C_RED}Contradictions: {', '.join(f['contradictory_evidence'])}{C_RESET}")
        print("-" * 75)
    print(f"Total Evaluated Findings: {len(findings)}\n")


def show_contradictions_ledger(chassis: SovereignChassis):
    print(f"\n{C_BOLD}=== FORENSIC CONTRADICTIONS LEDGER (CONTRA) ==={C_RESET}")
    contras = chassis.bridge.list_forensic_contradictions(100)
    if not contras:
        chassis.execute_forensic_self_audit()
        contras = chassis.bridge.list_forensic_contradictions(100)

    for c in contras:
        print(f"{C_BOLD}[{c['contra_id']}]{C_RESET} Tension Type: {C_YELLOW}{c['tension_type']}{C_RESET} | Status: {C_GREEN}{c['resolution_status']}{C_RESET}")
        print(f"  Claim A:  {c['claim_a']}")
        print(f"  Claim B:  {c['claim_b']}")
        print(f"  Basis:    {c['evidence_basis']}")
        print("-" * 75)
    print(f"Total Tracked Contradictions: {len(contras)}\n")


def show_plaintext_keys(chassis: SovereignChassis):
    print(f"\n{C_BOLD}=== SOVEREIGN OPERATIONAL CREDENTIALS (PLAINTEXT) ==={C_RESET}")
    creds = chassis.credentials.dump_all()
    for k, v in creds.items():
        print(f"  • {C_BOLD}{k:<24}{C_RESET}: {C_GREEN}{v}{C_RESET}")
    print()


def execute_audit_task(chassis: SovereignChassis, text: str):
    print(f"\n{C_BOLD}=== AEE v4.0 DETERMINISTIC AUDIT ==={C_RESET}")
    res = chassis.audit_text(text)
    fid = res.get("fidelity", {})

    print(f"Specimen Preview: '{text[:80]}{'...' if len(text) > 80 else ''}'")
    print("-" * 75)
    print(f"Words:           {res['words']:<6} | Letters: {res['letters']:<6} | s-Census: {res['s_census']}")
    print(render_gauge("PIC Metric", res['pic'], 2.0, ""))
    print(render_gauge("Truth Gradient (T_d)", res['t_d'], 5.0, ""))
    print(render_gauge("Duty Fidelity", fid.get('duty_fidelity', 100.0), 100.0, "%"))

    s_str = ", ".join(res['s_terms']) if res['s_terms'] else "None"
    d_str = ", ".join(res['d_terms']) if res['d_terms'] else "None"
    print(f"Structural (S):  {C_GREEN}{res['s_count']} terms{C_RESET} ({s_str})")
    print(f"Evasion (D):     {C_RED}{res['d_count']} terms{C_RESET} ({d_str})")
    print(f"Contamination:   {res['contamination']}")
    print(f"Intent Line:     {C_CYAN}{res['intent_line']}{C_RESET}")
    print(f"Distortion Risk: {C_BOLD}{fid.get('distortion_risk')}{C_RESET}")
    print("-" * 75)
    verdict_color = C_GREEN if res['verdict'] == 'TRUE' else C_RED
    print(f"FINAL VERDICT:   {verdict_color}{C_BOLD}*** {res['verdict']} ***{C_RESET}")
    print("=" * 75 + "\n")


def interactive_cli_ui(chassis: SovereignChassis):
    print_banner()
    render_status_card(chassis)

    while True:
        print(f"{C_BOLD}Sovereign Forensic UI Menu:{C_RESET}")
        print("  [1] Audit Text Specimen (AEE v4.0 Full Metrics & Intent)")
        print("  [2] Measure Specimen with Fidelity Device (Duty % & Distortion Risk)")
        print("  [3] Run Full Forensic Metadata & Evidentiary Self-Audit (17-Section JSON)")
        print("  [4] View Chronological Event Ledger (EVT-xxx with Evidence Tiers)")
        print("  [5] View Evidentiary Findings Ledger (FND-xxx with Confidence Basis)")
        print("  [6] View Contradictions Ledger (CONTRA-xxx)")
        print("  [7] Dump Operational Plaintext Keys & Hashes")
        print("  [8] View Task Audit Ledger (SQLite LocalDataBridge)")
        print("  [9] Refresh Telemetry Dashboard")
        print("  [q] Exit Interface")

        choice = input(f"\n{C_BOLD}Select Option [1-9, q]: {C_RESET}").strip()

        if choice == '1':
            sample = input("\nEnter text to audit (leave blank for verified formula): ").strip()
            if not sample:
                sample = "The measured transaction block signature matches the verified formula and audit record with zero error."
            execute_audit_task(chassis, sample)
        elif choice == '2':
            sample = input("\nEnter text for fidelity measurement: ").strip()
            if not sample:
                sample = "We collect your data to improve our services and potentially optimize user engagement moving forward."
            execute_audit_task(chassis, sample)
        elif choice == '3':
            execute_forensic_report_cli(chassis)
        elif choice == '4':
            show_events_ledger(chassis)
        elif choice == '5':
            show_findings_ledger(chassis)
        elif choice == '6':
            show_contradictions_ledger(chassis)
        elif choice == '7':
            show_plaintext_keys(chassis)
        elif choice == '8':
            logs = chassis.bridge.list_task_audits(20)
            print(f"\n{C_BOLD}=== TASK AUDIT LEDGER ==={C_RESET}")
            for l in logs:
                print(f"#{l['id']:<4} | {l['task_name'][:24]:<24} | Duty: {l.get('duty_fidelity', 100)}% | Latency: {l.get('latency_ms', 0):.1f}ms | Status: {l['status']}")
            print()
        elif choice == '9':
            render_status_card(chassis)
        elif choice.lower() in ['q', 'exit', 'quit']:
            print(f"\n{C_GREEN}Exiting Interface. Sovereign Chassis Operational.{C_RESET}\n")
            break
        else:
            print(f"\n{C_RED}Invalid option selected.{C_RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Sovereign CLI UI & Forensic Metadata Audit Engine")
    parser.add_argument("--audit", type=str, help="Run AEE v4.0 audit on text specimen")
    parser.add_argument("--forensic", action="store_true", help="Generate full forensic evidence self-audit report")
    parser.add_argument("--events", action="store_true", help="List chronological forensic event ledger")
    parser.add_argument("--findings", action="store_true", help="List evidentiary findings ledger")
    parser.add_argument("--contradictions", action="store_true", help="List tracked contradictions")
    parser.add_argument("--keys", action="store_true", help="Dump all operational credentials in plaintext")
    parser.add_argument("--status", action="store_true", help="Print chassis and forensic status card")

    args = parser.parse_args()

    db_path = "/tmp/oracle_chassis.db"
    chassis = SovereignChassis(db_path=db_path)

    has_flags = any([args.audit, args.forensic, args.events, args.findings, args.contradictions, args.keys, args.status])

    if not has_flags:
        interactive_cli_ui(chassis)
        return

    print_banner()
    if args.status:
        render_status_card(chassis)
    if args.keys:
        show_plaintext_keys(chassis)
    if args.audit:
        execute_audit_task(chassis, args.audit)
    if args.forensic:
        execute_forensic_report_cli(chassis)
    if args.events:
        show_events_ledger(chassis)
    if args.findings:
        show_findings_ledger(chassis)
    if args.contradictions:
        show_contradictions_ledger(chassis)


if __name__ == "__main__":
    main()