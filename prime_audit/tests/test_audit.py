import hashlib
import hmac
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from prime_audit.engine import audit_change, audit_text, simulate_operation, valid_path, digest
from prime_audit.hook import decision, ROOT
from prime_audit.mcp_server import dispatch
from prime_audit.webhook import ingest

class AuditTests(unittest.TestCase):
    def test_sensitive_read_requires_review(self):
        r = simulate_operation({'action': 'read', 'paths': ['.env']})
        self.assertEqual(r['decision'], 'BLOCKED_BY_POLICY')

    def test_hook_process_records_and_denies_shell(self):
        result = subprocess.run([sys.executable, '-m', 'prime_audit.hook'], input=json.dumps({'toolName': 'bash', 'toolArgs': {'command': 'echo not-executed'}}), text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)['permissionDecision'], 'deny')
        self.assertTrue((ROOT / '.git/prime-audit/decisions.jsonl').is_file())

    def test_canonical_paths(self):
        for path in ('.', './.github/workflows/x', 'foo//bar', 'foo/../bar', '/tmp/x'):
            self.assertFalse(valid_path(path))

    def test_mcp_invalid_params(self):
        with self.assertRaises(ValueError):
            dispatch({'id': 1, 'method': 'initialize', 'params': 'wrong'})

    def test_instrument_receipt(self):
        self.assertEqual(audit_text('It did not pass.')['surface']['negation_cues'][0]['quote'], 'not')
    def test_source(self):
        self.assertEqual(audit_text('Passed 15 tests', 'Failed 12 tests')['context_fidelity']['status'], 'REVIEW-CUES')
    def test_oversize(self):
        with self.assertRaises(ValueError): audit_text('a' * 65537)
    def test_read_simulation(self):
        r = simulate_operation({'action':'read','paths':['README.md']})
        self.assertFalse(r['executed']); self.assertEqual(r['decision'], 'READY_FOR_BOUNDED_REVIEW')
    def test_patch_needs_observation(self):
        self.assertEqual(simulate_operation({'action':'propose_patch'})['decision'], 'BLOCKED_BY_POLICY')
    def test_protected_patch(self):
        r=simulate_operation({'action':'propose_patch','paths':['.github/hooks/a.json'],'expected_observation':'test'})
        self.assertEqual(r['decision'], 'BLOCKED_BY_POLICY')
    def test_external_never_executes(self):
        for action in ['network','deploy','secret','delete','push','merge']:
            r=simulate_operation({'action':action,'approved':True})
            self.assertEqual(r['decision'],'BLOCKED_BY_POLICY'); self.assertFalse(r['executed'])
    def test_invalid_action(self):
        with self.assertRaises(ValueError): simulate_operation({'action':'shell'})
    def test_paths(self):
        for path in ['../x','/tmp/x','.git/config','x/../../q','x\\q', '', 'x\x00y']:
            self.assertFalse(valid_path(path), repr(path))
    def test_receipt(self):
        r=simulate_operation({'action':'read'}); receipt=r.pop('receipt'); self.assertEqual(receipt['sha256'],digest(r))
    def test_diff(self):
        self.assertEqual(audit_change(['.github/hooks/prime.json'], 'not retained')['decision'],'AUTOMATED_CHECKS_NEEDED')
    def test_diff_truncation(self):
        self.assertTrue(audit_change(['README.md'], 'x' * 65537)['analysis_truncated'])
    def test_hook_unknown(self):
        self.assertEqual(decision({'toolName':'bash','toolArgs':{'command':'curl evil'}})['permissionDecision'], 'deny')
    def test_hook_read(self):
        self.assertEqual(decision({'toolName':'view','toolArgs':{'path':'README.md'}})['permissionDecision'], 'allow')
    def test_hook_edit(self):
        self.assertEqual(decision({'toolName':'str_replace_editor','toolArgs':{'path':'src/new.py'}})['permissionDecision'], 'allow')
    def test_hook_protection(self):
        for path in ['.github/hooks/prime.json','prime_audit/hook.py','.git/config','../x','.env','foo/key.pem']:
            self.assertEqual(decision({'toolName':'str_replace_editor','toolArgs':{'path':path}})['permissionDecision'],'deny',path)
    def test_hook_absolute_external(self):
        self.assertEqual(decision({'toolName':'view','toolArgs':{'path':'/etc/passwd'}})['permissionDecision'],'deny')
    def test_hook_symlink(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            p=Path(d)/'link'; p.symlink_to('/etc/passwd')
            self.assertEqual(decision({'toolName':'view','toolArgs':{'path':str(p)}})['permissionDecision'],'deny')
    def test_mcp_initialize(self):
        self.assertEqual(dispatch({'id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}})['result']['protocolVersion'],'2025-03-26')
    def test_mcp_tools(self):
        tools=dispatch({'id':2,'method':'tools/list'})['result']['tools']
        self.assertEqual({t['name'] for t in tools},{'prime_audit_text','prime_simulate_operation','prime_investigate'}); self.assertTrue(all(t['annotations']['readOnlyHint'] for t in tools))
    def test_mcp_call(self):
        r=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_simulate_operation','arguments':{'operation':{'action':'push'}}}})
        self.assertFalse(r['result']['isError']); self.assertFalse(json.loads(r['result']['content'][0]['text'])['executed'])
    def test_mcp_unknown(self):
        self.assertTrue(dispatch({'id':1,'method':'tools/call','params':{'name':'exec'}})['result']['isError'])
    def test_mcp_stdio(self):
        data='\n'.join(json.dumps(x) for x in [{'jsonrpc':'2.0','id':1,'method':'initialize'}, {'jsonrpc':'2.0','method':'notifications/initialized'}, {'jsonrpc':'2.0','id':2,'method':'tools/list'}])+'\n'
        p=subprocess.run([sys.executable,'-m','prime_audit.mcp_server'],input=data,capture_output=True,text=True,check=True)
        self.assertEqual(len(p.stdout.splitlines()),2); self.assertEqual(json.loads(p.stdout.splitlines()[1])['id'],2)
    def signed(self, raw, delivery='test-123'):
        return {'X-Hub-Signature-256':'sha256='+hmac.new(b'test-secret',raw,hashlib.sha256).hexdigest(),'X-GitHub-Delivery':delivery,'X-GitHub-Event':'issues'}
    def test_webhook_signed_and_replay(self):
        raw=json.dumps({'repository':{'full_name':'owner/repo'},'action':'opened','issue':{'title':'Review test','body':'Not complete'}}).encode()
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'inbox.sqlite3')
            self.assertEqual(ingest(raw,self.signed(raw),'test-secret',{'owner/repo'},db)[0],202)
            self.assertEqual(ingest(raw,self.signed(raw),'test-secret',{'owner/repo'},db)[0],409)
            self.assertEqual(os.stat(db).st_mode & 0o777,0o600)
    def test_webhook_invalid(self):
        self.assertEqual(ingest(b'{}',{},'secret',{'a/b'},'unused')[0],401)
    def test_webhook_scope(self):
        raw=json.dumps({'repository':{'full_name':'other/repo'}}).encode()
        self.assertEqual(ingest(raw,self.signed(raw),'test-secret',{'owner/repo'},'unused')[0],403)
    def test_webhook_bad_envelope(self):
        self.assertEqual(ingest(b'[]',self.signed(b'[]'),'test-secret',{'owner/repo'},'unused')[0],400)

if __name__ == '__main__': unittest.main()
