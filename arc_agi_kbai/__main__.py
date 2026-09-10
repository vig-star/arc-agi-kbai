"""Run a synthetic demonstration, predict ARC tasks, or rescore saved predictions."""

import argparse
import json
import sys
import time
from pathlib import Path

from .evaluation import score_submission
from .solver import SearchConfig, solve_task


def _read(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="Solve an included synthetic rotation task")
    solve = commands.add_parser("solve", help="Predict using only task demonstrations")
    solve.add_argument("challenges", type=Path)
    solve.add_argument("--output", type=Path, default=Path("outputs/submission.json"))
    solve.add_argument("--report", type=Path, help="Optional program traces and timing JSON")
    solve.add_argument("--limit", type=_positive, help="First N task IDs in sorted order")
    solve.add_argument("--beam-width", type=_positive, default=5)
    solve.add_argument("--max-depth", type=_positive, default=6)
    solve.add_argument("--max-generated", type=_positive, default=20000)
    solve.add_argument("--max-sideways", type=_positive, default=5)
    score = commands.add_parser("score", help="Score a saved two-attempt submission")
    score.add_argument("submission", type=Path)
    score.add_argument("solutions", type=Path)
    score.add_argument("--output", type=Path, help="Optional full per-task report")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            # Author-created illustration, independent of the benchmark dataset.
            task = {"train": [
                {"input": [[1, 2, 3], [4, 5, 6]], "output": [[4, 1], [5, 2], [6, 3]]},
                {"input": [[7, 0], [8, 9]], "output": [[8, 7], [9, 0]]}],
                "test": [{"input": [[2, 0, 1], [0, 3, 0]]}]}
            result = solve_task(task)
            print(json.dumps(result, indent=2))
        elif args.command == "score":
            result = score_submission(_read(args.submission), _read(args.solutions))
            if args.output:
                if args.output.resolve() in (args.submission.resolve(), args.solutions.resolve()):
                    raise ValueError("Report must not overwrite input files")
                _write(args.output, result)
            print(json.dumps({k: v for k, v in result.items() if k != "per_task"}, indent=2))
        else:
            destinations = [args.output] + ([args.report] if args.report else [])
            resolved = [p.resolve() for p in destinations]
            if args.challenges.resolve() in resolved or len(set(resolved)) != len(resolved):
                raise ValueError("Challenge, submission, and report paths must be distinct")
            challenges = _read(args.challenges)
            if not isinstance(challenges, dict) or not challenges:
                raise ValueError("Challenges must be a non-empty object keyed by task ID")
            config = SearchConfig(args.beam_width, args.max_depth,
                                  args.max_generated, args.max_sideways)
            submission, details = {}, {}
            started = time.perf_counter()
            keys = sorted(challenges)[:args.limit]
            for i, key in enumerate(keys, 1):
                task_started = time.perf_counter()
                result = solve_task(challenges[key], config)
                submission[key] = result.pop("attempts")
                result["seconds"] = time.perf_counter() - task_started
                details[key] = result
                print(f"[{i}/{len(keys)}] {key}: {result['consistent_programs']} consistent programs",
                      file=sys.stderr)
            report = {"config": vars(config), "task_count": len(keys),
                      "seconds": time.perf_counter() - started, "tasks": details}
            _write(args.output, submission)
            if args.report:
                _write(args.report, report)
            print(f"Wrote {len(submission)} tasks to {args.output}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
