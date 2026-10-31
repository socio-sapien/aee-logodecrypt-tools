import contextlib
import io
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

from prime_audit import engine, mcp_server, webhook


class CheckpointCoverageTests(unittest.TestCase):
    def test_hook_malformed_is_denied_and_request_timed(self):
        p = subprocess.run([sys.executable, '-m', 'prime_audit.hook'], input='{bad',
                           text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(p.stdout)['permissionDecision'], 'deny')
        events = [json.loads(line) for line in p.stderr.splitlines()]
        self.assertIn(('pre_tool_request', 'completed'),
                      [(event['stage'], event['event']) for event in events])
        self.assertNotIn('{bad', p.stderr)

    def test_mcp_invalid_request_has_elapsed_metadata(self):
        result = mcp_server.dispatch({'id': 1, 'method': 'tools/call',
                                      'params': {'name': 'unknown'}})['result']
        self.assertTrue(result['isError'])
        self.assertEqual(result['_meta']['prime_timing']['stages'][0]['stage'], 'mcp_tool')

    def test_direct_text_audit_emits_completion(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            engine.audit_text('example')
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertIn(('audit_text', 'completed'),
                      [(event['stage'], event['event']) for event in events])
        self.assertNotIn('example', output.getvalue())

    def test_webhook_early_rejection_is_timed(self):
        server = mock.Mock()
        with mock.patch.dict(os.environ, {'PRIME_WEBHOOK_SECRET': 'example',
                                         'PRIME_WEBHOOK_REPOSITORIES': 'a/b'}), \
             mock.patch.object(sys, 'argv', ['webhook']), \
             mock.patch.object(webhook, 'HTTPServer', return_value=server) as factory:
            webhook.main()
        handler_type = factory.call_args.args[1]
        handler = object.__new__(handler_type)
        handler.path = '/wrong'
        handler.send_error = mock.Mock()
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            handler.do_POST()
        handler.send_error.assert_called_once_with(404)
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertIn(('webhook_request', 'completed'),
                      [(event['stage'], event['event']) for event in events])

if __name__ == '__main__':
    unittest.main()
