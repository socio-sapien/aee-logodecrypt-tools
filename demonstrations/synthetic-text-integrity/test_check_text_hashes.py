import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from check_text_hashes import check_rows

HERE = Path(__file__).resolve().parent
CLI = HERE / 'check_text_hashes.py'

def row(text):
    return {'text': text, 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}

class IntegrityTests(unittest.TestCase):
    def test_valid_unicode(self): self.assertEqual(check_rows([row('snow ☃\n')]), [])
    def test_bad_format(self): self.assertTrue(check_rows([{'text':'x','sha256':'g'*64}]))
    def test_uppercase_rejected(self):
        r = row('x'); r['sha256'] = r['sha256'].upper(); self.assertTrue(check_rows([r]))
    def test_wrong_digest(self):
        r = row('x'); r['sha256'] = '0'*64; self.assertTrue(check_rows([r]))
    def test_text_modified(self):
        r = row('x'); r['text'] = 'y'; self.assertTrue(check_rows([r]))
    def test_line_endings(self):
        r = row('a\nb'); r['text'] = 'a\r\nb'; self.assertTrue(check_rows([r]))
    def test_empty_list_or_nonlist(self):
        for value in ([], {}, None): self.assertTrue(check_rows(value))
    def test_bad_row_or_fields(self):
        for value in (None, {}, {'text':'', 'sha256':'0'*64}, {'text':'x','sha256':1}):
            self.assertTrue(check_rows([value]))
    def test_invalid_unicode(self): self.assertTrue(check_rows([{'text':'\ud800','sha256':'0'*64}]))
    def test_multiple_rows(self): self.assertEqual(check_rows([row('a'),row('b')]), [])
    def test_example_cli(self):
        result = subprocess.run([sys.executable, str(CLI), str(HERE / 'synthetic_records.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('2 row(s)', result.stdout)
    def test_missing_file(self):
        result = subprocess.run([sys.executable, str(CLI), str(HERE / 'not-present.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
    def test_no_input_text_in_errors(self):
        r = row('private test contents'); r['sha256'] = '0'*64
        self.assertNotIn('private test contents', str(check_rows([r])))

if __name__ == '__main__': unittest.main()
