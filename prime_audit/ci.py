"""Provider-free CI: audit a git comparison; never execute the diff."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from .engine import audit_change, simulate_operation

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def commit(ref):
    if not isinstance(ref, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', ref):
        raise ValueError('Full commit SHA required')
    return git('rev-parse', '--verify', ref + '^{commit}')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base')
    p.add_argument('--head')
    p.add_argument('--event', help='GitHub event JSON; extracts exact base/head commit IDs')
    p.add_argument('--output', default='prime-audit-receipt.json')
    a = p.parse_args()
    if a.event:
        data = json.loads(Path(a.event).read_text())
        pr = data.get('pull_request')
        if pr:
            base, head = pr['base']['sha'], pr['head']['sha']
        else:
            head = git('rev-parse', 'HEAD')
            base = data.get('before')
            if not base or base == '0' * 40:
                base = git('rev-parse', 'HEAD^')
    else:
        base, head = a.base, a.head
    refs = [commit(base), commit(head)]
    paths = subprocess.check_output(['git', 'diff', '--name-only', '-z', *refs, '--']).decode().split('\0')
    diff = subprocess.check_output(['git', 'diff', '--no-ext-diff', '--no-textconv', '--unified=3', *refs, '--']).decode(errors='replace')
    manifest = json.loads(Path('.prime/operations.json').read_text())
    if not isinstance(manifest, list) or len(manifest) > 100:
        raise ValueError('operation plan must be a bounded array')
    result = {'base': refs[0], 'head': refs[1], 'change': audit_change([x for x in paths if x], diff), 'operations': [simulate_operation(op) for op in manifest]}
    result['operation_gate'] = 'pass' if all(op['decision'] == 'READY_FOR_BOUNDED_REVIEW' for op in result['operations']) else 'review_required'
    Path(a.output).write_text(json.dumps(result, indent=2) + '\n')
    if result['operation_gate'] != 'pass':
        raise SystemExit('PRIME operation policy requires review; no operation executed.')
    print('PRIME audit recorded. Review the receipt; this is not authorization or a security certification.')

if __name__ == '__main__':
    main()
