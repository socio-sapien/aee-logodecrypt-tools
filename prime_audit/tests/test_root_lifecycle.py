import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from prime_audit import lifecycle
from prime_audit.engine import protected
from prime_audit.full import audit_full
from prime_audit.hook import ROOT

class RootLifecycleTests(unittest.TestCase):
    def test_root_version_and_protected_controls(self):
        p=subprocess.run([sys.executable,str(ROOT/'PRIME_6_7.py'),'--version'],capture_output=True,text=True,check=True)
        self.assertIn('6.7.0',p.stdout)
        for name in ('PRIME_6_7.py','PRIME_PROTOCOL.md','AGENTS.md'):
            self.assertTrue(protected(name))
    def test_each_lifecycle_event_hash_receipt_no_raw_text(self):
        for kind in lifecycle.EVENTS:
            with tempfile.TemporaryDirectory() as tmp:
                gitdir=Path(tmp)
                event={'sessionId':'control-session','prompt':'synthetic-private-control-XYZ','transformedPrompt':'synthetic-private-control-XYZ','toolResult':{'textResultForLlm':'test result'}}
                with patch('prime_audit.lifecycle.repository_git_dir',return_value=gitdir):
                    result=lifecycle.process(kind,event)
                saved=(gitdir/'prime-audit/lifecycle.jsonl').read_text()
                self.assertNotIn('synthetic-private-control-XYZ',saved)
                record=json.loads(saved)
                self.assertEqual(record['event'],kind)
                self.assertEqual(record['full_battery']['inputs'][0]['version'],'6.7.0')
                self.assertIn('receipt',str(result))
    def test_invalid_lifecycle_event_is_rejected(self):
        with self.assertRaises(ValueError): lifecycle.process('made-up',{})
        with self.assertRaises(ValueError): lifecycle.process('postToolUse',[])
    def test_full_battery_uses_agent_domain_and_records_performance(self):
        r=audit_full('Inspect actual repository instructions before execution.')
        self.assertEqual(r['version'],'6.7.0')
        self.assertIn('logical_action_cue_ledger_and_ranked_index',r['report'])
    def test_lifecycle_symlink_receipt_directory_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'outside').mkdir(); (root/'prime-audit').symlink_to(root/'outside')
            with patch('prime_audit.lifecycle.repository_git_dir',return_value=root):
                with self.assertRaises(ValueError): lifecycle.process('postToolUse',{})

    def test_compatibility_text_endpoint_runs_67_full_battery(self):
        from prime_audit.mcp_server import dispatch
        r=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_audit_text','arguments':{'text':'Check actual outcomes before claiming success.'}}})
        self.assertFalse(r['result']['isError'])
        out=json.loads(r['result']['content'][0]['text'])
        self.assertEqual(out['version'],'6.7.0')
        self.assertIn('logical_action_cue_ledger_and_ranked_index',out['report'])
