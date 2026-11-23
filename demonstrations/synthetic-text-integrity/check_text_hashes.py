#!/usr/bin/env python3
"""Check supplied SHA-256 values against the UTF-8 encoding of JSON text fields."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def check_rows(data):
    if not isinstance(data, list) or not data:
        return ['input must be a nonempty JSON array']
    errors = []
    for i, row in enumerate(data, start=1):
        if not isinstance(row, dict):
            errors.append(f'row {i}: must be an object')
            continue
        text, digest = row.get('text'), row.get('sha256')
        if not isinstance(text, str) or not text:
            errors.append(f'row {i}: text must be a nonempty string')
            continue
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            errors.append(f'row {i}: sha256 must be 64 lowercase hex characters')
            continue
        try:
            encoded = text.encode('utf-8')
        except UnicodeEncodeError:
            errors.append(f'row {i}: text cannot be encoded as UTF-8')
            continue
        if hashlib.sha256(encoded).hexdigest() != digest:
            errors.append(f'row {i}: digest mismatch')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file', type=Path, help='JSON array with text and sha256 fields')
    args = parser.parse_args()
    try:
        with args.json_file.open(encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'Cannot read JSON input: {exc.__class__.__name__}', file=sys.stderr)
        return 2
    errors = check_rows(data)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f'OK: {len(data)} row(s) match their provided SHA-256 values')
    return 0

if __name__ == '__main__':
    sys.exit(main())
