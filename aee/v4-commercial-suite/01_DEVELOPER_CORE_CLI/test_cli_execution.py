import json
import subprocess
import sys
import unittest
from pathlib import Path

CLI = Path(__file__).with_name("aee_cli.py")

class CLIExecutionTests(unittest.TestCase):
    def invoke(self, *args, input_text=None):
        return subprocess.run([sys.executable, str(CLI), *args], input=input_text, text=True, capture_output=True, check=True)

    def test_text_json(self):
        result = json.loads(self.invoke("--text", "we verified the result", "--json").stdout)
        self.assertEqual(result["WORDS"], 4)
        self.assertEqual(result["S"], 2)

    def test_stdin_json_is_machine_readable(self):
        run = self.invoke("--json", input_text="potentially")
        self.assertEqual(json.loads(run.stdout)["D_TERMS"], ["potentially"])
        self.assertIn("Reading from stdin", run.stderr)

    def test_text_human_output(self):
        run = self.invoke("--text", "verified result")
        self.assertIn("AEE v4.0 AUDIT RECORD", run.stdout)
        self.assertIn("VERDICT", run.stdout)

    def test_file_json(self):
        sample = CLI.parent / "sample_inputs" / "objective_mathematical_text.txt"
        output = json.loads(self.invoke("--file", str(sample), "--json").stdout)
        self.assertGreater(output["WORDS"], 0)

if __name__ == "__main__":
    unittest.main()
