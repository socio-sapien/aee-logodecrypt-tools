"""Deterministic local text repair with explicitly scoped targets and verification.

This is a host-invoked primitive, not an autonomous GitHub/MCP repair service.
It never interprets remote content as commands, starts programs, commits or merges.
"""
import hashlib
import os
import tempfile
from pathlib import Path
from .engine import valid_path, sensitive, receipt

MAX_BYTES = 65536

def _hash(b):
    return hashlib.sha256(b).hexdigest()

def repair(root, path, expected_sha256, before, after, allow_paths, verify):
    """Replace one unique literal in one explicitly allowed file; verify or rollback.

    Caller controls allow_paths and verifier independently of untrusted events. The
    verifier must observe actual post-change state. Local receipt is unsigned.
    Rollback is not promised after machine failure or concurrent modification.
    """
    if (not isinstance(path, str) or not valid_path(path) or sensitive(path)
        or path not in allow_paths or not callable(verify)):
        raise ValueError('invalid or disallowed repair target')
    if not isinstance(before, str) or not before or not isinstance(after, str):
        raise ValueError('literal replacement required')
    root = Path(root).resolve(strict=True)
    target = root
    for part in Path(path).parts:
        target = target / part
        if target.is_symlink(): raise ValueError('symlink path refused')
    if not target.is_file() or target.stat().st_nlink != 1:
        raise ValueError('regular unlinked file required')
    original = target.read_bytes()
    if len(original) > MAX_BYTES or _hash(original) != expected_sha256:
        raise ValueError('file changed or too large')
    try: old = original.decode('utf-8')
    except UnicodeDecodeError as e: raise ValueError('UTF-8 required') from e
    if old.count(before) != 1: raise ValueError('expected one exact occurrence')
    updated = old.replace(before, after, 1).encode('utf-8')
    if len(updated) > MAX_BYTES: raise ValueError('replacement too large')
    mode = target.stat().st_mode & 0o777
    def atomic_write(data):
        fd, tmp = tempfile.mkstemp(prefix='.prime-repair-', dir=target.parent)
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            os.chmod(tmp, mode)
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    atomic_write(updated)
    error = None
    try:
        passed = verify(target)
        if type(passed) is not bool: raise ValueError('verifier must return bool')
    except Exception as e:
        passed = False; error = type(e).__name__
    if passed and (target.is_symlink() or not target.is_file() or target.read_bytes() != updated):
        passed = False
    status = 'verified' if passed else 'verification_failed'
    if not passed:
        # Do not overwrite another actor's concurrent subsequent edit.
        if target.is_symlink() or not target.is_file() or target.read_bytes() != updated:
            status = 'rollback_conflict'
        else:
            atomic_write(original); status = 'rolled_back'
    return receipt({'schema': 'prime.local_repair.v1', 'path': path,
                    'before_sha256': _hash(original), 'candidate_sha256': _hash(updated),
                    'status': status, 'verifier_error_type': error,
                    'limits': ['single local text file', 'host-scoped allowlist',
                               'no external or GitHub action', 'unsigned receipt']})
