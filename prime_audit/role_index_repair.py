"""Automatically reconcile the derived role index with the local role definitions.

Only .prime/role-index.json is changed; no candidate patch or external command
is interpreted from audit input. The caller supplies the trusted repository root.
"""
import hashlib
import json
from pathlib import Path
from .auto_repair import repair
from .role_lexicons import ROLES

PATH = '.prime/role-index.json'

def canonical_index():
    return json.dumps({'schema': 'prime.role-index.v1', 'roles': [
        {'role': name, 'stage': spec['stage']} for name, spec in ROLES.items()
    ]}, indent=2) + '\n'

def reconcile(root):
    root = Path(root).resolve(strict=True)
    path = root / PATH
    if path.is_symlink() or not path.is_file():
        raise ValueError('existing regular role index required')
    old = path.read_bytes()
    desired = canonical_index()
    if old == desired.encode():
        return {'status': 'already_current', 'path': PATH}
    before = old.decode('utf-8')
    if not before: raise ValueError('empty index requires manual recovery')
    outcome = repair(root, PATH, hashlib.sha256(old).hexdigest(), before, desired,
                     [PATH], lambda actual: actual.read_text(encoding='utf-8') == desired)
    return outcome

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    p.add_argument('--receipt', default='prime-role-repair-receipt.json')
    args = p.parse_args()
    result = reconcile(args.root)
    Path(args.receipt).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    if result['status'] not in ('already_current', 'verified'):
        raise SystemExit('Index repair failed verification')
    print('Role index:', result['status'])
