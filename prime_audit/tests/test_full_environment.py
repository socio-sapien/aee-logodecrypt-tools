import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from prime_audit.full import audit_full, hook_audit, prime
from prime_audit.hook import ROOT, repository_git_dir
from prime_audit.mcp_server import dispatch

class FullEnvironmentTests(unittest.TestCase):
    def test_full_version_and_receipt(self):
        r=audit_full('If not approved, wait. 15 items.', 'If approved, run. 12 items.')
        self.assertEqual(r['version'],'6.7.0')
        self.assertTrue(prime.verify_report(r['report'], b'If not approved, wait. 15 items.')['input_source_match'])
        self.assertTrue(r['report']['per_word_dynamics_and_slot_permutation']['configured'])
        self.assertIn('logical_action_cue_ledger_and_ranked_index',r['report'])

    def test_long_words_are_chunked_without_dropped_text(self):
        text=' '.join('word'+str(i) for i in range(300))
        r=audit_full(text); chunks=r['word_dynamics_chunks']
        self.assertEqual(len(chunks),3)
        self.assertEqual(''.join(text[c['start']:c['end']] for c in chunks),text)
        self.assertEqual(chunks[0]['start'],0)
        self.assertEqual(chunks[-1]['end'],len(text))

    def test_rejects_oversize_and_wrong_types(self):
        for text in (None, {}, 'x'*65537):
            with self.assertRaises(ValueError):audit_full(text)
        with self.assertRaises(ValueError):audit_full('x',{})

    def test_mcp_full_audit(self):
        r=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_full_audit','arguments':{'text':'actual instruction'}}})
        self.assertFalse(r['result']['isError'])
        full = json.loads(r['result']['content'][0]['text'])
        self.assertEqual(full['version'],'6.7.0')
        self.assertIn('surface_census', full)

    def test_invalid_mcp_arguments_not_executed(self):
        for args in ({'operation':{}},{'text':4},{'text':'x','invented':1}):
            r=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_full_audit','arguments':args}})
            self.assertTrue(r['result']['isError'])

    def test_hook_audits_actual_instructions_without_logging_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'AGENTS.md').write_text('unique-task-secret-543210')
            r=hook_audit({'toolName':'view','toolArgs':{'path':'README.md'}},root)
            self.assertEqual([x['input'] for x in r['inputs']],['tool-event','AGENTS.md'])
            self.assertEqual(r['inputs'][1]['input_sha256'],hashlib.sha256(b'unique-task-secret-543210').hexdigest())
            self.assertNotIn('unique-task-secret-543210',json.dumps(r))

    def test_hook_denies_if_full_battery_fails(self):
        from prime_audit.hook import main
        import io
        stdout=io.StringIO()
        with patch('prime_audit.hook.hook_audit',side_effect=ValueError('broken')),patch('sys.stdin',io.StringIO('{"toolName":"view","toolArgs":{"path":"README.md"}}')),patch('sys.stdout',stdout):
            main()
        self.assertEqual(json.loads(stdout.getvalue())['permissionDecision'],'deny')

    def test_hook_process_records_automatic_full_battery(self):
        r=subprocess.run([sys.executable,'-m','prime_audit.hook'],input=json.dumps({'toolName':'view','toolArgs':{'path':'README.md'}}),text=True,capture_output=True,check=True)
        payload = json.loads(r.stdout)
        try:
            git_dir = repository_git_dir(ROOT)
        except (ValueError, OSError):
            git_dir = None
        if git_dir is None:
            self.assertEqual(payload['permissionDecision'], 'deny')
            self.assertIn('could not validate or record', payload['permissionDecisionReason'])
        else:
            self.assertEqual(payload['permissionDecision'], 'allow')
            record = json.loads((git_dir / 'prime-audit/decisions.jsonl').read_text().splitlines()[-1])
            self.assertIn('full_battery', record)
            self.assertTrue(all(x['version'] == '6.7.0' for x in record['full_battery']['inputs']))

    def test_auto_discovery_configs_and_profiles_include_full_tool(self):
        cfg=json.loads((ROOT/'.github/mcp.json').read_text())
        self.assertIn('prime_full_audit',cfg['mcpServers']['prime-audit']['tools'])
        for p in (ROOT/'.github/agents').glob('*.agent.md'):
            self.assertIn('prime_full_audit',p.read_text())
