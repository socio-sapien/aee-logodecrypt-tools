import contextlib
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from prime_audit import hook
from prime_audit.mcp_server import dispatch
from prime_audit.webhook import ingest

class HardeningTests(unittest.TestCase):
    def test_repo_local_sensitive_symlinks_denied_for_reads_and_edits(self):
        with tempfile.TemporaryDirectory(dir=hook.ROOT) as d:
            base = Path(d)
            for name in ('.env', 'credentials.json', 'private.key'):
                target = base / name
                target.write_text('placeholder')
                link = base / ('link-' + name.replace('.', '-'))
                link.symlink_to(target)
                for tool in ('view', 'write_file'):
                    self.assertEqual(hook.decision({'toolName': tool, 'toolArgs': {'path': str(link)}})['permissionDecision'], 'deny')
            safe = base / 'safe.txt'; safe.write_text('ok')
            alias = base / 'alias'; alias.symlink_to(safe)
            self.assertEqual(hook.decision({'toolName': 'view', 'toolArgs': {'path': str(alias)}})['permissionDecision'], 'allow')

    def test_hook_recording_failure_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / '.git').mkdir()
            event = json.dumps({'toolName': 'view', 'toolArgs': {'path': 'README.md'}})
            output = io.StringIO()
            with patch.object(hook, 'ROOT', root), patch.object(hook.os, 'open', side_effect=OSError('record failed')), patch('sys.stdin', io.StringIO(event)), contextlib.redirect_stdout(output):
                hook.main()
            self.assertEqual(json.loads(output.getvalue())['permissionDecision'], 'deny')

    def headers(self, raw, delivery='a', kind='issues'):
        return {'X-Hub-Signature-256': 'sha256=' + hmac.new(b'secret', raw, hashlib.sha256).hexdigest(), 'X-GitHub-Delivery': delivery, 'X-GitHub-Event': kind}

    def payload(self, title='hello'):
        return json.dumps({'repository': {'full_name':'owner/repo'}, 'action':'opened', 'issue':{'title':title}}).encode()

    def test_duplicate_body_different_delivery_and_distinct_body(self):
        with tempfile.TemporaryDirectory() as d:
            db = str(Path(d)/'inbox.db'); raw = self.payload(); different = self.payload('new')
            self.assertEqual(ingest(raw,self.headers(raw,'one'),'secret',{'owner/repo'},db)[0],202)
            self.assertEqual(ingest(raw,self.headers(raw,'two'),'secret',{'owner/repo'},db)[0],409)
            self.assertEqual(ingest(different,self.headers(different,'one'),'secret',{'owner/repo'},db)[0],409)
            self.assertEqual(ingest(different,self.headers(different,'three'),'secret',{'owner/repo'},db)[0],202)
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute('select count(*) from inbox').fetchone()[0],2)
                self.assertEqual(conn.execute('select count(*) from payload_fingerprints').fetchone()[0],2)

    def test_concurrent_identical_payloads_queue_once(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'inbox.db'); raw=self.payload()
            def request(delivery):
                return ingest(raw,self.headers(raw,delivery),'secret',{'owner/repo'},db)[0]
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes=list(pool.map(request, ('one', 'two')))
            self.assertEqual(sorted(outcomes), [202,409])
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute('select count(*) from inbox').fetchone()[0],1)

    def test_existing_inbox_hash_backfill(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'inbox.db'); raw=self.payload(); sha=hashlib.sha256(raw).hexdigest()
            with sqlite3.connect(db) as conn:
                conn.execute('CREATE TABLE inbox (delivery TEXT PRIMARY KEY, receipt TEXT NOT NULL)')
                conn.execute('INSERT INTO inbox VALUES (?, ?)', ('old', json.dumps({'payload_sha256':sha})))
            self.assertEqual(ingest(raw,self.headers(raw,'fresh'),'secret',{'owner/repo'},db)[0],409)
            fresh=self.payload('genuinely different')
            self.assertEqual(ingest(fresh,self.headers(fresh,'new'),'secret',{'owner/repo'},db)[0],202)
            self.assertEqual(ingest(raw,self.headers(raw,'another'),'secret',{'owner/repo'},db)[0],409)

    def test_malformed_webhook_objects_and_db_failure(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/'inbox.db')
            for obj in ({'repository':None}, {'repository':{'full_name':'owner/repo'},'action':'opened','issue':[]}, {'repository':{'full_name':'owner/repo'},'action':'opened','issue':None}):
                raw=json.dumps(obj).encode()
                self.assertEqual(ingest(raw,self.headers(raw),'secret',{'owner/repo'},db)[0],400)
            raw=self.payload()
            self.assertEqual(ingest(raw,self.headers(raw),'secret',{'owner/repo'},d)[0],503)

    def test_malformed_mcp_args_return_errors(self):
        for args in (None, [], 'bad', {'text': 5}, {'text':'ok','extra':1}):
            msg={'id':1,'method':'tools/call','params':{'name':'prime_audit_text','arguments':args}}
            self.assertTrue(dispatch(msg)['result']['isError'])
        r=dispatch({'id':1,'method':'initialize','params':{'protocolVersion':[]}})
        self.assertEqual(r['result']['protocolVersion'],'2024-11-05')

if __name__ == '__main__':
    unittest.main()
