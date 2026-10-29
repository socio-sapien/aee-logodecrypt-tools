#!/usr/bin/env python3
"""AEE v4.0 Core CLI - Developer Edition"""
import sys
import argparse
import json
from aee_minimal_skeleton import aee_minimal_audit

def main():
    parser = argparse.ArgumentParser(description="AEE v4.0 Core CLI: Deterministic Text Diagnostic")
    parser.add_argument("--text", type=str, help="Text string to audit")
    parser.add_argument("--file", type=str, help="Path to text file to audit")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    content = ""
    if args.text:
        content = args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("Reading from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()

    res = aee_minimal_audit(content)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("
================ AEE v4.0 AUDIT RECORD ================")
        print(f"VERDICT:        {res['VERDICT']}")
        print(f"CONTAMINATION:  {res['CONTAMINATION']} (Absolute Rule: C=0 -> TRUE)")
        print(f"TRUTH DECAY Td: {res['T_d']:.4f}")
        print(f"PIC RATIO:      {res['PIC']:.4f}")
        print(f"METRICS:        Words: {res['WORDS']} | S (Structure): {res['S']} | D (Evasion): {res['D']}")
        print(f"FIRST LOCUS:    {res['FLAG']}")
        if res['D_TERMS']:
            print(f"EVASIONS FOUND: {', '.join(res['D_TERMS'])}")
        print("=======================================================
")

if __name__ == '__main__':
    main()
