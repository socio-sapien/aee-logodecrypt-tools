#!/usr/bin/env python3
import unittest
import os
import shutil
from aee_daemon import AEEDaemon
from aee_sanitizer import InvasiveMetadataCleaner

class TestAEEDaemon(unittest.TestCase):
    def test_sanitizer(self):
        cleaner = InvasiveMetadataCleaner()
        dirty = "User at 192.168.1.1 with key sk-1234567890123456789012 in Fargo said hello.\u200b"
        cleaned = cleaner.clean_text(dirty)
        self.assertNotIn("192.168.1.1", cleaned)
        self.assertNotIn("sk-1234567890123456789012", cleaned)
        self.assertNotIn("Fargo", cleaned)
        self.assertNotIn("\u200b", cleaned)

    def test_daemon_batch(self):
        test_in = "./test_watch_in"
        test_out = "./test_watch_out"
        test_logs = "./test_watch_logs"
        daemon = AEEDaemon(watch_dir=test_in, out_dir=test_out, log_dir=test_logs)
        sample_path = os.path.join(test_in, "sample.txt")
        with open(sample_path, "w") as f:
            f.write("We computed the total sum and verified the result.")
        daemon.run_poll(interval=0.1, max_iterations=1)
        self.assertTrue(os.path.exists(os.path.join(test_out, "sanitized_sample.txt")))
        self.assertTrue(os.path.exists(os.path.join(test_logs, "audit_sample.txt.json")))
        shutil.rmtree(test_in, ignore_errors=True)
        shutil.rmtree(test_out, ignore_errors=True)
        shutil.rmtree(test_logs, ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
