"""Exact-match scoring compatible with the archived two-attempt course format."""

from .grid import make_grid


def _matches(prediction, answer):
    try:
        return make_grid(prediction) == answer
    except ValueError:
        return False


def score_submission(submission: dict, solutions: dict) -> dict:
    """Score each task as its fraction of exactly solved test grids.

    Missing tasks/attempts count as incorrect. Extra task IDs are rejected to
    catch mismatched files. Historical invalid grids simply score as incorrect.
    """
    if not isinstance(solutions, dict) or not solutions:
        raise ValueError("Solutions must be a non-empty object keyed by task ID")
    if not isinstance(submission, dict):
        raise ValueError("Submission must be an object keyed by task ID")
    extra = set(submission) - set(solutions)
    if extra:
        raise ValueError(f"Submission contains task IDs missing from solutions: {sorted(extra)[:5]}")
    total_score = correct = total = fully_solved = 0
    per_task = {}
    for task_id, answers in solutions.items():
        if not isinstance(answers, list) or not answers:
            raise ValueError(f"Task {task_id} has no solution grids")
        attempts = submission.get(task_id, [])
        if not isinstance(attempts, list) or len(attempts) > len(answers):
            raise ValueError(f"Task {task_id} has an invalid number of prediction entries")
        task_correct = 0
        for i, answer in enumerate(answers):
            answer = make_grid(answer)
            entry = attempts[i] if i < len(attempts) else {}
            if not isinstance(entry, dict):
                raise ValueError(f"Task {task_id}, test {i}: attempts must be an object")
            task_correct += any(_matches(entry.get(f"attempt_{j}"), answer) for j in (1, 2))
        fraction = task_correct / len(answers)
        per_task[task_id] = fraction
        total_score += fraction
        correct += task_correct
        total += len(answers)
        fully_solved += task_correct == len(answers)
    return {"task_normalized_score": total_score,
            "task_normalized_percent": 100 * total_score / len(solutions),
            "tasks": len(solutions), "fully_solved_tasks": fully_solved,
            "correct_test_grids": correct, "total_test_grids": total,
            "per_task": per_task}
