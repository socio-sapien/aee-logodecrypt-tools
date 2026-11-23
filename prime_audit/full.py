"""Repository adapter for the unchanged standalone PRIME 6.7 instrument.

No network, execution, arbitrary profiles, or invented contextual metadata.
"""
import hashlib
import json
import re
from .vendor import prime_v6_7 as prime
from .engine import receipt
from .evidence_case import surface_census, audit_evidence_case

MAX_TEXT = 65536
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def audit_full(text, source=None):
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError('text must be a string of at most 65536 characters')
    if source is not None and (not isinstance(source, str) or len(source) > MAX_TEXT):
        raise ValueError('source must be a string of at most 65536 characters')
    matches = list(TOKEN_RE.finditer(text))
    small = len(matches) <= 128
    report = prime.run_omni_analysis(text, context=source,
        domain='agent_trace', include_performance=True,
        include_word_dynamics=small, include_logical_actions=True)
    if not prime.verify_report(report, text.encode())['report_integrity_valid']:
        raise ValueError('PRIME 6.7 report integrity failure')
    # Respect the instrument's explicit 128-token lens bound without truncation.
    # Each local permutation remains chunk-scoped; never describe it as global.
    chunks = []
    if not small:
        starts = [0] + [m.start() for m in matches[128::128]] + [len(text)]
        for start, end in zip(starts, starts[1:]):
            chunk = text[start:end]
            chunks.append({'start': start, 'end': end,
                'input_sha256': hashlib.sha256(chunk.encode()).hexdigest(),
                'lens': prime._word_dynamics_lens(chunk)})
    return receipt({'schema': 'prime.full-battery.v2', 'version': prime.VERSION,
        'input_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'source_sha256': None if source is None else hashlib.sha256(source.encode()).hexdigest(),
        'report': report, 'word_dynamics_chunks': chunks,
        'surface_census': surface_census(text),
        'source_surface_census': None if source is None else surface_census(source),
        'coverage': {'base_analysis': 'complete input', 'surface_census': 'all Unicode code points, tokens, numbers, symbols, and adjacent token/word relations in supplied text', 'logical_actions': 'enabled',
            'word_dynamics': 'whole input' if small else 'contiguous chunks; local indices/permutations',
            'caller_metadata': 'unset unless supplied to the standalone instrument',
            'runtime_internal_thoughts': 'not observed'},
        'analytic_lexicons': 'vocabulary matches are measured outputs only; no term is excluded from analysis',
        'meaning': 'Deterministic surface measurements and rule-based cues; not proof of truth, intent or universal correctness.'})


def hook_audit(event, root):
    """Audit exact available instructions and event in memory; persist hashes only."""
    inputs = [('tool-event', json.dumps(event, ensure_ascii=False, sort_keys=True))]
    for name in ('AGENTS.md', '.github/copilot-instructions.md', 'PRIME_PROTOCOL.md'):
        path = root / name
        if path.is_file():
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError('instruction outside repository')
            inputs.append((name, path.read_text(encoding='utf-8')))
    summaries = []
    for label, text in inputs:
        result = audit_full(text)
        summaries.append({'input': label, 'input_sha256': result['input_sha256'],
            'report_sha256': result['receipt']['sha256'], 'version': prime.VERSION,
            'characters': len(text), 'word_dynamics': result['coverage']['word_dynamics'],
            'lenses': list(result['report']), 'raw_text_persisted': False})
    return receipt({'schema': 'prime.hook.full-battery.v1', 'inputs': summaries,
        'coverage': 'available repository instructions and exact hook event; not hidden model reasoning'})
