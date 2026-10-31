import unittest
from prime_audit import harness
from prime_audit.mcp_server import dispatch

OP = {'action': 'test', 'paths': ['README.md'], 'expected_observation': 'pass'}

class HarnessTests(unittest.TestCase):
    def test_default_cells_are_unknown(self):
        m = harness.matrix([])
        self.assertEqual(len(m['cells']), 16)
        self.assertTrue(all(c['state'] == 'unknown' for c in m['cells']))
    def test_observations_are_exact_and_never_infer_intent(self):
        row = {'remedy':'fix', 'lens':'conceptual', 'state':'supported', 'evidence_refs':['test:1']}
        m = harness.matrix([row]); self.assertEqual(m['cells'][0]['evidence_refs'], ['test:1'])
        self.assertEqual(sum(x['state']=='supported' for x in m['cells']), 1)
        with self.assertRaises(ValueError): harness.matrix([row,row])
        with self.assertRaises(ValueError): harness.matrix([{**row,'evidence_refs':[]}])
    def test_no_executor_means_no_effect(self):
        result = harness.run(OP)
        self.assertEqual(result['execution']['status'], 'not_run')
        self.assertEqual(result['verification']['status'], 'not_run')
    def test_executor_and_independent_verifier(self):
        result = harness.run(OP, executor=lambda _: {'exit': 0}, verifier=lambda v: v['exit']==0)
        self.assertEqual(result['execution']['status'], 'returned')
        self.assertEqual(result['verification']['status'], 'verified')
    def test_review_blocks_callback(self):
        called=[]
        result = harness.run({'action':'deploy','paths':[]}, executor=lambda _: called.append(1))
        self.assertEqual(result['execution']['status'], 'blocked_by_preflight')
        self.assertEqual(called, [])
    def test_failures_are_not_success(self):
        def bad(_): raise RuntimeError('secret should not be logged')
        result = harness.run(OP, executor=bad)
        self.assertEqual(result['execution'], {'status':'outcome_unknown', 'error_type':'RuntimeError'})
        result = harness.run(OP, executor=lambda _: {}, verifier=lambda _: False)
        self.assertEqual(result['verification']['status'], 'failed')
        result = harness.run(OP, executor=lambda _: {}, verifier=lambda _: 'yes')
        self.assertEqual(result['verification']['status'], 'error')
    def test_tampered_simulation_is_rejected(self):
        with self.assertRaises(ValueError):
            harness.preflight(OP, simulation_fn=lambda _: {'decision': 'READY_FOR_BOUNDED_REVIEW', 'receipt': {'sha256': '0'*64}})
    def test_preflight_has_advisory_target(self):
        pre = harness.preflight(OP)
        self.assertEqual(pre['target_ns'], 7_000_000)
        self.assertFalse(pre['executed']); self.assertTrue(pre['timing_is_observational'])
    def test_mcp_is_readonly_and_no_executor(self):
        import json
        x=dispatch({'id':1,'method':'tools/call','params':{'name':'prime_investigate','arguments':{'operation':OP}}})
        obj=json.loads(x['result']['content'][0]['text'])
        self.assertEqual(obj['execution']['status'], 'not_run')

if __name__ == '__main__': unittest.main()

class HarnessChainTests(unittest.TestCase):
    def test_seven_role_fixture_chain(self):
        from prime_audit.harness_demo import demonstration
        result = demonstration()
        self.assertTrue(result['passed'])
        self.assertEqual(len(result['steps']), 7)
        self.assertEqual(result['live_agent_sessions'], 0)
        self.assertTrue(all(s['verification'] == 'verified' for s in result['steps']))
