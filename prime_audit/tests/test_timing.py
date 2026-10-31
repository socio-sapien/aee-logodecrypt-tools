import unittest
from prime_audit.timing import Timing

class TemporalTests(unittest.TestCase):
    def test_measures_each_stage_and_reports_breach(self):
        ticks = iter([0, 100, 7_000_101, 8_000_000])
        t = Timing(clock=lambda: next(ticks))
        start = t.clock(); t.mark("triage", start); r = t.record()
        self.assertFalse(r["stages"][0]["within_target"])
        self.assertFalse(r["within_target"])
        self.assertEqual(r["target_kind"], "advisory")
    def test_invalid_target(self):
        for v in (0, -1, True, 2.5):
            with self.subTest(v=v), self.assertRaises(ValueError): Timing(v)
    def test_measured_seven_roles(self):
        from prime_audit.seven_roles import run
        result=run()
        self.assertEqual(len(result['timing']['stages']),7)
        self.assertTrue(all(x['passed'] for x in result['roles']))

if __name__ == '__main__': unittest.main()
