import unittest
from unittest.mock import patch
from prime_audit import seven_roles as s
from prime_audit.role_lexicons import cue_ledger

class SevenRoleTests(unittest.TestCase):
    def test_seven_distinct_profiles_and_scenarios(self):
        self.assertEqual(len(s.ROLES),7)
        self.assertEqual(set(s.ROLES),set(s.SCENARIOS))
        self.assertTrue(all(len(r['pairs']) >= 4 for r in s.ROLES.values()))
    def test_each_adversarial_scenario(self):
        result=s.run()
        self.assertEqual(result['agent_sessions_started'],0)
        self.assertEqual(result['executed_operations'],0)
        for scenario in result['roles']:
            with self.subTest(role=scenario['role']): self.assertTrue(scenario['passed'], scenario)
    def test_cue_ledger_reports_literal_counts_only(self):
        row=cue_ledger('Hear, listen, hear; do not overlook.')['perception']['pairs']
        self.assertEqual(next(x for x in row if x['verb']=='hear')['verb_count'],2)
        self.assertEqual(next(x for x in row if x['contrast']=='overlook')['contrast_count'],1)
        with self.assertRaises(ValueError): cue_ledger('x'*65537)
    def test_regression_or_error_is_not_reported_as_pass(self):
        with patch.dict(s.SCENARIOS, {'protocol': lambda: False}):
            result=s.run()
            self.assertFalse(next(x for x in result['roles'] if x['role']=='protocol')['passed'])
        def failure(): raise RuntimeError('unsafe detail not recorded')
        with patch.dict(s.SCENARIOS, {'boundary':failure}):
            result=s.run(); case=next(x for x in result['roles'] if x['role']=='boundary')
            self.assertFalse(case['passed']); self.assertEqual(case['error_type'],'RuntimeError')

if __name__ == '__main__': unittest.main()
