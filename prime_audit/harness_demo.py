"""A seven-stage local fixture chain through the host-supplied action wrapper."""
import argparse
import json
import time
import tempfile
import hashlib
from pathlib import Path
from .engine import receipt
from .harness import run
from .seven_roles import SCENARIOS
from .role_lexicons import ROLES
from .auto_repair import repair

def demonstration():
    steps = []
    start = time.monotonic_ns()
    for name, spec in ROLES.items():
        op = {'action': 'test', 'paths': ['README.md'], 'expected_observation': name + ' fixture passes'}
        result = run(op, executor=lambda _, fn=SCENARIOS[name]: fn(), verifier=lambda x: x is True)
        steps.append({'role': name, 'stage': spec['stage'], 'harness_receipt_sha256': result['receipt']['sha256'],
                      'execution': result['execution']['status'], 'verification': result['verification']['status'],
                      'preflight_elapsed_ns': result['preflight']['local_elapsed_ns']})
        if result['verification']['status'] != 'verified':
            break
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'fixture.txt'
        f.write_text('teh example', encoding='utf-8')
        repair_result = repair(d, 'fixture.txt', hashlib.sha256(b'teh example').hexdigest(),
                               'teh', 'the', ['fixture.txt'], lambda p: p.read_text() == 'the example')
    return receipt({'schema':'prime.harness.demo.v1', 'mode':'offline-fixture-chain',
                    'total_elapsed_ns':time.monotonic_ns()-start, 'steps':steps,
                    'passed':len(steps)==7 and all(x['verification']=='verified' for x in steps) and repair_result['status']=='verified',
                    'local_fixture_repair': repair_result,
                    'live_agent_sessions':0, 'external_calls':0,
                    'limitations':['Synthetic fixtures, not seven live agent runs.', 'Local durations exclude GitHub queues and network.']})

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output', default='prime-harness-demo.json')
    args=parser.parse_args(); result=demonstration()
    Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if not result['passed']: raise SystemExit(1)

if __name__ == '__main__': main()
