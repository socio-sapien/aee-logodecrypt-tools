import contextlib
import io
import json
import threading
import unittest
from prime_audit.timing import monitored

class MonitorTests(unittest.TestCase):
    def test_while_running_then_completion(self):
        entered=threading.Event(); release=threading.Event(); output=io.StringIO()
        @monitored('controlled_test', target_ns=1_000_000)
        def work():
            entered.set(); release.wait(2); return 42
        result=[]
        with contextlib.redirect_stderr(output):
            worker=threading.Thread(target=lambda: result.append(work())); worker.start()
            self.assertTrue(entered.wait(1))
            # Poll the in-memory event only in this test, not the provider.
            import time
            for _ in range(100):
                if 'deadline_exceeded' in output.getvalue(): break
                time.sleep(.002)
            self.assertIn('deadline_exceeded',output.getvalue())
            self.assertTrue(worker.is_alive())
            release.set(); worker.join(2)
        self.assertEqual(result,[42])
        events=[json.loads(x) for x in output.getvalue().splitlines()]
        self.assertEqual([x['event'] for x in events],['deadline_exceeded','completed'])
        self.assertTrue(all(x['stage']=='controlled_test' for x in events))
    def test_exception_is_not_swallowed_and_secrets_not_logged(self):
        @monitored('exception_case')
        def work(secret): raise RuntimeError(secret)
        output=io.StringIO()
        with contextlib.redirect_stderr(output):
            with self.assertRaises(RuntimeError): work('PRIVATE_SENTINEL')
        self.assertNotIn('PRIVATE_SENTINEL',output.getvalue())
        self.assertIn('completed',output.getvalue())

if __name__=='__main__': unittest.main()
