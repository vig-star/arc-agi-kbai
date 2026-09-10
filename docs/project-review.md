# Project review

**This is a credible symbolic AI project that ranked 3rd out of 91 students (top 3.3%) in a 2024 graduate KBAI course.** Its contribution is translating knowledge-based AI concepts into executable transformations, comparing search strategies, and analyzing their limits. The repository preserves the 2024 submission separately from the maintained 2026 implementation.

## What the original project implements

| Concept | Implementation | Scope |
| --- | --- | --- |
| Frames | `ARCPuzzle` encapsulates a grid; `ARCPuzzleProblem` defines the search problem | Class-based state representation |
| Production rules | Hand-authored rotation, reflection, recoloring, cropping, scaling, flood-fill, and other operations | Primarily raw-grid transformations with fixed parameters |
| Planning and search | Search composes rules into action sequences; the final notebook uses local beam search | The manuscript describes additional BFS and best-first experiments |
| Scripts and case reuse | The two most frequent sequences from a task's demonstrations become test predictions | Per-task sequence reuse; no separate script engine or persistent case library |

The [manuscript](manuscript.pdf), sections 3-5, explains the intended design. The [archived notebook](../archive/2024/submission.ipynb), code cells 14-15, establishes the implemented behavior. “Case-based reasoning” is an analogy to reusing demonstrated solutions, rather than a full retrieval-and-adaptation system.

## Historical results

| Item | Result | Evidence |
| --- | --- | --- |
| Course placement | 3rd out of 91 students | Author-confirmed 2024 course result |
| Task-normalized score | 7.5/400 points, or 1.875% | Saved predictions rescored against public evaluation solutions |
| Exact outputs | Seven fully solved tasks; nine correct test grids out of 419 | Two attempts allowed per test grid |
| Stored runtime | 206 seconds for 400 tasks, approximately 0.515 seconds per task | Archived notebook progress-bar output |

The [metrics record](../archive/2024/metrics.json) includes the prediction artifact's checksum. Scoring takes the fraction of correct test grids within each task and sums it across 400 tasks; either attempt can match. Thus, 7.5 points does not mean 7.5% or 7.5 fully solved tasks.

Rescoring verifies saved outputs; it does not rerun the original solver. The public evaluation split was used during course development. The maintained package is a separate implementation whose benchmark performance must be measured separately.

Historical runtime comparisons are inconsistent: the manuscript reports both 1.96 seconds per task and approximately 3.4 minutes for 400 tasks. It also gives conflicting BFS/best-first scores in its table and prose. These archived figures do not support a reliable numeric speedup claim.

## Correctness findings and 2026 maintenance

1. **Mirrors:** the original `hmirror` and `vmirror` both reverse row order. The maintained implementation provides distinct row-order and column-order reflections.
2. **Search success:** the original planner accepts the first `py_search.local_beam_search` result, which can be a local minimum rather than the goal. It also represents failure and identity with the same empty sequence. The maintained planner checks the goal and distinguishes those outcomes.
3. **Deduplication:** the original heuristic stores `Node` objects while successor generation checks `ARCPuzzle` objects, defeating the intended visited-state check. The maintained search tracks states locally.
4. **Hypothesis validation:** the original code votes on independently discovered sequences without checking their consistency across demonstrations. The maintained solver requires each candidate program to reproduce every demonstration.
5. **Bounds:** original operations can produce empty or oversized grids, and crop/fill enumeration can generate many successors. The maintained package validates grids and explicitly bounds search depth and generated actions.

These changes improve correctness and reproducibility while preserving the original notebook and predictions as historical artifacts.

## Portfolio value and research limit

The project supports substantive discussion of representations, combinatorial search, heuristics, and the difference between fitting an example and inferring a transferable rule. The [resume assessment](resume-review.md) provides concise wording.

Its main research limit is generalization: search cannot express transformations missing from the hand-authored rule vocabulary. A useful next experiment would add connected-component reasoning and compare it with the baseline under identical search budgets on a preselected split.
