import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aee_daemon import AEEDaemon

class FileSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.i, self.o, self.l = root/'in', root/'out', root/'logs'
        self.d = AEEDaemon(str(self.i), str(self.o), str(self.l))
        self.src = self.i/'example.txt'
        self.src.write_text('synthetic example email x@example.com', encoding='utf8')
        self.out = self.o/'sanitized_example.txt'
        self.log = self.l/'audit_example.txt.json'
    def tearDown(self): self.temp.cleanup()
    def test_preserves_input_and_output_contract(self):
        before=self.src.read_bytes()
        self.assertTrue(self.d.process_file(str(self.src)))
        self.assertEqual(before,self.src.read_bytes())
        self.assertTrue(self.out.exists()); self.assertEqual(json.loads(self.log.read_text())['source_file'],'example.txt')
    def test_output_collision_preserved(self):
        self.out.write_text('sentinel')
        self.assertFalse(self.d.process_file(str(self.src)))
        self.assertEqual(self.out.read_text(),'sentinel'); self.assertTrue(self.src.exists()); self.assertFalse(self.log.exists())
    def test_log_collision_leaves_empty_output(self):
        self.log.write_text('sentinel')
        self.assertFalse(self.d.process_file(str(self.src)))
        self.assertEqual(self.log.read_text(),'sentinel'); self.assertTrue(self.src.exists()); self.assertEqual(self.out.read_bytes(),b'')
    def test_ordinary_write_failure_preserves_partial_outputs(self):
        with patch('aee_daemon.json.dump', side_effect=OSError('synthetic failure')):
            self.assertFalse(self.d.process_file(str(self.src)))
        self.assertTrue(self.src.exists()); self.assertTrue(self.out.exists()); self.assertTrue(self.log.exists())
    def test_unchanged_input_not_processed_twice(self):
        self.d.run_poll(interval=0, max_iterations=3)
        before=(self.out.read_bytes(),self.log.read_bytes())
        self.assertFalse(self.d.process_file(str(self.src)))
        self.assertEqual(before,(self.out.read_bytes(),self.log.read_bytes()))
    def test_changed_input_refuses_collision(self):
        self.assertTrue(self.d.process_file(str(self.src)))
        before=(self.out.read_bytes(),self.log.read_bytes())
        self.src.write_text('different synthetic input',encoding='utf8')
        self.assertFalse(self.d.process_file(str(self.src)))
        self.assertEqual(before,(self.out.read_bytes(),self.log.read_bytes()))
        self.assertEqual(self.src.read_text(),'different synthetic input')
    def test_restart_refuses_collision(self):
        self.assertTrue(self.d.process_file(str(self.src)))
        d2=AEEDaemon(str(self.i),str(self.o),str(self.l))
        self.assertFalse(d2.process_file(str(self.src)))
        self.assertTrue(self.src.exists())
    def test_symlink_existing_output_not_followed(self):
        target=self.o/'other.txt'; target.write_text('sentinel')
        self.out.symlink_to(target)
        self.assertFalse(self.d.process_file(str(self.src)))
        self.assertEqual(target.read_text(),'sentinel'); self.assertTrue(self.src.exists()); self.assertFalse(self.log.exists())
    def test_output_inside_watch_refused(self):
        with self.assertRaises(ValueError):
            AEEDaemon(str(self.i), str(self.i / "out"), str(self.l))
        with self.assertRaises(ValueError):
            AEEDaemon(str(self.i), str(self.o), str(self.i))
    def test_redaction_is_not_general(self):
        clean=self.d.cleaner.clean_text('Synthetic Name: Alice Example; IPv6: 2001:db8::1; password=example-secret', aggressive=True)
        self.assertIn('Alice Example',clean)
        self.assertIn('2001:db8::1',clean)
        self.assertIn('example-secret',clean)

if __name__ == '__main__': unittest.main()
