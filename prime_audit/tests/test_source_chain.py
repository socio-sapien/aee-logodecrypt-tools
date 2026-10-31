import unittest
from prime_audit.source_chain import chain
from prime_audit.engine import MAX_TEXT

class SourceChainTest(unittest.TestCase):
    def test_every_role_receives_full_original_source_and_candidate(self):
        source = 'BEGIN ' + ('context ' * 300) + ' source says 12 units END'
        candidate = 'BEGIN report says 15 units ' + ('detail ' * 300) + ' END'
        calls = []
        def audit(text, original):
            calls.append((text, original))
            return {'source_length': len(original), 'text_length': len(text)}
        result = chain(source, candidate, audit)
        self.assertEqual(len(calls), 7)
        self.assertTrue(all(item == (candidate, source) for item in calls))
        self.assertEqual(len({item['role'] for item in result['roles']}), 7)
    def test_refuses_instead_of_truncating(self):
        with self.assertRaises(ValueError): chain('x' * (MAX_TEXT+1), 'candidate')
        with self.assertRaises(ValueError): chain('source', 'x' * (MAX_TEXT+1))
    def test_real_audit_sees_context_in_each_role(self):
        result = chain('Source says 12 units', 'Report says 15 units')
        self.assertEqual(len(result['roles']), 7)
        self.assertTrue(all(x['result']['context_fidelity']['status'] == 'REVIEW-CUES' for x in result['roles']))
