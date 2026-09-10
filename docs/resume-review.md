# Resume assessment

**Yes: include this as an academic AI project.** Ranking **3rd out of 91 students (top 3.3%)** in a graduate Knowledge-Based AI course is a strong result. The project also demonstrates symbolic reasoning, search design, and experimental analysis. Give it one entry with two bullets; prioritize recent production work if resume space is limited.

**ARC-AGI Symbolic Reasoning Agent | Python, Knowledge-Based AI | 2024**

- Built a symbolic ARC-AGI solver using structured grid representations, production rules, and search-based planning; ranked **3rd out of 91 students** in a graduate Knowledge-Based AI course.
- Compared breadth-first, heuristic best-first, and local beam search; constrained exploration and reused discovered transformation sequences to predict outputs from a few demonstrations.

For a research-oriented application, an alternative second bullet is:

> Evaluated the solver on 400 public ARC-AGI tasks, achieving 7.5/400 task-normalized points with two attempts per test grid; analyzed search tradeoffs and limits of hand-authored rules.

The [rescored historical metrics](../archive/2024/metrics.json) support that score: **1.875% task-normalized performance, seven fully solved tasks, and nine correct test grids out of 419**. The course rank is the stronger resume headline; the repository provides the full benchmark result.

## Fit by role

| Target | What this project demonstrates |
| --- | --- |
| AI/ML engineering | Symbolic representations, search, evaluation, and failure analysis |
| Research or graduate applications | An academic experiment with a manuscript and explicit limitations |
| General software engineering | Python design and bounded computation, plus validation and tests added during maintenance |

## Interview explanation

“I represented ARC grids as structured states and encoded transformations such as rotation, cropping, recoloring, and flood fill as rules. Search assembled these into action sequences, and I reused common sequences from a task's demonstrations to generate two predictions. I ranked third out of 91 students. The low absolute benchmark score taught me that efficient search still depends on a sufficient rule vocabulary and consistent hypotheses.”

Describe the result as a **2024 course leaderboard placement** and the PDF as a **course manuscript**. The frames terminology refers to class-based state representation; the case-based reasoning analogy refers to sequence reuse within a task. The implementation has no persistent case library or separate script engine.

Use qualitative runtime language: archived timing figures conflict. The notebook records 206 seconds for 400 tasks, while the manuscript lists 1.96 seconds per task for local beam search. Matched benchmark runs would be needed for a reliable speedup comparison.

The **2026 maintenance work** adds a separate engineering story: preserving the original artifacts, correcting transformations and search behavior, validating candidate programs against every demonstration, and separating failed search from identity. See the [project review](project-review.md).

**Next action (two minutes):** copy the suggested two-bullet entry into the resume.
