import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from prime_audit import hook

class WorktreeHookTests(unittest.TestCase):
    def git(self, root, *args):
        return subprocess.run(['git', *args], cwd=root, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_normal_and_linked_worktree_record_allow(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'repo'; root.mkdir()
            self.git(root, 'init', '-q')
            self.git(root, 'config', 'user.email', 'test@example.invalid')
            self.git(root, 'config', 'user.name', 'Test')
            (root / 'README.md').write_text('source')
            self.git(root, 'add', 'README.md')
            self.git(root, 'commit', '-qm', 'initial')
            linked = Path(temp) / 'linked'
            self.git(root, 'worktree', 'add', '-qb', 'linked', str(linked))
            for checkout in [root, linked]:
                output = io.StringIO()
                with patch.object(hook, 'ROOT', checkout), patch('sys.stdin', io.StringIO(json.dumps({'toolName':'view','toolArgs':{'path':'README.md'}}))), contextlib.redirect_stdout(output):
                    hook.main()
                self.assertEqual(json.loads(output.getvalue())['permissionDecision'], 'allow')
                logfile = hook.repository_git_dir(checkout) / 'prime-audit' / 'decisions.jsonl'
                record = json.loads(logfile.read_text().splitlines()[-1])
                self.assertEqual(record['decision'], 'allow')

    def test_bad_worktree_backlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'checkout'; root.mkdir()
            gitdir = Path(temp) / 'repo' / '.git' / 'worktrees' / 'bad'; gitdir.mkdir(parents=True)
            (root / '.git').write_text('gitdir: ' + str(gitdir) + '\n')
            (gitdir / 'gitdir').write_text(str(Path(temp) / 'missing') + '\n')
            with self.assertRaises((ValueError, OSError)):
                hook.repository_git_dir(root)

if __name__ == '__main__':
    unittest.main()
