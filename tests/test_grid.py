"""Regression coverage for transformation semantics and ARC grid boundaries."""

import unittest

from arc_agi_kbai.grid import Action, apply_action, execute_actions, legal_actions, make_grid


class GridTests(unittest.TestCase):
    def test_grid_validation(self):
        invalid = [[], [[]], [[1], [2, 3]], [[True]], [[1.0]], [[-1]], [[10]],
                   [[0] * 31], [[0]] * 31, None, "12"]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(ValueError):
                make_grid(data)
        self.assertEqual(make_grid([[0, 9]]), ((0, 9),))

    def test_mirrors_have_distinct_axes(self):
        grid = make_grid([[1, 2, 3], [4, 5, 6]])
        self.assertEqual(apply_action(grid, Action("hmirror")), ((4, 5, 6), (1, 2, 3)))
        self.assertEqual(apply_action(grid, Action("vmirror")), ((3, 2, 1), (6, 5, 4)))
        for name in ("hmirror", "vmirror"):
            self.assertEqual(execute_actions(grid, [Action(name), Action(name)]), grid)

    def test_rectangular_rotations_and_round_trip(self):
        grid = make_grid([[1, 2, 3], [4, 5, 6]])
        expected = {90: ((4, 1), (5, 2), (6, 3)),
                    180: ((6, 5, 4), (3, 2, 1)),
                    270: ((3, 6), (2, 5), (1, 4))}
        for degrees, result in expected.items():
            self.assertEqual(apply_action(grid, Action("rotate", (degrees,))), result)
        self.assertEqual(execute_actions(grid, [Action("rotate", (90,))] * 4), grid)

    def test_flood_fill_connectivity_and_input_immutability(self):
        original = [[1, 0, 1], [1, 0, 0], [0, 1, 1]]
        result = execute_actions(original, [Action("flood_fill", (0, 0, 2))])
        self.assertEqual(result, ((2, 0, 1), (2, 0, 0), (0, 1, 1)))
        self.assertEqual(original, [[1, 0, 1], [1, 0, 0], [0, 1, 1]])
        uniform = make_grid([[0] * 30 for _ in range(30)])
        self.assertEqual(apply_action(uniform, Action("flood_fill", (0, 0, 9))),
                         make_grid([[9] * 30 for _ in range(30)]))
        self.assertEqual(apply_action(result, Action("flood_fill", (-1, 0, 3))), result)

    def test_compress_removes_uniform_rows_and_columns(self):
        grid = make_grid([[0, 0, 0, 0], [0, 1, 2, 0], [0, 3, 4, 0]])
        self.assertEqual(apply_action(grid, Action("compress")), ((1, 2), (3, 4)))

    def test_crop_is_inclusive_and_clipped(self):
        grid = make_grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertEqual(apply_action(grid, Action("crop", (1, 1, 2, 2))),
                         ((5, 6), (8, 9)))
        self.assertEqual(apply_action(grid, Action("crop", (-3, -2, 9, 9))), grid)

    def test_scale_preserves_nearest_neighbor_and_odd_dimension_behavior(self):
        grid = make_grid([[1, 2], [3, 4]])
        enlarged = apply_action(grid, Action("scale", (2,)))
        self.assertEqual(enlarged, ((1, 1, 2, 2), (1, 1, 2, 2),
                                    (3, 3, 4, 4), (3, 3, 4, 4)))
        self.assertEqual(apply_action(enlarged, Action("scale", (0.5,))), grid)
        self.assertEqual(execute_actions([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                         [Action("scale", (0.5,))]), ((1,),))

    def test_other_original_operations(self):
        grid = make_grid([[0, 1, 0, 2], [3, 0, 4, 0]])
        self.assertEqual(apply_action(grid, Action("lshift")), ((1, 2, 0, 0), (3, 4, 0, 0)))
        self.assertEqual(apply_action(grid, Action("tophalf")), ((0, 1, 0, 2),))
        self.assertEqual(apply_action(grid, Action("mapcolor", (0, 9))),
                         ((9, 1, 9, 2), (3, 9, 4, 9)))
        repeated = execute_actions([[1, 2], [3, 4]], [Action("pattern_repeat")])
        self.assertEqual(repeated, ((1, 2, 1, 2, 1, 2), (3, 4, 3, 4, 3, 4)) * 3)
        alternating = apply_action(repeated, Action("alternate_pattern"))
        self.assertEqual(alternating[2], (2, 1, 2, 1, 2, 1))
        self.assertEqual(alternating[4], repeated[4])
        odd = make_grid([[1, 2, 3]] * 3)
        self.assertEqual(apply_action(odd, Action("alternate_pattern"))[2], (2, 1, 3))

    def test_empty_and_oversized_outputs_are_rejected(self):
        cases = [([[1]], Action("tophalf")),
                 ([[1, 1], [1, 1]], Action("compress")),
                 ([[1, 2]], Action("scale", (0.5,))),
                 ([[1]], Action("crop", (2, 2, 4, 4))),
                 ([[0] * 16], Action("scale", (2,))),
                 ([[0] * 11], Action("pattern_repeat"))]
        for grid, action in cases:
            with self.subTest(action=action), self.assertRaises(ValueError):
                apply_action(make_grid(grid), action)

    def test_invalid_actions_fail_explicitly(self):
        invalid = [Action("unknown"), Action("rotate", (45,)), Action("scale", (0,)),
                   Action("scale", (True,)), Action("mapcolor", (0, 10)),
                   Action("mapcolor", (0,)), Action("hmirror", (1,)),
                   Action("crop", (0.0, 0, 1, 1)), Action("flood_fill", (0, 0, 10))]
        for action in invalid:
            with self.subTest(action=action), self.assertRaises(ValueError):
                apply_action(((1, 2), (3, 4)), action)

    def test_candidate_order_and_size_bounds(self):
        grid = make_grid([[2, 1]])
        first = list(legal_actions(grid))
        self.assertEqual(first, list(legal_actions(grid)))
        recolors = [action for action in first if action.name == "mapcolor"]
        self.assertEqual(recolors[0], Action("mapcolor", (1, 0)))
        self.assertEqual(len(set(first)), len(first))
        large = list(legal_actions(make_grid([[0] * 16 for _ in range(16)])))
        self.assertFalse(any(action.name in {"crop", "flood_fill", "pattern_repeat"}
                             for action in large))
        self.assertNotIn(Action("scale", (2,)), large)

    def test_action_arguments_are_immutable_and_identity_preserves_input(self):
        args = [0, 2]
        action = Action("mapcolor", args)
        args[1] = 9
        self.assertEqual(action.args, (0, 2))
        self.assertEqual(str(action), "mapcolor(0,2)")
        self.assertEqual(execute_actions([[1, 2]], []), ((1, 2),))


if __name__ == "__main__":
    unittest.main()
