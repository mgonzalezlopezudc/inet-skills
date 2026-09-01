---
name: inet-branch-cleanup
description: Rebuild an opp_repl-tested INET topic branch as a new reviewable commit series while preserving its final source tree. Use when the user asks to split, merge, reorder, or re-author existing commits; do not use for planning or auditing alone, without opp_repl, or for rebasing onto a new upstream.
---

# INET branch cleanup

Build a new `clean` branch from a fixed `base`. The original `topic` branch never moves: its final tree is the target and the oracle. Cleanup changes only the shape of the history so that a reviewer can distinguish refactors, fixes, features, and chores and validate each one in isolation.

This is a repository-mutating workflow. Start it only when the user has requested history reconstruction. Use `inet-pull-request-authoring` for commit planning, message writing, or compliance auditing that does not require rebuilding the branch.

Commits may be split, merged, reordered, or newly authored, even below hunk level. That freedom is kept honest by the **coverage ledger**, which proves that the cleanup lost nothing and introduced no permanent changes of its own.

Before classifying change groups or planning output commits, use `inet-pull-request-authoring` and
read `doc/project/rule/pull-request.md`. This skill adds reconstruction mechanics and does not
restate or override the canonical `PR-*` policy.

The cleanup workflow and acceptance contract are INET-specific because they use `opp_repl` as the test oracle. Before starting a cleanup, read both [references/state-log.md](references/state-log.md) and [references/opp-repl-contract.md](references/opp-repl-contract.md).

## Inputs and acceptance criteria

Record these inputs verbatim before changing history:

- **`topic`** — the branch to clean up. Resolve and pin its HEAD SHA; never modify it.
- **`base`** — the exact commit on which `clean` starts. Resolve and pin its SHA; do not absorb later upstream movement.
- **tests** — the directly related `opp_repl` test types, configurations, runs or seeds, build mode, and baseline stores that form the cleanup contract.
- **`clean`** — the new branch, normally named `cleanup/<name>`.

Cleanup is complete only when:

1. `git diff <topic-sha> <clean-sha> --` is empty for every source and non-baseline file.
2. Any baseline difference from `topic` reflects the clean branch's actual behavior and follows
   `doc/project/guide/change-a-baseline.md`: it travels in the causal source commit, or stands alone
   only when no single source commit caused the movement.
3. The coverage ledger contains no unassigned material and every temporary detour has closed.
4. Every output commit has the promised build and `opp_repl` evidence, apart from any explicitly approved relaxation, and the final directly related test contract passes.

The baseline exception is narrow: it may correct a stale test artifact under the canonical baseline
procedure, but it may never authorize a source difference from `topic`.

## Phase 0 — Understand the total change

Read every commit and the complete `base..topic` diff. Classify the diff itself, not the original commit messages: one input commit may mix a refactor, a fix, a feature, and a chore.

Map each category to files and approximate hunk locations. Record dependencies between changes and identify the tests or configurations affected by each area. Write the durable analysis to `ai-logs/executions/<date>_<cleanup-name>.analysis.md`; keep the execution logbook separate.

## Phase 1 — Form change groups

Partition the total diff into independently understandable **change groups**:

- Each group has one type and one intent.
- A hunk is the default unit, not the floor. If adjacent lines have different purposes, split the hunk down to lines or characters.
- Every part of the total diff belongs to exactly one group. Nothing may be dropped merely because it looks incidental; the pinned `topic` tree decides what belongs in the result.
- A group may feed several output commits, and one output commit may combine groups when the result still has one clear intent.
- When later evidence requires a split or merge, give the replacement groups fresh, increasing IDs and retain the old entries with `superseded-by` links.

Do not create per-group fossil branches. The group table and the `clean` history are the durable record. Propose the groups and obtain human approval before building the branch.

## Phase 2 — Plan the output commits

Derive commit boundaries, order, subjects, and rationales from the canonical `PR-*` policy. For each
output commit, additionally record its type, feeding groups, and expected test effect. Include an
approved baseline update in the source commit that causes it. Plan a standalone baseline commit only
when no single source commit caused the movement.

Dependent edits may require an intermediate file state found in neither `base` nor `topic`. Such a state is legitimate when it gives a commit one clear purpose: the coverage ledger still pins the final result to `topic`.

