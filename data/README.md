# Public ARC-AGI-1 data

These four JSON bundles came from the 2024 course starter, which used ARC Prize's aggregated format. The tasks were checked against [fchollet/ARC-AGI](https://github.com/fchollet/ARC-AGI/tree/399030444e0ab0cc8b4e199870fb20b863846f34), commit `399030444e0ab0cc8b4e199870fb20b863846f34`, during repository maintenance.

Every training demonstration, test input, and test solution matches its upstream task. Only the packaging differs: the source stores one task per file with labeled test outputs; these bundles separate challenge inputs from solutions.

| Files | Tasks | Use |
| --- | --- | --- |
| `arc-agi_training_{challenges,solutions}.json` | 400 | Development and smoke checks |
| `arc-agi_evaluation_{challenges,solutions}.json` | 400 | Public evaluation; 419 test grids |

Each challenge task has `train` input/output demonstrations and `test` inputs. A solutions entry contains the corresponding test outputs in order. The solver never loads solution files; only the scorer does.

The dataset is distributed under the included [Apache License 2.0](LICENSE), copied from the same upstream commit. Attribution: François Chollet, *Abstraction and Reasoning Corpus*. This license applies to the dataset; it does not grant a blanket license to the course manuscript or other repository material.

The local school starter's `arc-agi_test_challenges.json` is byte-identical to the evaluation challenges. It and the unrelated 100-task sample submission are omitted from the published data to avoid a misleading extra split.
