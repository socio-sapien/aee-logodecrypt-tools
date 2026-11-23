#!/usr/bin/env python3
"""Standalone CLI batch runner for AEE metric scoring.

Reads a JSONL file of records, each containing "prompt" and "completion"
(or "response") fields, scores every completion with the METR task scorer,
and prints (and optionally writes) the aggregate summary.

Usage:
    python scripts/run_batch.py --input records.jsonl [--output results.json]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aee_benchmark.plugin import METRTaskScorer


def main() -> None:
    parser = argparse.ArgumentParser(description="AEE batch scorer (JSONL in, summary out)")
    parser.add_argument("--input", required=True, help="Path to a JSONL file of records")
    parser.add_argument("--output", default=None, help="Optional path for the JSON summary")
    args = parser.parse_args()

    records = []
    with open(args.input, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))

    summary = METRTaskScorer().evaluate_batch(records)
    rendered = json.dumps(summary, indent=2)

    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")

    print(rendered)


if __name__ == "__main__":
    main()
