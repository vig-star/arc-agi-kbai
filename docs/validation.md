# Maintenance validation

The 2026 maintained implementation is a correctness-focused revision of the 2024 approach. It is not a behavior-preserving extraction or a demonstrated accuracy improvement.

| Check | Result |
| --- | --- |
| Unit and CLI integration tests | 30 pass on Python 3.9.6 and 3.12.14 |
| Clean virtual-environment installation | Package installs; `arc-kbai demo` infers and replays `rotate(90)` |
| Original transformations | 854 valid outputs matched in a parity check, excluding the intentional mirror correction; one empty output was rejected |
| Archived submission rescoring | 7.5/400 points, seven complete tasks, nine correct test grids out of 419 |
| Public dataset provenance | All 800 tasks and solutions matched the pinned upstream ARC-AGI commit |

The first five training tasks, selected by sorted task ID, completed with the default search limits and valid fallback grids. None produced a program consistent with every demonstration. This checks the fallback path; it does not establish solver accuracy.

A separate diagnostic selected **all eight public evaluation tasks with a nonzero archived score**. The maintained implementation used its default settings and fully solved five of them:

| Task | Archived task score | Maintained task score |
| --- | --- | --- |
| `00576224` | 1 | 1 |
| `60c09cac` | 1 | 1 |
| `68b67ca3` | 1 | 1 |
| `6ea4a07e` | 0.5 | 0 |
| `73182012` | 1 | 1 |
| `8597cfd7` | 1 | 0 |
| `bbb1b8b6` | 1 | 0 |
| `be03b35f` | 1 | 1 |

This deliberately selected subset cannot estimate full-benchmark performance. Exact-goal search, all-demonstration validation, corrected transformations, and explicit budgets change the candidate programs. The three losses have not been individually attributed to one change. The maintained solver has **not** been evaluated across the full 400-task split; the README includes the command to run that experiment.

The saved notebook, predictions, manuscript, and poster match their local originals byte-for-byte. The personal reflection, authoring templates, duplicate “test” split, and generated outputs are excluded from the Git repository.