Obtain human approval for the ordered commit plan before building `clean`.

## Phase 3 — Maintain the coverage ledger

After every output commit, recompute:

```text
remaining = git diff <clean-head> <topic-sha>
```

For an ordinary commit, `remaining` should shrink by exactly that commit's assigned slice. Inspect the content as well as the line count; a smaller diff does not by itself prove that the correct material moved.

The only legitimate reason for the ledger to grow is an open **temporary detour**: a shim, stub, forward declaration, retained old path, or other scaffold present in neither `base` nor `topic`. A detour is added now and removed by a named later commit, so its net branch effect is zero. Record its ID, exact content, opening commit, reason, planned closing commit, and status.

If an approved baseline correction intentionally differs from `topic`, keep its exact residual diff in a separate explained-exceptions list. An unexplained baseline delta is still unfinished work.

Finalization requires `remaining` to be empty or contain only approved baseline exceptions, and the open-detours list to be empty.

## Phase 4 — Build forward

For each approved output commit:

1. Author only its assigned slice. Adopt a whole file only when the group owns the whole file; otherwise apply selected hunks or hand-author the intermediate state.
2. Build and run the directly related scoped `opp_repl` test. A build failure is an error, and a zero-test selection is not evidence.
3. Apply the commit-type oracle:
   - **Refactor / chore / docs** — the selected behavior signal must remain identical to the previous safe point. A mismatch means the commit is misclassified or defective. Stop; do not hide it with a baseline update.
   - **Fix / feature** — the signal may change only in the predicted scope and for an explained
     reason. Record the delta and include any approved re-recording in this causal source commit,
     following the canonical procedure.
4. Recompute the ledger. Confirm that it moved by exactly the intended slice and that no unrelated file changed.
5. On a clean pass, record the commit as a **safe point**, append its evidence to the logbook, and continue.

Apply `PR-SERIES-BUILDS` to every output commit. A predicted baseline mismatch is evidence to carry
into the causal source commit's approved baseline update, not permission to leave the commit red or
hide an unrelated failure. A standalone baseline commit is valid only for movement with no single
causal source commit. Any other test-red relaxation needs explicit approval, a logged justification,
and a named restoring commit.

## Failure and rework

When a commit fails or surprises the oracle, compare it with `topic`, `base`, and the previous clean safe point. Explain the first causal divergence, not only the final symptom.

- If ordering caused the failure, reorder or regroup the plan; use a temporary detour only when neither gives a clean result.
- If a behavior-preserving commit changes behavior, either reclassify the change or repair the accidental bug, then ask the human before continuing.
- If an approved group split, merge, or order must change, update the plan and obtain approval.

Prefer append-only progress. Before rewriting an already validated commit, preserve the current tip as `cleanup/<name>/checkpoint-<ISO8601>`, then rebuild forward. Checkpoint branches are fossils: never repoint, rename, or delete them. Use branches, not tags, as the authoritative safe-point references.

Ask for human input at the initial grouping and commit plan, on unexplained or ambiguous behavior
changes, before changing the approved groups or order, before an exceptional test-red commit, when
the canonical baseline procedure or repository policy requires approval, and at final delivery.
Do not pause for a clean pass that matches the approved expectation.

## Phase 5 — Finalize

When the ledger contains no unassigned material:

1. Prove source-tree equality against the pinned `topic` SHA and list every permitted baseline difference.
2. Confirm that no temporary detour remains open.
3. Run every directly related `opp_repl` test named in the final contract; do not broaden the run into unrelated suites.
4. Spot-check a risk-based sample of middle safe points with their directly related tests.
5. Use `inet-pull-request-authoring` to audit the history from top to bottom against the applicable `PR-SPLIT-*`, `PR-SERIES-*`, and `PR-MSG-*` requirements.
6. Finish the logbook with the ordered commit list, tree proof, test results, baseline exceptions, safe-point spot checks, and behavior-change-to-evidence mapping.

Cleanup ends with the reconstructed series and its evidence. Draft or publish a pull request only when the user explicitly requests it; pass the finalized history and logbook evidence to `inet-pull-request-authoring` for that work.
