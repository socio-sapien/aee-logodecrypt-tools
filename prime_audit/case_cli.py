"""Command-line interface for supplied PRIME evidence cases; reads local JSON only."""
import argparse
import json
import sys
from pathlib import Path
from .evidence_case import audit_evidence_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="JSON file; omit to read JSON from stdin")
    args = parser.parse_args()
    raw = Path(args.input).read_text(encoding="utf-8") if args.input and args.input != "-" else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise SystemExit("input must be a JSON object")
    allowed = {"prompt", "output", "tool_receipts", "requirements"}
    if set(data) - allowed or not {"prompt", "output"} <= set(data):
        raise SystemExit("expected prompt/output and optional tool_receipts/requirements")
    result = audit_evidence_case(**data)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
