import hashlib, tempfile, unittest
from pathlib import Path
from prime_audit.auto_repair import repair

def h(data): return hashlib.sha256(data).hexdigest()
class TestAutoRepair(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.file=self.root/'fixture.txt'; self.file.write_text('teh example')
        self.args=(self.root,'fixture.txt',h(b'teh example'),'teh','the',['fixture.txt'])
    def test_repairs_and_verifies(self):
        r=repair(*self.args,verify=lambda p:p.read_text()=='the example')
        self.assertEqual(r['status'],'verified'); self.assertEqual(self.file.read_text(),'the example')
    def test_failure_restores(self):
        r=repair(*self.args,verify=lambda p:False)
        self.assertEqual(r['status'],'rolled_back'); self.assertEqual(self.file.read_text(),'teh example')
    def test_verifier_error_restores(self):
        def fail(_): raise RuntimeError()
        self.assertEqual(repair(*self.args,verify=fail)['status'],'rolled_back')
    def test_concurrent_change_not_overwritten(self):
        def change(p): p.write_text('external edit'); return False
        r=repair(*self.args,verify=change)
        self.assertEqual(r['status'],'rollback_conflict'); self.assertEqual(self.file.read_text(),'external edit')
    def test_changed_hash_and_not_allowed(self):
        with self.assertRaises(ValueError): repair(self.root,'fixture.txt','0'*64,'teh','the',['fixture.txt'],lambda p:True)
        with self.assertRaises(ValueError): repair(*self.args[:-1],[],lambda p:True)
    def test_symlink_and_sensitive(self):
        (self.root/'link').symlink_to(self.file)
        with self.assertRaises(ValueError): repair(self.root,'link',h(b'teh example'),'teh','the',['link'],lambda p:True)
        (self.root/'.env').write_text('teh')
        with self.assertRaises(ValueError): repair(self.root,'.env',h(b'teh'),'teh','the',['.env'],lambda p:True)
    def test_ambiguous_literal(self):
        self.file.write_text('teh teh')
        with self.assertRaises(ValueError): repair(self.root,'fixture.txt',h(b'teh teh'),'teh','the',['fixture.txt'],lambda p:True)
