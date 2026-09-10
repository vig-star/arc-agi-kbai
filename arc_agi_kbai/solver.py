"""Bounded beam search and demonstration-validated program selection.

This maintained implementation follows the 2024 project's rule/search/replay
design. It is not a bit-for-bit reproduction of py_search.local_beam_search.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Optional, Tuple

from .grid import Action, Grid, apply_action, execute_actions, legal_actions, make_grid

Program = Tuple[Action, ...]


@dataclass(frozen=True)
class SearchConfig:
    beam_width: int = 5
    max_depth: int = 6
    max_generated: int = 20000
    max_sideways: int = 5

    def __post_init__(self):
        for name in ("beam_width", "max_depth", "max_generated", "max_sideways"):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer")


def mismatch(grid: Grid, goal: Grid) -> int:
    """Cell disagreement plus dimension penalties; not an admissible heuristic."""
    cells = sum(a != b for row, target in zip(grid, goal) for a, b in zip(row, target))
    dimensions = abs(len(grid) - len(goal)) * len(goal[0])
    dimensions += abs(len(grid[0]) - len(goal[0])) * len(goal)
    return cells + dimensions


def plan(input_grid, output_grid, config: Optional[SearchConfig] = None) -> Optional[Program]:
    """Return an exact program, () for identity, or None when search fails.

    The generation budget counts every attempted action, including invalid and
    duplicate results. Each pair has its own visited states and resource budget.
    """
    config = config or SearchConfig()
    initial, goal = make_grid(input_grid), make_grid(output_grid)
    if initial == goal:
        return ()
    beam = [(initial, ())]
    visited = {initial}
    generated = 0
    best_value = mismatch(initial, goal)
    stagnant = 0
    for depth in range(1, config.max_depth + 1):
        candidates = []
        for state, program in beam:
            for action in legal_actions(state):
                if generated >= config.max_generated:
                    return None
                generated += 1
                try:
                    successor = apply_action(state, action)
                except ValueError:
                    continue
                if successor in visited:
                    continue
                visited.add(successor)
                path = program + (action,)
                if successor == goal:
                    return path
                candidates.append((mismatch(successor, goal) + depth, successor, path))
        if not candidates:
            return None
        # Stable sorting preserves deterministic action-order tie breaking.
        candidates.sort(key=lambda item: item[0])
        current_best = candidates[0][0]
        stagnant = 0 if current_best < best_value else stagnant + 1
        best_value = min(best_value, current_best)
        if stagnant >= config.max_sideways:
            return None
        beam = [(state, path) for _, state, path in candidates[:config.beam_width]]
    return None


def _fits(program: Program, examples) -> bool:
    for pair in examples:
        try:
            if execute_actions(pair["input"], program) != make_grid(pair["output"]):
                return False
        except ValueError:
            return False
    return True


def solve_task(task: dict, config: Optional[SearchConfig] = None) -> dict:
    """Infer from demonstration pairs only and emit two attempts per test input.

    Exact pair solutions become candidates. Only candidates matching *every*
    demonstration survive. If none apply to a test grid, copy that input as an
    explicitly reported fallback. Test output labels are never read here.
    """
    if not isinstance(task, dict) or not task.get("train") or not task.get("test"):
        raise ValueError("Each task needs non-empty 'train' and 'test' lists")
    examples = task["train"]
    for pair in examples:
        make_grid(pair["input"])
        make_grid(pair["output"])
    test_inputs = [make_grid(pair["input"]) for pair in task["test"]]
    counts = Counter()
    for pair in examples:
        program = plan(pair["input"], pair["output"], config)
        if program is not None:
            counts[program] += 1
    programs = [p for p in counts if _fits(p, examples)]
    programs.sort(key=lambda p: (-counts[p], len(p), tuple(map(str, p))))
    attempts, explanations = [], []
    for grid in test_inputs:
        predictions, applied = [], []
        for program in programs:
            try:
                prediction = execute_actions(grid, program)
            except ValueError:
                continue
            if prediction not in predictions:
                predictions.append(prediction)
                applied.append([str(action) for action in program])
            if len(predictions) == 2:
                break
        fallback = not predictions
        if fallback:
            predictions = [grid]
        if len(predictions) == 1:
            predictions.append(predictions[0])
        attempts.append({f"attempt_{i + 1}": [list(row) for row in g]
                         for i, g in enumerate(predictions)})
        explanations.append({"programs": applied, "fallback": fallback})
    return {"attempts": attempts, "explanations": explanations,
            "candidate_programs": len(counts), "consistent_programs": len(programs)}
