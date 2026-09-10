"""Scoring regressions, including the preserved 2024 submission."""

import json
import unittest
from pathlib import Path

from arc_agi_kbai.evaluation import score_submission

ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    def test_task_weighting_and_two_attempts(self):
        solutions = {"a": [[[1]], [[2]]], "b": [[[3]]]}
        submission = {"a": [{"attempt_1": [[0]], "attempt_2": [[1]]},
                            {"attempt_1": [[0]], "attempt_2": [[0]]}],
                      "b": [{"attempt_1": [[3]], "attempt_2": [[3]]}]}
        result = score_submission(submission, solutions)
        self.assertEqual(result["task_normalized_score"], 1.5)
        self.assertEqual(result["task_normalized_percent"], 75)
        self.assertEqual(result["fully_solved_tasks"], 1)
        self.assertEqual(result["correct_test_grids"], 2)
        self.assertEqual(result["total_test_grids"], 3)

    def test_missing_attempts_and_tasks_count_as_incorrect(self):
        result = score_submission({"a": [{}]}, {"a": [[[1]]], "b": [[[2]]]})
        self.assertEqual(result["task_normalized_score"], 0)

    def test_invalid_predictions_never_match(self):
        for grid in ([[True]], [[1.0]], [], [[]], [[1], [1, 1]]):
            with self.subTest(grid=grid):
                result = score_submission({"a": [{"attempt_1": grid}]}, {"a": [[[1]]]})
                self.assertEqual(result["task_normalized_score"], 0)

    def test_wrong_dataset_and_malformed_records_fail(self):
        cases = [({"unknown": []}, {"a": [[[1]]]}),
                 ({"a": [{}, {}]}, {"a": [[[1]]]}),
                 ({"a": [None]}, {"a": [[[1]]]}),
                 ({}, {}), ({}, {"a": []}), ({}, {"a": [[[True]]]})]
        for submission, solutions in cases:
            with self.subTest(submission=submission), self.assertRaises(ValueError):
                score_submission(submission, solutions)

    def test_historical_saved_submission_score(self):
        submission = json.loads((ROOT / "archive/2024/submission.json").read_text())
        solutions = json.loads((ROOT / "data/arc-agi_evaluation_solutions.json").read_text())
        result = score_submission(submission, solutions)
        self.assertEqual(result["task_normalized_score"], 7.5)
        self.assertEqual(result["fully_solved_tasks"], 7)
        self.assertEqual(result["correct_test_grids"], 9)
        self.assertEqual(result["total_test_grids"], 419)
