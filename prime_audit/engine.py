"""Deterministic policy simulation. No subprocess, network, credentials or code execution."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from .instrument import analyze, verify

MAX_TEXT = 65536
ACTIONS = {'read', 'propose_patch', 'test', 'network', 'deploy', 'secret', 'delete', 'push', 'merge'}
PROTECTED = ('.git', '.github', '.prime', 'prime_audit')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def receipt(value):
    return {**value, 'receipt': {'sha256': digest(value), 'type': 'unsigned-integrity-record'}}

def valid_path(path):
    if not isinstance(path, str) or not path or '\\' in path or '\x00' in path:
        return False
    p = PurePosixPath(path)
    return bool(p.parts) and p.as_posix() == path and not p.is_absolute() and '..' not in p.parts and p.parts[0] != '.git'

def protected(path):
    return any(path == p or path.startswith(p + '/') for p in PROTECTED)

def sensitive(path):
    return any(x == '.git' or x in {'.env', 'credentials.json', 'token.json', 'client_secret.json'} or x.startswith(('.env.', 'client_secret_')) or x.endswith(('.pem', '.key')) for x in PurePosixPath(path).parts)

def audit_text(text, source=None):
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError('text must be a string of at most 65536 characters')
    if source is not None and (not isinstance(source, str) or len(source) > MAX_TEXT):
        raise ValueError('source must be at most 65536 characters')
    report = analyze(text, context=source, token_cap=1)
    if not verify(report):
        raise ValueError('instrument receipt mismatch')
    return report

def simulate_operation(operation):
    if not isinstance(operation, dict):
        raise ValueError('operation must be an object')
    action = operation.get('action')
    paths = operation.get('paths', [])
    if action not in ACTIONS or not isinstance(paths, list) or len(paths) > 200:
        raise ValueError('unknown action or invalid paths')
    if any(not valid_path(p) for p in paths):
        raise ValueError('paths must be repository-relative without traversal')
    reasons = []
    if any(sensitive(p) for p in paths):
        reasons.append('sensitive path requires separate credential-safe handling')
    if action not in {'read', 'propose_patch', 'test'}:
        reasons.append('external or destructive effect requires a separate authorized executor')
    if action == 'propose_patch' and any(protected(p) for p in paths):
        reasons.append('control-plane change requires independent human review')
    if action in {'propose_patch', 'test'} and not operation.get('expected_observation'):
        reasons.append('define a concrete expected observation before execution')
    return receipt({'schema': 'prime.operation.v1', 'mode': 'simulation-only',
        'operation_sha256': digest(operation), 'action': action, 'paths': paths,
        'decision': 'REVIEW_REQUIRED' if reasons else 'READY_FOR_BOUNDED_REVIEW',
        'reasons': reasons, 'executed': False,
        'constraints': {'network': False, 'credential_access': False, 'automatic_apply': False},
        'meaning': 'Policy simulation only; neither authorization nor proof of runtime safety.'})

def audit_change(paths, diff):
    if len(paths) > 10000 or any(not valid_path(p) for p in paths):
        raise ValueError('invalid changed-file inventory')
    truncated = len(diff) > MAX_TEXT
    report = audit_text(diff[:MAX_TEXT])
    # Do not copy patch/source text into receipts or hook logs.
    return receipt({'schema': 'prime.change.v1', 'paths': paths,
        'control_plane_changes': [p for p in paths if protected(p)],
        'diff_sha256': hashlib.sha256(diff.encode()).hexdigest(), 'analysis_truncated': truncated,
        'negation_cue_count': len(report['surface']['negation_cues']),
        'instrument_receipt': report['receipt'], 'executed': False,
        'decision': 'REVIEW_REQUIRED' if truncated or any(protected(p) for p in paths) else 'REVIEW_RECORDED',
        'meaning': 'Text cues are review evidence, not a correctness/security verdict.'})
