"""Bounded audit/triage/action wrapper. An executor must be supplied by the host.

The four-by-four matrix is a deterministic evidence ledger, not quaternion algebra,
independent verification, or inferred motivation. Observations must be caller supplied.
"""
import time
from .engine import simulate_operation, receipt, digest

REMEDIES = ('fix', 'repair', 'remedy', 'solution')
LENSES = ('conceptual', 'ideological', 'cumulative', 'progressive')
STATES = ('supported', 'contradicted', 'unknown')


def matrix(observations):
    if not isinstance(observations, list) or len(observations) > 16:
        raise ValueError('up to 16 observations required')
    cells = {(r, l): {'state': 'unknown', 'evidence_refs': []} for r in REMEDIES for l in LENSES}
    seen = set()
    for obs in observations:
        if not isinstance(obs, dict) or set(obs) != {'remedy', 'lens', 'state', 'evidence_refs'}:
            raise ValueError('invalid matrix observation')
        r, l, state, refs = obs['remedy'], obs['lens'], obs['state'], obs['evidence_refs']
        if r not in REMEDIES or l not in LENSES or state not in STATES or (r, l) in seen:
            raise ValueError('invalid or duplicate matrix cell')
        if not isinstance(refs, list) or len(refs) > 8 or any(not isinstance(x, str) or not x or len(x) > 240 for x in refs):
            raise ValueError('invalid evidence references')
        if state != 'unknown' and not refs:
            raise ValueError('supported and contradicted cells need evidence references')
        seen.add((r, l)); cells[(r, l)] = {'state': state, 'evidence_refs': refs}
    return {'schema': 'prime.matrix.v1', 'rows': list(REMEDIES), 'columns': list(LENSES),
            'cells': [{'remedy': r, 'lens': l, **cells[(r, l)]} for r in REMEDIES for l in LENSES],
            'interpretation': 'caller-supplied evidence ledger; labels do not prove intent or efficacy'}


def preflight(operation, simulation_fn=None):
    """Preserve existing policy and wrap its exact simulated decision with timing."""
    start = time.monotonic_ns()
    simulation = (simulation_fn or simulate_operation)(operation)
    if not isinstance(simulation, dict):
        raise ValueError('invalid simulation')
    unsigned = {k: v for k, v in simulation.items() if k != 'receipt'}
    if simulation.get('receipt', {}).get('sha256') != digest(unsigned):
        raise ValueError('invalid simulation receipt')
    return receipt({'schema': 'prime.harness.preflight.v1', 'simulation': simulation,
                    'local_elapsed_ns': time.monotonic_ns() - start,
                    'target_ns': 7_000_000, 'timing_is_observational': True,
                    'executed': False})


def run(operation, observations=None, executor=None, verifier=None):
    """Assess a supplied operation; only an explicit host callback executes it.

    A passing simulation is not authority. Host MUST independently authorize and
    constrain the callback. Any policy-blocked decision blocks callback invocation.
    Verifier returns a bool based on actual observations, not self-reported intent.
    """
    if observations is None:
        observations = []
    mat = matrix(observations)
    pre = preflight(operation)
    stages = [{'stage': 'investigate', 'status': 'recorded'},
              {'stage': 'triage', 'status': pre['simulation']['decision']}]
    execution = {'status': 'not_run'}
    verification = {'status': 'not_run'}
    if executor is not None and not callable(executor):
        raise ValueError('executor must be callable')
    if verifier is not None and not callable(verifier):
        raise ValueError('verifier must be callable')
    if executor is not None and pre['simulation']['decision'] == 'READY_FOR_BOUNDED_REVIEW':
        try:
            value = executor(operation)
            execution = {'status': 'returned'}
            try:
                execution['result_sha256'] = digest(value)
            except (TypeError, ValueError):
                execution['result_recording'] = 'not_serializable'
            if verifier is not None:
                verified = verifier(value)
                if type(verified) is not bool:
                    raise ValueError('verifier must return bool')
                verification = {'status': 'verified' if verified else 'failed'}
        except Exception as exc:
            if execution['status'] == 'returned':
                verification = {'status': 'error', 'error_type': type(exc).__name__}
            else:
                execution = {'status': 'outcome_unknown', 'error_type': type(exc).__name__}
    elif executor is not None:
        execution = {'status': 'blocked_by_preflight'}
    stages.extend([{'stage': 'action', 'status': execution['status']},
                   {'stage': 'verify', 'status': verification['status']}])
    return receipt({'schema': 'prime.harness.run.v1', 'preflight': pre, 'matrix': mat,
                    'stages': stages, 'execution': execution, 'verification': verification,
                    'limits': ['unsigned local receipt', 'host authorizes executor separately',
                               'coverage is limited to adapters that invoke this wrapper']})
