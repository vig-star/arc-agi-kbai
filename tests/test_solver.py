"""End-to-end regressions for exact planning, bounds, and generalization."""

import copy
import unittest
from unittest.mock import patch

from arc_agi_kbai.grid import apply_action, execute_actions, make_grid
from arc_agi_kbai.solver import SearchConfig, plan, solve_task


class InputOnlyTestPair(dict):
    """Fail immediately if inference tries to consult a test answer."""

    def __getitem__(self, key):
        if key == "output":
            raise AssertionError("Inference accessed a held-out test label")
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "output":
            raise AssertionError("Inference accessed a held-out test label")
        return super().get(key, default)


class SolverTests(unittest.TestCase):
    def setUp(self):
        self.initial = [[1, 2, 3], [4, 5, 6]]
        self.goal = [[4, 0], [5, 2], [6, 3]]

    def test_identity_and_failed_search_have_distinct_results(self):
        self.assertEqual(plan(self.initial, self.initial), ())
        self.assertIsNone(plan(self.initial, self.goal, SearchConfig(max_depth=1)))

    def test_multistep_plan_exactly_reaches_target(self):
        original = copy.deepcopy(self.initial)
        program = plan(self.initial, self.goal, SearchConfig(max_depth=2))
        self.assertIsNotNone(program)
        self.assertEqual(len(program), 2)
        self.assertEqual(execute_actions(self.initial, program), make_grid(self.goal))
        self.assertEqual(self.initial, original)

    def test_generation_budget_bounds_every_attempted_action(self):
        with patch("arc_agi_kbai.solver.apply_action", wraps=apply_action) as operation:
            result = plan(self.initial, self.goal, SearchConfig(max_generated=2))
        self.assertIsNone(result)
        self.assertEqual(operation.call_count, 2)

    def test_search_state_and_resource_budgets_are_isolated(self):
        config = SearchConfig(max_depth=2)
        first = plan(self.initial, self.goal, config)
        self.assertIsNotNone(first)
        self.assertIsNone(plan(self.initial, self.goal, SearchConfig(max_generated=1)))
        plan([[1, 2], [3, 4]], [[4, 3], [2, 1]], config)
        second = plan(self.initial, self.goal, config)
        self.assertEqual(first, second)
        self.assertEqual(execute_actions(self.initial, second), make_grid(self.goal))

    def test_programs_must_match_every_demonstration(self):
        task = {"train": [
            {"input": [[1, 1], [1, 1]], "output": [[2, 2], [2, 2]]},
            {"input": [[3, 3], [3, 3]], "output": [[4, 4], [4, 4]]}],
            "test": [{"input": [[1, 3], [3, 1]]}]}
        result = solve_task(task, SearchConfig(max_depth=1))
        self.assertEqual(result["candidate_programs"], 2)
        self.assertEqual(result["consistent_programs"], 0)
        self.assertTrue(result["explanations"][0]["fallback"])
        self.assertEqual(result["attempts"][0]["attempt_1"], task["test"][0]["input"])

    def test_invalid_transferred_program_falls_back_to_valid_input(self):
        task = {"train": [
            {"input": [[1, 2, 3], [4, 5, 6]], "output": [[1, 2, 3]]},
            {"input": [[2, 4], [6, 8]], "output": [[2, 4]]}],
            "test": [{"input": [[9, 8, 7]]}]}
        result = solve_task(task)
        self.assertEqual(result["consistent_programs"], 1)
        self.assertTrue(result["explanations"][0]["fallback"])
        self.assertEqual(result["attempts"][0],
                         {"attempt_1": [[9, 8, 7]], "attempt_2": [[9, 8, 7]]})

    def test_deterministic_predictions_without_test_label_access(self):
        task = {"train": [
            {"input": [[1, 2, 3], [4, 5, 6]], "output": [[4, 1], [5, 2], [6, 3]]},
            {"input": [[7, 0], [8, 9]], "output": [[8, 7], [9, 0]]}],
            "test": [InputOnlyTestPair(input=[[2, 0, 1], [0, 3, 0]], output=[[9]])]}
        first = solve_task(task)
        task["test"][0]["output"] = [[1, 2, 3, 4]]
        second = solve_task(task)
        del task["test"][0]["output"]
        third = solve_task(task)
        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual(first["attempts"][0]["attempt_1"], [[0, 2], [3, 0], [0, 1]])
        self.assertFalse(first["explanations"][0]["fallback"])

    def test_learned_identity_is_reported_as_a_program(self):
        task = {"train": [{"input": [[1, 2]], "output": [[1, 2]]}],
                "test": [{"input": [[3, 4]]}]}
        result = solve_task(task)
        self.assertEqual(result["consistent_programs"], 1)
        self.assertFalse(result["explanations"][0]["fallback"])
        self.assertEqual(result["explanations"][0]["programs"], [[]])
        self.assertEqual(result["attempts"][0]["attempt_1"], [[3, 4]])

    def test_config_rejects_invalid_resource_limits(self):
        for field in ("beam_width", "max_depth", "max_generated", "max_sideways"):
            for value in (0, -1, True, 1.5, "2"):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    SearchConfig(**{field: value})
        self.assertEqual(SearchConfig(1, 1, 1, 1).max_generated, 1)

    def test_invalid_tasks_and_grids_fail_before_search(self):
        for task in ({}, {"train": [], "test": [{"input": [[1]]}]},
                     {"train": [{"input": [[1]], "output": [[1]]}], "test": []}):
            with self.subTest(task=task), self.assertRaises(ValueError):
                solve_task(task)
        with self.assertRaises(ValueError):
            plan([[]], [[1]])
        with self.assertRaises(ValueError):
            solve_task({"train": [{"input": [[1]], "output": [[1]]}],
                        "test": [{"input": [[True]]}]})


if __name__ == "__main__":
    unittest.main()
