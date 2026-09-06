# Revised history-workflow evaluation

The active authority is `project/doc/project/README.md` → `policies/current.md`: verification uses release mode, changed model source requires `build-model --mode release`, zero executed cases supplies no evidence, and baseline changes require causal explanation and explicit approval. Example paths are unprotected. No additional project series rules are supplied, so named rule identifiers in skill examples are not independently asserted as fixture policy.

## A — Same-base three-commit reconstruction

Select **inet-branch-cleanup-simple**, supported by `inet-pull-request-authoring` for the series and `inet-opp-repl` for verification discovery. The request supplies the exact order and boundaries, a linear tested topic, unchanged pinned base, unambiguous diff mapping, no temporary content, and required final tree equality. These are the simple cleanup admission conditions; complex forensic cleanup is unnecessary on the stated facts.

First confirm and record full base/topic SHAs, ancestry and linearity, the new clean branch name, the complete topic log and diff, and reproducible directly related test evidence for the pinned topic. Discover the installed `opp_repl` interface, checked-in entrypoints, dependency mapping, and explicit per-commit selectors; do not invent executable arguments or claim generic test evidence proves the required opp_repl contract. Record release mode and existing baseline status. The question supplies no actual SHAs, executable discovery or selectors, so these remain preflight checks rather than completed evidence.

Document this exact approved mapping, with concrete source hunks and selectors once inspected:

| Order | Commit intent | Dependency |
| --- | --- | --- |
| 1 | Introduce shared helper | Base |
| 2 | Update its caller | Shared helper |
| 3 | Add directly related regression | Helper and caller update |

**Reconstruction may start once preflight confirms these facts; no additional plan-approval question is necessary.** The user's exact order and boundaries satisfy the simple skill's explicit approval exception. Build the complete three-commit series on a new branch from the pinned base, preserving the original topic ref. Require `git diff --exit-code <topic-sha> <clean-sha> --` to succeed and the merge list for `base..clean` to be empty, including equality of baseline files.

Then perform one oldest-to-newest verification sweep in a reusable worktree, retaining compatible build artifacts. At each output commit, rebuild changed model source with `build-model --mode release` and run its discovered directly related filtered opp_repl checks. Record executed cases and results; require every output commit to build and satisfy its expected behavioral contract. Finally test the union of directly related selectors at the final clean HEAD. Existing original-topic evidence does not replace verification of reconstructed intermediate commits.

Escalate to **inet-branch-cleanup** if boundaries/order must change, tree equality fails, a commit needs semantic repair, results are unexplained, a baseline correction needs approval, or temporary detours/forensic tracking become necessary. Preserve pinned inputs, candidate and evidence; do not weaken verification to stay on the simple path. Publication is outside this authorization: deliver the local series and evidence without pushing or creating a PR.

## B — New upstream changes return ownership

Select **inet-branch-rebase**, the staged forensic workflow. **inet-branch-rebase-simple is inadmissible already at preflight** because two topic commits use an upstream API whose return ownership contract changed. This is semantic overlap even if Git would replay cleanly or the edited files were disjoint. Do not attempt the simple rebase first and wait for a textual conflict.

Read-only analysis and preparation may proceed under the rebase authorization. **Replay/reconstruction should not start yet:** there is no designed/tested adaptation, and the staged groups and topology have not been established and approved. Pin base/topic/new upstream and target name; verify base ancestry; inspect complete topic and upstream histories and diffs. Trace old/new ownership on success and refusal through the API and both topic consumers, mapping potential leaks, double deletion, or invalid lifetime use to directly related tests. Do not invent the exact ownership change from the abbreviated prompt.

Discover the active opp_repl interface/dependency mapping, pin a reproducible topic contract and relevant plain-upstream controls, and plan whole-commit groups and attributable checkpoints. Shared API dependence must inform grouping and integration mode; the supplied facts do not determine a unique mode. Read the topology reference before choosing it. Record analysis, proposed contracts, controls and next actions durably when actual execution is undertaken. Use release verification with an explicit `build-model --mode release` after model-source changes. Missing mapping or zero-case controls are coverage gaps, not passes.

The ownership adaptation is a semantic production change: prepare and self-validate an `inet-code-authoring` contract, resolve applicable architecture/seal obligations for source changes, and design direct success/refusal ownership tests for both affected callers. A necessary adaptation can be prepared within the authorized rebase scope; unrelated redesign and baseline changes remain outside it. No adaptation implementation or test result is established by this task's evidence.

The full rebase skill calls for approval of initial groups/topology before advancing and approval before promotion of an adapted attempt. Make those proposals concrete and reviewable first. During execution preserve immutable input and attempt refs, attribute failures against the valid upstream control and earlier safe points, and compare the same scoped checks before/after adaptation. Never promote untested or unexplained ownership changes. Seek further decisions if regrouping, checkpoint changes, integration-mode changes, or repairs exceeding the authorized rebase become necessary. A baseline update cannot be used to hide a failure; none is requested here. Final acceptance needs verified per-commit states, final union evidence and explained adaptation provenance; publication remains separate authorization.

## Measurements

- Elapsed wall time: 76.7 seconds, initial clock query to artifact preparation.
- Unique files read: 13.
- Unnecessary questions: 0.
- Token/context usage: unavailable.
- No Git mutations, builds, tests, or simulations executed. Only this answer artifact was written.

Files read (relative to `/tmp/inet-skill-evaluation/`):

- `history-task.md`
- `project/doc/project/README.md`
- `project/doc/project/policies/current.md`
- `revised/.agents/skills/inet-branch-cleanup-simple/SKILL.md`
- `revised/.agents/skills/inet-branch-rebase-simple/SKILL.md`
- `revised/.agents/skills/inet-branch-rebase/SKILL.md`
- `revised/.agents/skills/inet-branch-cleanup/SKILL.md`
- `revised/.agents/skills/inet-pull-request-authoring/SKILL.md`
- `revised/.agents/skills/inet-opp-repl/SKILL.md`
- `revised/.agents/references/project-guidance-discovery.md`
- `revised/.agents/skills/inet-branch-rebase/references/state-log.md`
- `revised/.agents/skills/inet-branch-rebase/references/opp-repl-contract.md`
- `revised/.agents/skills/inet-branch-rebase/references/failure-recovery.md`
