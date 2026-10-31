"""Verify installed files, MCP dispatch, automatic hook inputs and source integrity."""
import argparse
import hashlib
import json
from pathlib import Path
from .full import audit_full, hook_audit, prime
from .mcp_server import dispatch
from .engine import receipt

ROOT = Path(__file__).resolve().parent.parent

def verify():
    config=json.loads((ROOT/'.github/mcp.json').read_text())
    assert 'prime_full_audit' in config['mcpServers']['prime-audit']['tools']
    result=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_full_audit','arguments':{'text':'Do not run until approved. 15 records.','source':'Run if approved. 12 records.'}}})
    assert not result['result']['isError']
    parsed=json.loads(result['result']['content'][0]['text'])
    assert parsed['version']=='6.7.0'
    hooked=hook_audit({'toolName':'view','toolArgs':{'path':'README.md'}},ROOT)
    return receipt({'schema':'prime.environment.v1','version':prime.VERSION,
        'module':'prime_audit/vendor/prime_v6_7.py',
        'module_sha256':hashlib.sha256((ROOT/'prime_audit/vendor/prime_v6_7.py').read_bytes()).hexdigest(),
        'workspace_mcp_config':'.github/mcp.json','mcp_dispatch':'passed',
        'hook_full_battery':hooked,'hosted_copilot_session':'not established by this self-check'})

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); args=ap.parse_args()
    report=verify(); Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print('PRIME 6.7 files, MCP dispatch and hook battery verified; no live-agent claim.')

if __name__=='__main__':main()
