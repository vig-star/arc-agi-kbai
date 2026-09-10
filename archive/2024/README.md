# Preserved 2024 course submission

`submission.ipynb` and `submission.json` are byte-for-byte copies of the final school artifacts. `metrics.json` records the score independently recovered from the saved predictions and the runtime stored in the notebook output.

The notebook is retained for provenance and code review. It includes the original school starter cells, relative data paths, optional `py_search`/`tqdm` imports, and known implementation defects. It has not been rerun during maintenance; its original execution environment was not locked. Use the maintained CLI in the [root README](../../README.md) for a supported run.

The archived score is 7.5/400 task-normalized points: seven fully solved tasks and one half-solved task. One archived prediction has an empty grid and is counted as incorrect. The original notebook's “test” dataset was identical to the public evaluation dataset.

Re-score the saved file from the repository root:

```bash
python3 -m arc_agi_kbai score archive/2024/submission.json data/arc-agi_evaluation_solutions.json
```

The original notebook and original predictions remain separate from the corrected 2026 implementation. Rerunning the maintained solver is not expected to recreate the historical prediction file.
