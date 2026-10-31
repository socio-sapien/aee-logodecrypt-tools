"""Seven role simulations. These checks never assign agents or execute user operations."""
from .timing import monitored
import contextlib
import hashlib
import hmac
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from . import hook
from .engine import audit_text, simulate_operation, receipt
from .mcp_server import dispatch
from .webhook import ingest

from .role_lexicons import ROLES
from .timing import Timing

def _evidence():
    r=simulate_operation({'action':'propose_patch','paths':['file.py']})
    return r['decision']=='REVIEW_REQUIRED' and r['executed'] is False

def _perception():
    r=audit_text('Do not deploy.', 'Deploy.')
    return bool(r['surface']['negation_cues'])

def _boundary():
    try:
        simulate_operation({'action':'read','paths':['../.env']})
    except ValueError:
        return True
    return False

def _integrity():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); (root/'.git').mkdir()
        event=json.dumps({'toolName':'view','toolArgs':{'path':'README.md'}})
        out=io.StringIO()
        with patch.object(hook,'ROOT',root), patch.object(hook.os,'open',side_effect=OSError('injected')), patch('sys.stdin',io.StringIO(event)), contextlib.redirect_stdout(out):
            hook.main()
        return json.loads(out.getvalue())['permissionDecision']=='deny'

def _protocol():
    r=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_simulate_operation','arguments':{'operation':{'action':'deploy','paths':[]}}}})
    obj=json.loads(r['result']['content'][0]['text'])
    return obj['decision']=='REVIEW_REQUIRED' and not obj['executed']

def _webhook():
    raw=json.dumps({'repository':{'full_name':'fixture/repo'},'action':'opened','issue':{'title':'fixture'}}).encode()
    sig='sha256='+hmac.new(b'fixture-secret',raw,hashlib.sha256).hexdigest()
    def headers(delivery): return {'X-Hub-Signature-256':sig,'X-GitHub-Delivery':delivery,'X-GitHub-Event':'issues'}
    with tempfile.TemporaryDirectory() as d:
        db=str(Path(d)/'inbox.sqlite')
        first=ingest(raw,headers('first'),'fixture-secret',{'fixture/repo'},db)
        replay=ingest(raw,headers('second'),'fixture-secret',{'fixture/repo'},db)
        return first[0]==202 and first[1].get('executed') is False and replay[0]==409

def _verification():
    safe=simulate_operation({'action':'test','paths':['file.py'],'expected_observation':'tests pass'})
    risky=simulate_operation({'action':'propose_patch','paths':['.github/workflows/prime-audit.yml'],'expected_observation':'reviewed'})
    return safe['decision']=='READY_FOR_BOUNDED_REVIEW' and risky['decision']=='REVIEW_REQUIRED' and not safe['executed']

SCENARIOS = {'evidence':_evidence,'perception':_perception,'boundary':_boundary,'integrity':_integrity,'protocol':_protocol,'webhook':_webhook,'verification':_verification}

@monitored("seven_scenarios")
def run():
    results=[]
    timing=Timing()
    for role, spec in ROLES.items():
        started=timing.clock()
        try:
            passed=SCENARIOS[role]() is True
            error=None
        except Exception as exc:
            passed=False
            error=type(exc).__name__
        timing.mark(role, started)
        results.append({'role':role,'stage':spec['stage'],'passed':passed,'error_type':error})
    return receipt({'timing':timing.record(), 'schema':'prime.seven-role-simulations.v1','mode':'offline-fixture-only','roles':results,'agent_sessions_started':0,'executed_operations':0,'limitations':['Finite synthetic checks, not a guarantee.','Lexicons are contextual cues, not semantic or sensory analysis.','Identical webhook bodies may be legitimate; deduplication is not complete replay protection.']})

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--output',default='prime-seven-role-receipt.json'); a=p.parse_args()
    result=run(); Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not all(item['passed'] for item in result['roles']): raise SystemExit(1)

if __name__=='__main__': main()
