# 2024 course submission

`submission.ipynb` contains the final course notebook, and `submission.json` contains its saved predictions. `metrics.json` records the evaluation score and runtime stored in the notebook output.

The notebook uses the original school starter's relative data paths and imports `py_search` and `tqdm`. For current setup and execution instructions, see the [root README](../../README.md).

The archived score is 7.5/400 task-normalized points: seven fully solved tasks and one half-solved task. One archived prediction has an empty grid and is counted as incorrect. The original notebook's “test” dataset was identical to the public evaluation dataset.

Re-score the saved file from the repository root:

```bash
python3 -m arc_agi_kbai score archive/2024/submission.json data/arc-agi_evaluation_solutions.json
```

The current Python package uses different search constraints and validation, so its predictions can differ from this submission.
