"""CLI integration: inference, artifact output, and path collision protection."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from arc_agi_kbai.__main__ import main


class CliTests(unittest.TestCase):
    def test_solve_writes_predictions_and_program_report(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            challenges, output, report = [folder / f for f in ("tasks.json", "sub.json", "report.json")]
            challenges.write_text(json.dumps({"demo": {
                "train": [{"input": [[1]], "output": [[2]]}],
                "test": [{"input": [[1]]}, {"input": [[1], [1]]}]}}))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["solve", str(challenges), "--output", str(output),
                                       "--report", str(report)]), 0)
            predictions = json.loads(output.read_text())["demo"]
            self.assertEqual(predictions[0]["attempt_1"], [[2]])
            self.assertEqual(predictions[1]["attempt_2"], [[2], [2]])
            details = json.loads(report.read_text())
            self.assertEqual(details["task_count"], 1)
            self.assertFalse(details["tasks"]["demo"]["explanations"][0]["fallback"])

    def test_inference_does_not_overwrite_its_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "tasks.json"
            source.write_text("{}")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(["solve", str(source), "--output", str(source)])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(source.read_text(), "{}")

    def test_invalid_cli_budget_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["solve", "unused.json", "--max-generated", "0"])
        self.assertEqual(error.exception.code, 2)
