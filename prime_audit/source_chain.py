"""Seven-role audit of the same complete source and candidate.

Each local role invokes PRIME; roles are not GitHub-assigned Copilot agents. A
role's output is never substituted for the original source or candidate.
"""
import argparse
import hashlib
import json
from pathlib import Path
from .engine import MAX_TEXT, audit_text
from .role_lexicons import ROLES


def chain(source, candidate, audit=audit_text):
    if not isinstance(source, str) or not isinstance(candidate, str):
        raise ValueError('source and candidate must be strings')
    if len(source) > MAX_TEXT or len(candidate) > MAX_TEXT:
        raise ValueError('full inputs exceed PRIME limit; refusing truncation')
    results = []
    for role in ROLES:
        outcome = audit(candidate, source)
        results.append({'role': role, 'result': outcome})
    return {'schema': 'prime.source-chain.v1',
            'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
            'source_characters': len(source), 'candidate_characters': len(candidate),
            'roles': results, 'mode': 'local-prime-per-role',
            'limits': ['identical text-pattern audit at each role; not independent agent reasoning',
                       'not a live Copilot chain or autonomous repair']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(args.source).read_text(encoding='utf-8')
    candidate = Path(args.candidate).read_text(encoding='utf-8')
    result = chain(source, candidate)
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Seven local role audits completed with full identical inputs; see receipt.')

if __name__ == '__main__':
    main()
